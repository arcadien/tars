/*
 * TARS - bench test on a Wemos D1 mini (ESP8266): 1.3" ST7789 screen, INMP441 microphone,
 * MAX98357A amplifier + speaker.
 *
 *   - screen: test patterns + a photo (bench_assets/image.h), auto-cycling, full-fill timing;
 *   - "record and replay": records from the INMP441 (as long as free RAM allows, ~2.5 s),
 *     normalises, plays it back on the speaker;
 *   - a short MP3 from flash (src/sound.h, ESP8266Audio).
 * Assets: uv run ../../bench_assets/make_assets.py (see its header for your own photo / MP3).
 *
 * Everything is 3.3 V: no level shifting. The I2S pins of the ESP8266 are fixed, so the
 * screen runs on a bit-banged SPI on the remaining pins.
 *
 *     Module         pin     D1 mini
 *     ------         ---     -------
 *     ST7789 screen  GND     G
 *                    VCC     3V3
 *                    SCL     D1  (GPIO5)
 *                    SDA     D2  (GPIO4)
 *                    RES     RST (reset together with the D1 mini)
 *                    DC      D3  (GPIO0: high at boot, the screen input does not pull it)
 *                    CS      D0  (GPIO16)
 *                    BLK     not connected (backlight on)
 *     INMP441 mic    VDD     3V3
 *                    GND     G
 *                    L/R     G   (left channel)
 *                    SD      D6  (GPIO12, I2S in data)
 *                    SCK     D7  (GPIO13, I2S in clock)
 *                    WS      D5  (GPIO14, I2S in frame)
 *     MAX98357A amp  VIN     5V  (USB)
 *                    GND     G
 *                    BCLK    D8  (GPIO15)
 *                    LRC     D4  (GPIO2, the blue LED flickers while it plays)
 *                    DIN     RX  (GPIO3)
 *                    SD, GAIN not connected (on, 9 dB)
 *     Speaker on the amp's + / - (4-8 ohm).
 *
 * RX (GPIO3) is both the USB serial input and the I2S data out: commands are read
 * between two sounds only (the serial port is restarted after each one); what is typed
 * during a sound is lost. The serial output works all the time.
 *
 * Serial commands (115200 baud, one letter):
 *   screen: n / b next / previous pattern, a auto-cycle on / off, i inversion,
 *           c RGB / BGR, s speed test
 *   sound : r record then replay, e replay again, m play the MP3, v volume,
 *           l microphone channel (left / right, if the recording is silent)
 *   ?     : help
 */

#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <core_esp8266_i2s.h>
#include <AudioFileSourcePROGMEM.h>
#include <AudioGeneratorMP3.h>
#include <AudioOutputI2S.h>
#include "image.h"
#include "sound.h"

// ---- pins and settings -------------------------------------------------------

static const uint8_t PIN_SCK = 5;        // D1
static const uint8_t PIN_MOSI = 4;       // D2
static const uint8_t PIN_DC = 0;         // D3
static const uint8_t PIN_CS = 16;        // D0
static const uint16_t W = 240;
static const uint16_t H = 240;
static const uint32_t AUTO_MS = 4000;

static const uint32_t MIC_RATE = 16000;  // I2S clock 32 x 16 kHz = 512 kHz (INMP441 min ~0.5 MHz)
static const uint32_t STORE_RATE = 8000; // pairs of mic samples averaged: 2 bytes per stored sample
static const uint32_t KEEP_FREE = 8192;  // heap left to the rest while recording
static const float VOLUMES[] = {0.25f, 0.5f, 1.0f};

static const uint16_t BLACK = 0x0000, WHITE = 0xFFFF, RED = 0xF800, GREEN = 0x07E0,
                      BLUE = 0x001F, CYAN = 0x07FF, MAGENTA = 0xF81F, YELLOW = 0xFFE0,
                      GREY = 0x8410;

static bool inverted = true;             // IPS ST7789 panels need INVON for true colours
static bool bgr = false;
static bool auto_cycle = true;
static bool mic_right = false;           // L/R tied to GND -> left
static uint8_t volume_step = 1;
static int16_t *recording = nullptr;
static uint32_t recording_len = 0;

// ---- bit-banged SPI (mode 0, MSB first) --------------------------------------

#define SCK_HIGH() (GPOS = 1 << PIN_SCK)
#define SCK_LOW() (GPOC = 1 << PIN_SCK)

static inline void IRAM_ATTR spi_byte(uint8_t b) {
  for (uint8_t m = 0x80; m; m >>= 1) {
    if (b & m) GPOS = 1 << PIN_MOSI; else GPOC = 1 << PIN_MOSI;
    asm volatile("nop; nop;");           // a few ns of setup: long Dupont wires
    SCK_HIGH();
    asm volatile("nop; nop;");
    SCK_LOW();
  }
}

static inline void spi16(uint16_t v) {
  spi_byte(v >> 8);
  spi_byte(v);
}

// ---- minimal ST7789 driver ---------------------------------------------------

static void command(uint8_t c) {
  GPOC = 1 << PIN_DC;
  digitalWrite(PIN_CS, LOW);
  spi_byte(c);
  GPOS = 1 << PIN_DC;                    // following bytes are parameters
}

static void end_write() {
  digitalWrite(PIN_CS, HIGH);
}

static void command1(uint8_t c, uint8_t value) {
  command(c);
  spi_byte(value);
  end_write();
}

// Opens a window and leaves CS low: push its pixels, then end_write().
static void begin_pixels(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1) {
  command(0x2A);                         // CASET
  spi16(x0);
  spi16(x1);
  command(0x2B);                         // RASET
  spi16(y0);
  spi16(y1);
  command(0x2C);                         // RAMWR
}

static void fill_rect(int16_t x, int16_t y, int16_t w, int16_t h, uint16_t color) {
  if (x < 0) { w += x; x = 0; }
  if (y < 0) { h += y; y = 0; }
  if (x + w > W) w = W - x;
  if (y + h > H) h = H - y;
  if (w <= 0 || h <= 0) return;
  begin_pixels(x, y, x + w - 1, y + h - 1);
  for (int16_t row = 0; row < h; row++) {
    for (int16_t n = 0; n < w; n++) spi16(color);
    if ((row & 31) == 31) yield();       // keep the watchdog fed on big fills
  }
  end_write();
}

static void pixel(int16_t x, int16_t y, uint16_t color) {
  if (x < 0 || y < 0 || x >= W || y >= H) return;
  begin_pixels(x, y, x, y);
  spi16(color);
  end_write();
}

static void fill(uint16_t color) { fill_rect(0, 0, W, H, color); }

static void apply_madctl() {
  command1(0x36, bgr ? 0x08 : 0x00);     // MADCTL: rotation 0 (no RAM offset on 240x240)
}

static void apply_inversion() {
  command(inverted ? 0x21 : 0x20);       // INVON / INVOFF
  end_write();
}

static void lcd_init() {
  // RES is tied to the D1 mini RST: the screen was reset with the board.
  command(0x01); end_write(); delay(150); // SWRESET
  command(0x11); end_write(); delay(120); // SLPOUT
  command1(0x3A, 0x55);                   // COLMOD: 16 bits per pixel
  apply_madctl();
  apply_inversion();
  command(0x13); end_write(); delay(10);  // NORON
  command(0x29); end_write(); delay(10);  // DISPON
}

// ---- drawing helpers ---------------------------------------------------------

static void line(int16_t x0, int16_t y0, int16_t x1, int16_t y1, uint16_t color) {
  int16_t dx = abs(x1 - x0), sx = x0 < x1 ? 1 : -1;
  int16_t dy = -abs(y1 - y0), sy = y0 < y1 ? 1 : -1;
  int16_t err = dx + dy;
  for (;;) {
    pixel(x0, y0, color);
    if (x0 == x1 && y0 == y1) break;
    int16_t e2 = 2 * err;
    if (e2 >= dy) { err += dy; x0 += sx; }
    if (e2 <= dx) { err += dx; y0 += sy; }
  }
}

static void circle(int16_t cx, int16_t cy, int16_t r, uint16_t color) {
  int16_t x = r, y = 0, err = 1 - r;
  while (x >= y) {
    pixel(cx + x, cy + y, color); pixel(cx - x, cy + y, color);
    pixel(cx + x, cy - y, color); pixel(cx - x, cy - y, color);
    pixel(cx + y, cy + x, color); pixel(cx - y, cy + x, color);
    pixel(cx + y, cy - x, color); pixel(cx - y, cy - x, color);
    y++;
    if (err < 0) err += 2 * y + 1;
    else { x--; err += 2 * (y - x) + 1; }
  }
}

static uint16_t rgb(uint8_t r, uint8_t g, uint8_t b) {
  return (r & 0xF8) << 8 | (g & 0xFC) << 3 | b >> 3;
}

// ---- patterns ----------------------------------------------------------------

static void pattern_solid() {
  static const uint16_t colors[] = {RED, GREEN, BLUE, WHITE, BLACK};
  for (uint8_t i = 0; i < 5; i++) fill_rect(0, i * 48, W, 48, colors[i]);
  Serial.println(F("# bands top to bottom: red, green, blue, white, black"));
}

static void pattern_bars() {
  static const uint16_t bars[] = {WHITE, YELLOW, CYAN, GREEN, MAGENTA, RED, BLUE, BLACK};
  for (uint8_t i = 0; i < 8; i++) fill_rect(i * 30, 0, 30, 120, bars[i]);
  for (uint8_t band = 0; band < 4; band++) {   // ramps 0 -> full: grey, red, green, blue
    begin_pixels(0, 120 + band * 30, W - 1, 120 + band * 30 + 29);
    for (uint8_t y = 0; y < 30; y++) {
      for (uint16_t x = 0; x < W; x++) {
        uint8_t v = x * 255 / (W - 1);
        spi16(band == 0 ? rgb(v, v, v) : band == 1 ? rgb(v, 0, 0)
              : band == 2 ? rgb(0, v, 0) : rgb(0, 0, v));
      }
    }
    end_write();
    yield();
  }
  Serial.println(F("# bars: white yellow cyan green magenta red blue black; ramps grey/red/green/blue"));
}

static void pattern_frame() {
  fill(BLACK);
  for (uint16_t v = 20; v < W; v += 20) {
    fill_rect(v, 0, 1, H, GREY);
    fill_rect(0, v, W, 1, GREY);
  }
  fill_rect(0, 0, W, 1, RED);            // outermost pixels: red top, green bottom,
  fill_rect(0, H - 1, W, 1, GREEN);      // blue left, yellow right
  fill_rect(0, 0, 1, H, BLUE);
  fill_rect(W - 1, 0, 1, H, YELLOW);
  fill_rect(W / 2 - 1, H / 2 - 10, 2, 20, WHITE);
  fill_rect(W / 2 - 10, H / 2 - 1, 20, 2, WHITE);
  Serial.println(F("# edges: red top, green bottom, blue left, yellow right; grid every 20 px"));
}

static void pattern_checker(uint8_t size) {
  begin_pixels(0, 0, W - 1, H - 1);
  for (uint16_t y = 0; y < H; y++) {
    for (uint16_t x = 0; x < W; x++) spi16(((x / size) ^ (y / size)) & 1 ? WHITE : BLACK);
    if ((y & 31) == 31) yield();
  }
  end_write();
  Serial.print(F("# checkerboard "));
  Serial.print(size);
  Serial.println(F(" px (smooth grey at 1 px = no glitch)"));
}

static void pattern_shapes() {
  fill(BLACK);
  static const uint16_t colors[] = {RED, YELLOW, GREEN, CYAN, BLUE, MAGENTA};
  for (uint8_t i = 0; i < 12; i++) circle(W / 2, H / 2, 10 + i * 9, colors[i % 6]);
  for (uint16_t v = 0; v < W; v += 24) {
    line(0, v, v, H - 1, colors[(v / 24) % 6]);
    line(W - 1, H - 1 - v, W - 1 - v, 0, colors[(v / 24 + 3) % 6]);
  }
  fill_rect(W / 2 - 15, H / 2 - 15, 30, 30, WHITE);
  Serial.println(F("# circles round = square pixels; lines straight"));
}

static void pattern_photo() {
  begin_pixels(0, 0, W - 1, H - 1);
  for (uint32_t i = 0; i < sizeof(IMG_RGB565); i++) {
    spi_byte(pgm_read_byte(IMG_RGB565 + i));
    if ((i & 0x3FFF) == 0x3FFF) yield();
  }
  end_write();
  Serial.println(F("# photo 240 x 240 RGB565"));
}

static const uint8_t PATTERN_COUNT = 7;
static uint8_t pattern = 0;

static void show(uint8_t n) {
  uint32_t t0 = millis();
  Serial.print(F("PAT,"));
  Serial.print(n);
  Serial.print(',');
  switch (n) {
    case 0: Serial.println(F("solid")); pattern_solid(); break;
    case 1: Serial.println(F("bars")); pattern_bars(); break;
    case 2: Serial.println(F("frame")); pattern_frame(); break;
    case 3: Serial.println(F("checker1")); pattern_checker(1); break;
    case 4: Serial.println(F("checker8")); pattern_checker(8); break;
    case 5: Serial.println(F("shapes")); pattern_shapes(); break;
    default: Serial.println(F("photo")); pattern_photo(); break;
  }
  Serial.print(F("# drawn in "));
  Serial.print(millis() - t0);
  Serial.println(F(" ms"));
}

static void speed_test() {
  uint32_t t0 = millis();
  for (uint8_t i = 0; i < 10; i++) fill(i & 1 ? WHITE : BLACK);
  Serial.print(F("SPEED,full_fill_ms="));
  Serial.println((millis() - t0) / 10);
}

// Level bar at the top of the screen while recording / playing (peak, log scale).
static void level_bar(int16_t peak, uint16_t color) {
  uint16_t w = 0;
  if (peak > 0) w = constrain((int)(log10f(peak) * W / 4.5f), 0, W);  // 1 -> 0, 32767 -> ~W
  fill_rect(0, 0, w, 12, color);
  fill_rect(w, 0, W - w, 12, BLACK);
}

// ---- sound -------------------------------------------------------------------

static void serial_restart() {
  // I2S data out took GPIO3 (RX): give it back to the UART.
  Serial.flush();
  Serial.end();
  Serial.begin(115200);
}

static void record() {
  free(recording);
  recording = nullptr;
  uint32_t bytes = ESP.getMaxFreeBlockSize();
  if (bytes < KEEP_FREE + 4000) {
    Serial.println(F("# not enough RAM to record"));
    return;
  }
  recording_len = (bytes - KEEP_FREE) / sizeof(int16_t);
  recording = (int16_t *)malloc(recording_len * sizeof(int16_t));
  if (!recording) return;

  Serial.print(F("REC,start,seconds="));
  Serial.println((float)recording_len / STORE_RATE, 1);
  fill(BLACK);
  i2s_set_bits(16);
  if (!i2s_rxtx_begin(true, false)) {
    Serial.println(F("# I2S RX start failed"));
    free(recording);
    recording = nullptr;
    return;
  }
  i2s_set_rate(MIC_RATE);
  int16_t l, r;
  for (uint16_t i = 0; i < 1600; i++) i2s_read_sample(&l, &r, true);  // 0.1 s: mic start-up

  int32_t sum = 0;
  int16_t lo = 32767, hi = -32768, peak = 0;
  for (uint32_t n = 0; n < recording_len; n++) {
    int32_t acc = 0;
    for (uint8_t k = 0; k < MIC_RATE / STORE_RATE; k++) {
      i2s_read_sample(&l, &r, true);
      acc += mic_right ? r : l;
    }
    int16_t s = acc / (int32_t)(MIC_RATE / STORE_RATE);
    recording[n] = s;
    sum += s;
    lo = min(lo, s);
    hi = max(hi, s);
    peak = max(peak, (int16_t)abs(s));
    if ((n & 511) == 511) {              // every 64 ms: 3 ms of drawing, the DMA holds 32 ms
      level_bar(peak, RED);
      peak = 0;
    }
  }
  i2s_end();

  // remove the DC offset, then normalise to ~ -1 dBFS
  int16_t mean = sum / (int32_t)recording_len;
  int32_t max_abs = 1;
  for (uint32_t n = 0; n < recording_len; n++) {
    recording[n] -= mean;
    max_abs = max(max_abs, (int32_t)abs(recording[n]));
  }
  Serial.print(F("REC,done,min="));
  Serial.print(lo);
  Serial.print(F(",max="));
  Serial.print(hi);
  Serial.print(F(",mean="));
  Serial.print(mean);
  Serial.print(F(",gain=x"));
  Serial.println(29000 / max_abs);
  if (hi == lo || max_abs < 4) {
    Serial.println(F("# silent or constant: check SD / SCK / WS, or press l (other channel)"));
  }
  for (uint32_t n = 0; n < recording_len; n++) recording[n] = (int32_t)recording[n] * 29000 / max_abs;
}

static void replay() {
  if (!recording) {
    Serial.println(F("# nothing recorded yet (r)"));
    return;
  }
  Serial.println(F("PLAY,recording"));
  if (!i2s_rxtx_begin(false, true)) {
    Serial.println(F("# I2S TX start failed"));
    serial_restart();
    return;
  }
  i2s_set_rate(MIC_RATE);
  float vol = VOLUMES[volume_step];
  int16_t peak = 0;
  for (uint32_t n = 0; n < recording_len; n++) {
    int16_t a = recording[n] * vol;
    int16_t b = (n + 1 < recording_len ? (recording[n] + recording[n + 1]) / 2 : recording[n]) * vol;
    i2s_write_lr(a, a);                  // 8 kHz -> 16 kHz, linear interpolation
    i2s_write_lr(b, b);
    peak = max(peak, (int16_t)abs(a));
    if ((n & 511) == 511) {
      level_bar(peak, GREEN);
      peak = 0;
    }
  }
  for (uint16_t i = 0; i < 1024; i++) i2s_write_lr(0, 0);  // flush the DMA with silence
  i2s_end();
  serial_restart();
  Serial.println(F("PLAY,done"));
}

static void play_mp3() {
  Serial.print(F("PLAY,mp3,bytes="));
  Serial.println(sizeof(SOUND_MP3));
  free(recording);                       // the decoder needs ~30 KB of heap
  recording = nullptr;
  fill(BLACK);
  AudioFileSourcePROGMEM file(SOUND_MP3, sizeof(SOUND_MP3));
  AudioOutputI2S out;
  out.SetGain(VOLUMES[volume_step]);
  AudioGeneratorMP3 mp3;
  if (!mp3.begin(&file, &out)) {
    Serial.println(F("# MP3 start failed"));
  } else {
    uint32_t last = millis();
    while (mp3.isRunning()) {
      if (!mp3.loop()) mp3.stop();
      if (millis() - last > 100) {       // a progress bar (the decoder has no level to show)
        last = millis();
        fill_rect(0, 0, (uint32_t)file.getPos() * W / sizeof(SOUND_MP3), 12, CYAN);
      }
    }
  }
  serial_restart();
  Serial.println(F("PLAY,done"));
}

// ---- commands ----------------------------------------------------------------

static void print_help() {
  Serial.println(F("# screen: n/b next/prev, a auto, i inversion, c RGB/BGR, s speed"));
  Serial.println(F("# sound : r record + replay, e replay, m MP3, v volume, l mic channel, ? help"));
}

static void handle_command(char cmd) {
  switch (cmd) {
    case 'n': pattern = (pattern + 1) % PATTERN_COUNT; show(pattern); break;
    case 'b': pattern = (pattern + PATTERN_COUNT - 1) % PATTERN_COUNT; show(pattern); break;
    case 'a':
      auto_cycle = !auto_cycle;
      Serial.println(auto_cycle ? F("# auto on") : F("# auto off"));
      break;
    case 'i':
      inverted = !inverted;
      apply_inversion();
      Serial.println(inverted ? F("# INVON") : F("# INVOFF"));
      break;
    case 'c':
      bgr = !bgr;
      apply_madctl();
      show(pattern);
      Serial.println(bgr ? F("# BGR") : F("# RGB"));
      break;
    case 's': speed_test(); show(pattern); break;
    case 'r': record(); replay(); show(pattern); break;
    case 'e': replay(); show(pattern); break;
    case 'm': play_mp3(); show(pattern); break;
    case 'v':
      volume_step = (volume_step + 1) % (sizeof(VOLUMES) / sizeof(VOLUMES[0]));
      Serial.print(F("# volume "));
      Serial.println((int)(VOLUMES[volume_step] * 100));
      break;
    case 'l':
      mic_right = !mic_right;
      Serial.println(mic_right ? F("# mic channel right") : F("# mic channel left"));
      break;
    case '?':
    case 'h': print_help(); break;
    default: break;                      // ignore CR, LF and the rest
  }
}

void setup() {
  WiFi.mode(WIFI_OFF);                   // more heap for the recording, less noise
  pinMode(PIN_SCK, OUTPUT);
  pinMode(PIN_MOSI, OUTPUT);
  pinMode(PIN_DC, OUTPUT);
  pinMode(PIN_CS, OUTPUT);
  digitalWrite(PIN_CS, HIGH);
  digitalWrite(PIN_SCK, LOW);

  Serial.begin(115200);
  delay(200);
  Serial.println();
  Serial.println(F("# TARS bench test - D1 mini: ST7789 screen, INMP441 mic, MAX98357A amp"));
  print_help();
  Serial.print(F("# free heap "));
  Serial.println(ESP.getFreeHeap());

  lcd_init();
  show(pattern);
}

void loop() {
  static uint32_t last = millis();
  while (Serial.available()) {
    handle_command(Serial.read());
    last = millis();
  }
  if (auto_cycle && millis() - last >= AUTO_MS) {
    pattern = (pattern + 1) % PATTERN_COUNT;
    show(pattern);
    last = millis();
  }
}
