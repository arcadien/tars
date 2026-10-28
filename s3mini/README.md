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
- **Flash**: ~54 % of the 1.25 MB app partition (48 % before the sensors) (default 4 MB layout with OTA), mostly the Arduino /
  ESP-IDF core (no Wi-Fi linked yet), the 115 KB photo and the MP3 decoder (details below).
- **PIR (GPIO3)**: 30 s warm-up (`w` skips it). Each pulse is logged with what the S3 was doing
  (idle, drawing, recording, playing, mp3): `p` prints the counts per activity. Pulses while nobody
  moves = false triggers from the backlight PWM, SPI bursts or the speaker (README checklist: 1 nF on
  GPIO3 if so). A green bar at the bottom of both screens follows OUT.
- **BME280** (0x76, forced mode, `t`): the I2C scan at start-up (`g`) also names the ADXL345 (0x53),
  DS3231 (0x68) and ZS-042 EEPROM (0x57) if they are on the bus. 100 kHz as in TARS.
- **Battery** (`u`): VBAT/2 on GPIO1, eFuse-calibrated ADC, 16 samples; compare with a multimeter
  (README: ± 3 %). Without C6 100 nF at the pin the 500 k source reads low and noisy. `j` logs BME280
  + battery every 2 s (CSV `BME,...` / `VBAT,...`), e.g. during a charge.
- **PSRAM** is required (frame buffer + recording); the sketch stops with a message if it's missing.

## Flash budget and firmware updates (notes, 2026-10-28)

### Where the 633 KB of `bench_test` go

Measured from `firmware.map`:

| Part | Size | With pure ESP-IDF |
|---|---|---|
| Photo 240 × 240 (115 KB) + MP3 (26 KB) | 141 KB | same |
| The sketch itself | ~8 KB | same |
| ESP8266Audio (mostly the MP3 decoder and its tables) | 104 KB | other decoder needed: minimp3 ~25–30 KB |
| Arduino layer (Serial, SPI, ledc, start-up) | ~55 KB | saved |
| ESP-IDF drivers (GPIO, I2S, UART, RMT…), libc, FreeRTOS, NVS, coredump… | ~250 KB | almost all kept (Arduino-ESP32 is built on ESP-IDF) |

- Moving to ESP-IDF saves **~60–100 KB** (5–8 % of the partition). minimp3 instead of ESP8266Audio
  saves as much and works under Arduino too.
- The 48 % is of the **1.25 MB app partition**: the default 4 MB layout keeps two OTA slots.
- On TARS, pictures and sounds go to LittleFS / the microSD, not into the code (−141 KB).
- The only big item to come is Wi-Fi / BLE: +500–700 KB, the same Espressif stack with Arduino
  or ESP-IDF.
- ESP-IDF brings nothing for deep sleep: `esp_sleep_*`, `gpio_hold` and EXT1 wake-up are called
  directly from an Arduino sketch. ESP-IDF costs: LovyanGFX or `esp_lcd` for the screens, no
  ESP8266Audio (minimp3 / esp-audio-codec), menuconfig, slower builds. Arduino can also run as an
  ESP-IDF component if one day both are needed.
- **Decision for now: stay on Arduino.** If flash gets tight: `huge_app` partitions + minimp3
  first, they gain more than a port.

### OTA and the microSD

OTA keeps **two app slots**: the update is written to the other slot while the current one runs,
and boots only once fully written and checked; if it crashes at start-up the bootloader rolls back.
That safety costs half of the app space.

The **microSD can be the source of an update, not a replacement for flash**: the ESP32 runs code
from its internal flash (cache / XIP), never from the SD. Copying `firmware.bin` from the SD into
flash uses Arduino's `Update` library (example `SD_Update`); with the two-slot safety kept, nothing
is gained.

| Scheme | 4 MB layout | Update | If the update is interrupted |
|---|---|---|---|
| Classic OTA (default) | 2 × 1.25 MB | Wi-Fi or SD → the other slot | the old firmware boots |
| Updater + one big app | ~0.4 MB small "factory" updater (reads the SD) + ~3.3 MB app | TARS reboots into the updater (`esp_ota_set_boot_partition`), which copies `firmware.bin` from the SD into the app | the updater boots again and retries |
| No OTA (`huge_app`) | 3 MB single app | USB-C of the S3 only | nothing to recover: plug the cable |

- Updater + big app: an ESP-IDF scheme (factory + `ota_0`), usable from Arduino. No rollback to the
  previous version, but TARS can't brick itself. The updater needs the SD driver (~300–400 KB).
- The TARS microSD is fine for it: SDMMC 1-bit at 10 MHz copies 1 MB in a few seconds; **SD_EN
  (GPIO36) must power the card** during the copy.
- With pictures and sounds on the SD, the TARS app should stay under 1.25 MB even with Wi-Fi:
  **classic OTA fits**; the other two schemes only matter if the app grows a lot.
