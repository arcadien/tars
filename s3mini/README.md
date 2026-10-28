# S3 Mini bench tests

Bench tests on the LOLIN S3 Mini with the **TARS pin map** (`tars4_schematic.html`,
`tools/kicad_sch_gen.py`), before the carrier is soldered: Dupont wires straight to the S3 pins.

## `bench_test`: both screens + microphone + amplifier

Same test as `d1mini/bench_test`, on the real target: both 1.3" ST7789 screens (shared SCK / MOSI /
DC / RST, CS1 / CS2, BL_EN PWM), INMP441 on I2S1, MAX98357A on I2S0 with AMP_SD. Wiring and serial
commands are at the top of `bench_test/src/main.cpp`; photo and MP3 come from `bench_assets/`.

```sh
cd s3mini/bench_test
uvx platformio run -t upload         # no port? hold 0 (BOOT), press RST, release
uvx platformio device monitor        # USB-C, 115200 baud
```

Not run on hardware yet (compiles only, 2026-10-28). Arduino-ESP32 3.3, ESP8266Audio 2.4.1.

## Points to watch

- **Bench wiring has no series resistors**: R12 / R19 (SCK split), R20 (MOSI), R13 / R14 (BCLK / LRC)
  and R10 / R18 (AMP_SD) live on the carrier and P2. Fine with short wires; if the image glitches at
  40 MHz with long wires, that's what they are for.
- **SPI speed** (README checklist): starts at 26.7 MHz, `f` switches to 40 MHz. `s` prints the frame
  time per screen. Check the 1 px checkerboard on **screen 2** (longest wires) at both speeds.
- **`d`** shows a different pattern on screen 2: each CS really selects its own screen. Both
  identical and fixed = CS wiring swapped or shorted.
- **Microphone**: proper 32-bit slots here (64 clocks per frame, SCK 1.024 MHz), unlike the D1 mini.
  Silent recording → `k` (other channel), then SD / SCK / WS wiring. The printed `min24 / max24` are
  raw 24-bit values: a few hundred at rest is normal.
- **Recording**: 5 s in PSRAM (`REC_SECONDS`), stored at +24 dB over the 16 MSBs, then DC removed and
  normalised. A loud clap close to the mic can clip.
- **AMP_SD (GPIO4)** is driven high only while a sound plays, low otherwise (as in TARS deep sleep).
  On the breakout without R18 the 1 M pull-up keeps the amp on even if GPIO4 isn't wired.
- **Amp supply**: VIN on 5 V (the S3 Mini's VBUS pad, or a USB supply), not 3V3 if you want volume.
  Start at 50 % (`v`).
- **BL_EN** PWM at 20 kHz (above hearing, next to the amp); `l` steps 100 / 50 / 10 / 0 %. Measure
  the BLK current at 100 % (README: transistor needed only if it feeds the LEDs directly).
- **Flash**: ~48 % of the 1.25 MB app partition (default 4 MB layout with OTA), mostly the Arduino /
  Wi-Fi core, the 115 KB photo and the MP3 decoder.
- **PSRAM** is required (frame buffer + recording); the sketch stops with a message if it's missing.
