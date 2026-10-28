/*
 * TARS - 1.3" ST7789 240x240 screen bench test (lcd130cs, 8 pins with CS) on a Pro Micro.
 *
 * Shows test patterns then a photo (src/image.h, made by make_image.py), one every
 * AUTO_MS, and times full-screen fills. No library: a minimal ST7789 driver on the
 * hardware SPI.
 *
 * The ST7789 is a 3.3 V part: its inputs must not see 5 V.
 *
 *   3.3 V / 8 MHz Pro Micro: wire straight, screen VCC on the Pro Micro VCC (3.3 V).
 *   5 V / 16 MHz Pro Micro : screen VCC on a 3.3 V supply (the TPS63020 fed from the
 *                            Pro Micro VCC works), common GND, and a divider on every
 *                            signal: 1 k in series from the Pro Micro, 2 k (or 2.2 k)
 *                            to GND at the screen pin -> ~3.3 V.
 *
 *     Screen    Pro Micro
 *     ------    ---------
 *     GND  ---- GND
 *     VCC  ---- 3.3 V (see above)
 *     SCL  ---- 15  (SCK)
 *     SDA  ---- 16  (MOSI)
 *     RES  ---- 8
 *     DC   ---- 9
 *     CS   ---- 10
 *     BLK  ---- 5   (PWM; left unconnected, the module's pull-up keeps the backlight on)
 *
 * Patterns: solid fills, colour bars + ramps, frame + grid (edge pixels: is the whole
 * 240 x 240 visible behind the window?), checkerboards (1 px shows SPI glitches),
 * circles and lines, photo.
 *
 * Serial commands (115200 baud, one letter):
 *   n / p   next / previous pattern      a   auto-cycle on / off
 *   i       colour inversion on / off    c   RGB / BGR order
 *   b       backlight 100 / 50 / 10 / 0 % (PWM on BLK)
 *   s       speed test (10 full fills)   ?   help
 * Red shows as blue: press c. Black and white swapped: press i.
 */

#include <Arduino.h>
#include <SPI.h>
#include "image.h"

static const uint8_t PIN_CS = 10;
static const uint8_t PIN_DC = 9;
static const uint8_t PIN_RST = 8;
static const uint8_t PIN_BLK = 5;
static const uint16_t W = 240;
static const uint16_t H = 240;
static const uint32_t AUTO_MS = 4000;
static const uint32_t SERIAL_WAIT_MS = 3000;
// Modules without a CS pin (7 pins) need SPI_MODE3; the 8-pin one works in mode 0.
static const SPISettings LCD_SPI(F_CPU / 2, MSBFIRST, SPI_MODE0);

static const uint16_t BLACK = 0x0000, WHITE = 0xFFFF, RED = 0xF800, GREEN = 0x07E0,
                      BLUE = 0x001F, CYAN = 0x07FF, MAGENTA = 0xF81F, YELLOW = 0xFFE0,
                      GREY = 0x8410;

static bool inverted = true;             // IPS ST7789 panels need INVON for true colours
static bool bgr = false;
static bool auto_cycle = true;
static uint8_t backlight_step = 0;
static const uint8_t BACKLIGHT[] = {255, 128, 26, 0};

// ---- minimal ST7789 driver -------------------------------------------------

static void command(uint8_t c) {
  digitalWrite(PIN_DC, LOW);
  digitalWrite(PIN_CS, LOW);
  SPI.transfer(c);
  digitalWrite(PIN_DC, HIGH);            // following bytes are parameters
}

static void end_write() {
  digitalWrite(PIN_CS, HIGH);
}

static void command1(uint8_t c, uint8_t value) {
  command(c);
  SPI.transfer(value);
  end_write();
}

// Opens a window and leaves CS low: push width x height pixels, then end_write().
static void begin_pixels(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1) {
  command(0x2A);                         // CASET
  SPI.transfer16(x0);
  SPI.transfer16(x1);
  command(0x2B);                         // RASET
  SPI.transfer16(y0);
  SPI.transfer16(y1);
  command(0x2C);                         // RAMWR
}

static void fill_rect(int16_t x, int16_t y, int16_t w, int16_t h, uint16_t color) {
  if (x < 0) { w += x; x = 0; }
  if (y < 0) { h += y; y = 0; }
  if (x + w > W) w = W - x;
  if (y + h > H) h = H - y;
  if (w <= 0 || h <= 0) return;
  begin_pixels(x, y, x + w - 1, y + h - 1);
  for (uint32_t n = (uint32_t)w * h; n; n--) SPI.transfer16(color);
  end_write();
}

static void pixel(int16_t x, int16_t y, uint16_t color) {
  if (x < 0 || y < 0 || x >= W || y >= H) return;
  begin_pixels(x, y, x, y);
  SPI.transfer16(color);
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
  digitalWrite(PIN_RST, HIGH);
  delay(5);
  digitalWrite(PIN_RST, LOW);
  delay(20);
  digitalWrite(PIN_RST, HIGH);
  delay(150);
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
  for (uint8_t i = 0; i < 5; i++) {      // 5 bands, then the last colour fills the screen
    fill_rect(0, i * 48, W, 48, colors[i]);
  }
  Serial.println(F("# bands top to bottom: red, green, blue, white, black"));
}

static void pattern_bars() {
  static const uint16_t bars[] = {WHITE, YELLOW, CYAN, GREEN, MAGENTA, RED, BLUE, BLACK};
  for (uint8_t i = 0; i < 8; i++) fill_rect(i * 30, 0, 30, 120, bars[i]);
  // four ramps 0 -> full, 30 px high: grey, red, green, blue
  for (uint8_t band = 0; band < 4; band++) {
    begin_pixels(0, 120 + band * 30, W - 1, 120 + band * 30 + 29);
    for (uint8_t y = 0; y < 30; y++) {
      for (uint16_t x = 0; x < W; x++) {
        uint8_t v = x * 255 / (W - 1);
        SPI.transfer16(band == 0 ? rgb(v, v, v) : band == 1 ? rgb(v, 0, 0)
                       : band == 2 ? rgb(0, v, 0) : rgb(0, 0, v));
      }
    }
    end_write();
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
  for (uint16_t y = 0; y < H; y++)
    for (uint16_t x = 0; x < W; x++)
      SPI.transfer16(((x / size) ^ (y / size)) & 1 ? WHITE : BLACK);
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
  uint16_t palette[16];
  for (uint8_t i = 0; i < 16; i++) palette[i] = pgm_read_word(&IMG_PALETTE[i]);
  begin_pixels(0, 0, W - 1, H - 1);
  for (uint8_t y = 0; y < IMG_SIDE; y++) {
    for (uint8_t rep = 0; rep < 2; rep++) {  // each source row twice
      const uint8_t *row = IMG_PIXELS + y * (IMG_SIDE / 2);
      for (uint8_t x = 0; x < IMG_SIDE / 2; x++) {
        uint8_t b = pgm_read_byte(row + x);
        uint16_t c0 = palette[b >> 4], c1 = palette[b & 0x0F];
        SPI.transfer16(c0); SPI.transfer16(c0);
        SPI.transfer16(c1); SPI.transfer16(c1);
      }
    }
  }
  end_write();
  Serial.println(F("# photo 120 x 120 x2, 16 colours"));
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
  uint32_t ms = millis() - t0;
  Serial.print(F("SPEED,full_fill_ms="));
  Serial.print(ms / 10);
  Serial.print(F(",spi_hz="));
  Serial.println(F_CPU / 2);
}

static void print_help() {
  Serial.println(F("# n/p next/prev, a auto on/off, i inversion, c RGB/BGR, b backlight, s speed, ? help"));
}

static void handle_command(char cmd) {
  switch (cmd) {
    case 'n': pattern = (pattern + 1) % PATTERN_COUNT; show(pattern); break;
    case 'p': pattern = (pattern + PATTERN_COUNT - 1) % PATTERN_COUNT; show(pattern); break;
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
    case 'b':
      backlight_step = (backlight_step + 1) % sizeof(BACKLIGHT);
      analogWrite(PIN_BLK, BACKLIGHT[backlight_step]);
      Serial.print(F("# backlight "));
      Serial.println(BACKLIGHT[backlight_step] * 100 / 255);
      break;
    case 's': speed_test(); show(pattern); break;
    case '?':
    case 'h': print_help(); break;
    default: break;                      // ignore CR, LF and the rest
  }
}

void setup() {
  pinMode(PIN_CS, OUTPUT);
  pinMode(PIN_DC, OUTPUT);
  pinMode(PIN_RST, OUTPUT);
  digitalWrite(PIN_CS, HIGH);
  analogWrite(PIN_BLK, BACKLIGHT[0]);

  Serial.begin(115200);
  uint32_t t0 = millis();
  while (!Serial && millis() - t0 < SERIAL_WAIT_MS) {}
  Serial.println(F("# TARS ST7789 240x240 screen test"));
  print_help();

  SPI.begin();                           // SS (pin 17, RX LED) becomes an output: SPI master
  SPI.beginTransaction(LCD_SPI);         // only device on the bus: never released
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
