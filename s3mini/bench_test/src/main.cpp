/*
 * TARS - bench test on the LOLIN S3 Mini, TARS pin map (tars4_schematic.html / tools/kicad_sch_gen.py):
 * both 1.3" ST7789 screens, INMP441 microphone, MAX98357A amplifier + speaker.
 *
 *   - screens: test patterns + a photo (bench_assets/image.h) from a frame buffer in PSRAM,
 *     hardware SPI at 26.7 MHz (40 MHz with f), same or different pattern on each screen;
 *   - "record and replay": REC_SECONDS from the INMP441 (I2S1, 32-bit slots), normalised,
 *     played back on the MAX98357A (I2S0);
 *   - a short MP3 from flash (bench_assets/sound.h, ESP8266Audio).
 * Assets: uv run ../../bench_assets/make_assets.py
 *
 * Wiring on the bench (no carrier, Dupont wires; on TARS the series resistors R12 / R19 /
 * R20 / R13 / R14 / R10 sit on the carrier and P2, not needed for short wires):
 *
 *     Module           pin     S3 Mini
 *     ------           ---     -------
 *     both screens     GND     GND
 *                      VCC     3V3
 *                      SCL     GPIO12 (SCK, shared)
 *                      SDA     GPIO11 (MOSI, shared)
 *                      RES     GPIO8  (shared)
 *                      DC      GPIO13 (shared)
 *                      BLK     GPIO7  (BL_EN, PWM 20 kHz; 10 k to GND like R4, optional)
 *     screen 1         CS      GPIO10 (CS1)
 *     screen 2         CS      GPIO9  (CS2)
 *     INMP441 mic      VDD     3V3
 *                      GND     GND
 *                      L/R     GND    (left channel)
 *                      SCK     GPIO14 (MIC_BCLK)
 *                      WS      GPIO38 (MIC_WS)
 *                      SD      GPIO15 (MIC_SD)
 *     MAX98357A amp    VIN     5 V (VBUS pad or a USB supply; 3.3 V works, quieter)
 *                      GND     GND
 *                      BCLK    GPIO18
 *                      LRC     GPIO17
 *                      DIN     GPIO16
 *                      SD      GPIO4  (AMP_SD: high while a sound plays; 10 k to GND like R18)
 *                      GAIN    not connected (9 dB)
 *     Speaker on the amp's + / - (4-8 ohm).
 *
 * Serial over the S3's USB-C (USB CDC), 115200 baud, one letter:
 *   screens: n / b next / previous pattern, a auto-cycle on / off, d same / different
 *            pattern on screen 2, i inversion, c RGB / BGR, f SPI 26.7 / 40 MHz,
 *            l backlight 100 / 50 / 10 / 0 %, s speed test
 *   sound  : r record then replay, e replay again, m play the MP3, v volume,
 *            k microphone channel (left / right, if the recording is silent)
 *   ?      : help
 */

#include <Arduino.h>
#include <SPI.h>
#include <ESP_I2S.h>
#include <AudioFileSourcePROGMEM.h>
#include <AudioGeneratorMP3.h>
#include <AudioOutputI2S.h>
#include "image.h"
#include "sound.h"

// ---- pins and settings -------------------------------------------------------

static const int8_t PIN_SCK = 12;
static const int8_t PIN_MOSI = 11;
static const int8_t PIN_DC = 13;
static const int8_t PIN_RST = 8;
static const int8_t PIN_BL = 7;
static const int8_t PIN_CS[2] = {10, 9};   // CS1, CS2
static const int8_t PIN_MIC_SCK = 14;
static const int8_t PIN_MIC_WS = 38;
static const int8_t PIN_MIC_SD = 15;
static const int8_t PIN_AMP_BCLK = 18;
static const int8_t PIN_AMP_LRC = 17;
static const int8_t PIN_AMP_DIN = 16;
static const int8_t PIN_AMP_SD = 4;

static const uint16_t W = 240;
static const uint16_t H = 240;
static const uint32_t AUTO_MS = 4000;
static const uint32_t SPI_HZ[2] = {26666667, 40000000};  // 80 MHz / 3, 80 MHz / 2
static const uint8_t BACKLIGHT[] = {255, 128, 26, 0};

static const uint32_t RATE = 16000;
static const uint32_t REC_SECONDS = 5;
static const uint32_t REC_LEN = RATE * REC_SECONDS;
static const float VOLUMES[] = {0.25f, 0.5f, 1.0f};

static const uint16_t BLACK = 0x0000, WHITE = 0xFFFF, RED = 0xF800, GREEN = 0x07E0,
                      BLUE = 0x001F, CYAN = 0x07FF, MAGENTA = 0xF81F, YELLOW = 0xFFE0,
                      GREY = 0x8410;

static SPIClass spi(FSPI);
static uint16_t *fb = nullptr;           // 240 x 240, big endian (SPI order), in PSRAM
static int16_t *recording = nullptr;     // REC_LEN samples, in PSRAM
static bool recorded = false;

static bool inverted = true;             // IPS ST7789 panels need INVON for true colours
static bool bgr = false;
static bool auto_cycle = true;
static bool different = true;            // screen 2 shows another pattern than screen 1
static bool fast_spi = false;
static bool mic_right = false;           // L/R tied to GND -> left
static uint8_t backlight_step = 0;
static uint8_t volume_step = 1;

// ---- ST7789 on the shared bus ------------------------------------------------

static void select(uint8_t screen) {
  spi.beginTransaction(SPISettings(SPI_HZ[fast_spi], MSBFIRST, SPI_MODE0));
  digitalWrite(PIN_CS[screen], LOW);
}

static void deselect(uint8_t screen) {
  digitalWrite(PIN_CS[screen], HIGH);
  spi.endTransaction();
}

static void command(uint8_t c) {
  digitalWrite(PIN_DC, LOW);
  spi.transfer(c);
  digitalWrite(PIN_DC, HIGH);            // following bytes are parameters / pixels
}

static void command_to(uint8_t screen, uint8_t c, int16_t value = -1) {
  select(screen);
  command(c);
  if (value >= 0) spi.transfer((uint8_t)value);
  deselect(screen);
}

static void window(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1) {
  command(0x2A);                         // CASET
  spi.transfer16(x0);
  spi.transfer16(x1);
  command(0x2B);                         // RASET
  spi.transfer16(y0);
  spi.transfer16(y1);
  command(0x2C);                         // RAMWR
}

// Sends rows y0..y1 of the frame buffer to one screen.
static void push_rows(uint8_t screen, uint16_t y0, uint16_t y1) {
  select(screen);
  window(0, y0, W - 1, y1);
  spi.writeBytes((const uint8_t *)(fb + y0 * W), (y1 - y0 + 1) * W * 2);
  deselect(screen);
}

static void push(uint8_t screen) { push_rows(screen, 0, H - 1); }

static void apply_settings() {
  for (uint8_t s = 0; s < 2; s++) {
    command_to(s, 0x36, bgr ? 0x08 : 0x00);  // MADCTL: rotation 0 (no RAM offset on 240x240)
    command_to(s, inverted ? 0x21 : 0x20);   // INVON / INVOFF
  }
}

static void lcd_init() {
  digitalWrite(PIN_RST, HIGH);           // RST shared: one reset for both screens
  delay(5);
  digitalWrite(PIN_RST, LOW);
  delay(20);
  digitalWrite(PIN_RST, HIGH);
  delay(150);
  for (uint8_t s = 0; s < 2; s++) {
    command_to(s, 0x11);                 // SLPOUT
  }
  delay(120);
  for (uint8_t s = 0; s < 2; s++) {
    command_to(s, 0x3A, 0x55);           // COLMOD: 16 bits per pixel
    command_to(s, 0x13);                 // NORON
  }
  apply_settings();
  for (uint8_t s = 0; s < 2; s++) command_to(s, 0x29);  // DISPON
}

// ---- drawing into the frame buffer ---------------------------------------------

static inline uint16_t swap16(uint16_t c) { return c << 8 | c >> 8; }

static void fill_rect(int16_t x, int16_t y, int16_t w, int16_t h, uint16_t color) {
  if (x < 0) { w += x; x = 0; }
  if (y < 0) { h += y; y = 0; }
  if (x + w > W) w = W - x;
  if (y + h > H) h = H - y;
  if (w <= 0 || h <= 0) return;
  uint16_t c = swap16(color);
  for (int16_t j = y; j < y + h; j++)
    for (int16_t i = x; i < x + w; i++) fb[j * W + i] = c;
}

static void pixel(int16_t x, int16_t y, uint16_t color) {
  if (x >= 0 && y >= 0 && x < W && y < H) fb[y * W + x] = swap16(color);
}

static void fill(uint16_t color) { fill_rect(0, 0, W, H, color); }

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

static const char *draw_pattern(uint8_t n) {
  switch (n) {
    case 0: {                            // bands top to bottom: red, green, blue, white, black
      static const uint16_t colors[] = {RED, GREEN, BLUE, WHITE, BLACK};
      for (uint8_t i = 0; i < 5; i++) fill_rect(0, i * 48, W, 48, colors[i]);
      return "solid";
    }
    case 1: {                            // colour bars + ramps grey / red / green / blue
      static const uint16_t bars[] = {WHITE, YELLOW, CYAN, GREEN, MAGENTA, RED, BLUE, BLACK};
      for (uint8_t i = 0; i < 8; i++) fill_rect(i * 30, 0, 30, 120, bars[i]);
      for (uint8_t band = 0; band < 4; band++)
        for (uint16_t x = 0; x < W; x++) {
          uint8_t v = x * 255 / (W - 1);
          fill_rect(x, 120 + band * 30, 1, 30, band == 0 ? rgb(v, v, v) : band == 1 ? rgb(v, 0, 0)
                    : band == 2 ? rgb(0, v, 0) : rgb(0, 0, v));
        }
      return "bars";
    }
    case 2:                              // edges: red top, green bottom, blue left, yellow right
      fill(BLACK);
      for (uint16_t v = 20; v < W; v += 20) {
        fill_rect(v, 0, 1, H, GREY);
        fill_rect(0, v, W, 1, GREY);
      }
      fill_rect(0, 0, W, 1, RED);
      fill_rect(0, H - 1, W, 1, GREEN);
      fill_rect(0, 0, 1, H, BLUE);
      fill_rect(W - 1, 0, 1, H, YELLOW);
      fill_rect(W / 2 - 1, H / 2 - 10, 2, 20, WHITE);
      fill_rect(W / 2 - 10, H / 2 - 1, 20, 2, WHITE);
      return "frame";
    case 3:
    case 4: {                            // checkerboard 1 px (smooth grey = no glitch) / 8 px
      uint8_t size = n == 3 ? 1 : 8;
      for (uint16_t y = 0; y < H; y++)
        for (uint16_t x = 0; x < W; x++) fb[y * W + x] = ((x / size) ^ (y / size)) & 1 ? WHITE : BLACK;
      return n == 3 ? "checker1" : "checker8";
    }
    case 5: {                            // circles round = square pixels; lines straight
      fill(BLACK);
      static const uint16_t colors[] = {RED, YELLOW, GREEN, CYAN, BLUE, MAGENTA};
      for (uint8_t i = 0; i < 12; i++) circle(W / 2, H / 2, 10 + i * 9, colors[i % 6]);
      for (uint16_t v = 0; v < W; v += 24) {
        line(0, v, v, H - 1, colors[(v / 24) % 6]);
        line(W - 1, H - 1 - v, W - 1 - v, 0, colors[(v / 24 + 3) % 6]);
      }
      fill_rect(W / 2 - 15, H / 2 - 15, 30, 30, WHITE);
      return "shapes";
    }
    default:                             // photo 240 x 240 RGB565, already big endian
      memcpy_P(fb, IMG_RGB565, sizeof(IMG_RGB565));
      return "photo";
  }
}

static const uint8_t PATTERN_COUNT = 7;
static uint8_t pattern = 0;

static void show() {
  for (uint8_t s = 0; s < 2; s++) {
    uint8_t n = (pattern + (different && s ? 3 : 0)) % PATTERN_COUNT;
    const char *name = draw_pattern(n);
    uint32_t t0 = micros();
    push(s);
    Serial.printf("PAT,screen%u,%u,%s,push_ms=%.1f\n", s + 1, n, name, (micros() - t0) / 1000.0f);
  }
}

static void speed_test() {
  uint32_t t0 = micros();
  for (uint8_t i = 0; i < 10; i++) {
    fill(i & 1 ? WHITE : BLACK);
    push(0);
    push(1);
  }
  Serial.printf("SPEED,spi_hz=%lu,frame_ms_per_screen=%.1f\n", SPI_HZ[fast_spi], (micros() - t0) / 20000.0f);
}

// Level bar on the top 12 rows of both screens while recording / playing (peak, log scale).
static void level_bar(int32_t peak, uint16_t color) {
  uint16_t w = peak > 0 ? constrain((int)(log10f(peak) * W / 4.5f), 0, W) : 0;  // 1 -> 0, 32767 -> ~W
  fill_rect(0, 0, w, 12, color);
  fill_rect(w, 0, W - w, 12, BLACK);
  push_rows(0, 0, 11);
  push_rows(1, 0, 11);
}

// ---- sound -------------------------------------------------------------------

static void record() {
  I2SClass mic;
  mic.setPins(PIN_MIC_SCK, PIN_MIC_WS, -1, PIN_MIC_SD);
  // 32-bit slots = 64 clocks per frame (INMP441), 16 kHz -> SCK 1.024 MHz
  if (!mic.begin(I2S_MODE_STD, RATE, I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_MONO,
                 mic_right ? I2S_STD_SLOT_RIGHT : I2S_STD_SLOT_LEFT)) {
    Serial.println("# I2S mic start failed");
    return;
  }
  Serial.printf("REC,start,seconds=%lu\n", REC_SECONDS);
  fill(BLACK);
  push(0);
  push(1);
  static int32_t block[512];
  for (uint8_t i = 0; i < 4; i++) mic.readBytes((char *)block, sizeof(block));  // ~0.13 s: mic start-up

  int64_t sum = 0;
  int32_t lo = INT32_MAX, hi = INT32_MIN;
  for (uint32_t n = 0; n < REC_LEN;) {
    size_t got = mic.readBytes((char *)block, sizeof(block)) / 4;
    int32_t peak = 0;
    for (size_t i = 0; i < got && n < REC_LEN; i++, n++) {
      int32_t s = block[i] >> 8;         // 24-bit sample, left-aligned in the 32-bit slot
      lo = min(lo, s);
      hi = max(hi, s);
      sum += s;
      peak = max(peak, abs(s) >> 8);
      recording[n] = constrain(s >> 4, -32768, 32767);  // keep 20 bits of headroom -> 16 bits, +24 dB
    }
    level_bar(peak, RED);                // every 32 ms, on top of the I2S DMA
  }
  mic.end();

  // remove the DC offset, then normalise to ~ -1 dBFS
  int32_t mean = sum / (int64_t)REC_LEN >> 4;
  int32_t max_abs = 1;
  for (uint32_t n = 0; n < REC_LEN; n++) {
    recording[n] = constrain(recording[n] - mean, -32768, 32767);
    max_abs = max(max_abs, (int32_t)abs(recording[n]));
  }
  Serial.printf("REC,done,min24=%ld,max24=%ld,mean=%ld,gain=x%.1f\n", lo, hi, mean, 29000.0f / max_abs);
  if (hi == lo || max_abs < 4)
    Serial.println("# silent or constant: check SD / SCK / WS, or press k (other channel)");
  for (uint32_t n = 0; n < REC_LEN; n++) recording[n] = (int32_t)recording[n] * 29000 / max_abs;
  recorded = true;
}

static void replay() {
  if (!recorded) {
    Serial.println("# nothing recorded yet (r)");
    return;
  }
  I2SClass amp;
  amp.setPins(PIN_AMP_BCLK, PIN_AMP_LRC, PIN_AMP_DIN);
  if (!amp.begin(I2S_MODE_STD, RATE, I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_STEREO)) {
    Serial.println("# I2S amp start failed");
    return;
  }
  Serial.println("PLAY,recording");
  digitalWrite(PIN_AMP_SD, HIGH);
  float vol = VOLUMES[volume_step];
  static int16_t frames[2 * 512];
  for (uint32_t n = 0; n < REC_LEN; n += 512) {
    int32_t peak = 0;
    size_t count = min<uint32_t>(512, REC_LEN - n);
    for (size_t i = 0; i < count; i++) {
      int16_t s = recording[n + i] * vol;
      frames[2 * i] = frames[2 * i + 1] = s;   // same sample on both channels
      peak = max(peak, (int32_t)abs(s));
    }
    amp.write((const uint8_t *)frames, count * 4);
    level_bar(peak, GREEN);
  }
  memset(frames, 0, sizeof(frames));
  amp.write((const uint8_t *)frames, sizeof(frames));  // flush the DMA with silence
  digitalWrite(PIN_AMP_SD, LOW);
  amp.end();
  Serial.println("PLAY,done");
}

static void play_mp3() {
  Serial.printf("PLAY,mp3,bytes=%u\n", (unsigned)sizeof(SOUND_MP3));
  fill(BLACK);
  push(0);
  push(1);
  AudioFileSourcePROGMEM file(SOUND_MP3, sizeof(SOUND_MP3));
  AudioOutputI2S out;
  out.SetPinout(PIN_AMP_BCLK, PIN_AMP_LRC, PIN_AMP_DIN);
  out.SetGain(VOLUMES[volume_step]);
  AudioGeneratorMP3 mp3;
  digitalWrite(PIN_AMP_SD, HIGH);
  if (!mp3.begin(&file, &out)) {
    Serial.println("# MP3 start failed");
  } else {
    uint32_t last = millis();
    while (mp3.isRunning()) {
      if (!mp3.loop()) mp3.stop();
      if (millis() - last > 100) {       // progress bar (the decoder has no level to show)
        last = millis();
        fill_rect(0, 0, (uint32_t)file.getPos() * W / sizeof(SOUND_MP3), 12, CYAN);
        push_rows(0, 0, 11);
        push_rows(1, 0, 11);
      }
    }
  }
  digitalWrite(PIN_AMP_SD, LOW);
  Serial.println("PLAY,done");
}

// ---- commands ----------------------------------------------------------------

static void print_help() {
  Serial.println("# screens: n/b next/prev, a auto, d same/different, i inversion, c RGB/BGR,");
  Serial.println("#          f SPI 26.7/40 MHz, l backlight, s speed");
  Serial.println("# sound  : r record + replay, e replay, m MP3, v volume, k mic channel, ? help");
}

static void handle_command(char cmd) {
  switch (cmd) {
    case 'n': pattern = (pattern + 1) % PATTERN_COUNT; show(); break;
    case 'b': pattern = (pattern + PATTERN_COUNT - 1) % PATTERN_COUNT; show(); break;
    case 'a': auto_cycle = !auto_cycle; Serial.println(auto_cycle ? "# auto on" : "# auto off"); break;
    case 'd': different = !different; show(); break;
    case 'i': inverted = !inverted; apply_settings(); Serial.println(inverted ? "# INVON" : "# INVOFF"); break;
    case 'c': bgr = !bgr; apply_settings(); show(); Serial.println(bgr ? "# BGR" : "# RGB"); break;
    case 'f': fast_spi = !fast_spi; Serial.printf("# SPI %lu Hz\n", SPI_HZ[fast_spi]); show(); break;
    case 'l':
      backlight_step = (backlight_step + 1) % sizeof(BACKLIGHT);
      ledcWrite(PIN_BL, BACKLIGHT[backlight_step]);
      Serial.printf("# backlight %u %%\n", BACKLIGHT[backlight_step] * 100 / 255);
      break;
    case 's': speed_test(); show(); break;
    case 'r': record(); replay(); show(); break;
    case 'e': replay(); show(); break;
    case 'm': play_mp3(); show(); break;
    case 'v':
      volume_step = (volume_step + 1) % (sizeof(VOLUMES) / sizeof(VOLUMES[0]));
      Serial.printf("# volume %d %%\n", (int)(VOLUMES[volume_step] * 100));
      break;
    case 'k': mic_right = !mic_right; Serial.println(mic_right ? "# mic right" : "# mic left"); break;
    case '?':
    case 'h': print_help(); break;
    default: break;                      // ignore CR, LF and the rest
  }
}

void setup() {
  pinMode(PIN_AMP_SD, OUTPUT);
  digitalWrite(PIN_AMP_SD, LOW);         // amp off until a sound plays
  for (int8_t cs : PIN_CS) {
    pinMode(cs, OUTPUT);
    digitalWrite(cs, HIGH);
  }
  pinMode(PIN_DC, OUTPUT);
  pinMode(PIN_RST, OUTPUT);
  ledcAttach(PIN_BL, 20000, 8);          // BL_EN PWM 20 kHz (above hearing, next to the amp)
  ledcWrite(PIN_BL, BACKLIGHT[0]);

  Serial.begin(115200);
  uint32_t t0 = millis();
  while (!Serial && millis() - t0 < 3000) {}
  Serial.println("# TARS bench test - S3 Mini: 2 x ST7789, INMP441, MAX98357A");
  print_help();

  fb = (uint16_t *)ps_malloc(W * H * 2);
  recording = (int16_t *)ps_malloc(REC_LEN * 2);
  Serial.printf("# PSRAM %lu bytes, free %lu\n", (unsigned long)ESP.getPsramSize(), (unsigned long)ESP.getFreePsram());
  if (!fb || !recording) {
    Serial.println("# no PSRAM: check the board (S3 Mini = 2 MB PSRAM)");
    while (true) delay(1000);
  }

  spi.begin(PIN_SCK, -1, PIN_MOSI, -1);
  lcd_init();
  show();
}

void loop() {
  static uint32_t last = millis();
  while (Serial.available()) {
    handle_command(Serial.read());
    last = millis();
  }
  if (auto_cycle && millis() - last >= AUTO_MS) {
    pattern = (pattern + 1) % PATTERN_COUNT;
    show();
    last = millis();
  }
}
