# D1 mini bench tests

Bench tests on a Wemos D1 mini (ESP8266, 3.3 V), used while the LOLIN S3 Mini is not ready. The
reference is still the S3: pins, buses and sizes here are **not** the TARS ones.

## `bench_test`: screen + microphone + amplifier

1.3" ST7789 240 × 240 screen (patterns + photo), INMP441 microphone ("record and replay"), MAX98357A
amplifier + speaker (replay + a short MP3). Wiring and serial commands are at the top of
`bench_test/src/main.cpp`.

```sh
cd d1mini/bench_test
uvx platformio run -t upload
uvx platformio device monitor        # 115200 baud
uv run make_assets.py                # photo / MP3 -> src/image.h, src/sound.h
uv run make_assets.py --mp3 my.mp3 --seconds 8
```

Not run on hardware yet (compiles only, 2026-10-28).

## Points to watch

### Pins

- **The ESP8266 I2S pins are fixed**: out BCLK D8 (GPIO15), LRC D4 (GPIO2), DIN RX (GPIO3); in SD D6
  (GPIO12), SCK D7 (GPIO13), WS D5 (GPIO14). They take the hardware SPI pins, so the screen runs on a
  **bit-banged SPI** on D1 / D2 / D3 / D0.
- **No pin left for the screen RES**: it goes to the D1 mini **RST** (the screen resets with the board),
  plus a software reset (SWRESET) at start-up.
- **Boot strapping pins**: D3 (GPIO0, screen DC) and D4 (GPIO2, LRC) must be high at boot, D8 (GPIO15,
  BCLK) low. The modules' inputs don't pull them; don't add pull-ups / pull-downs on them.
- D4 is also the blue LED: it flickers while a sound plays.

### Serial port

- **RX (GPIO3) is both the USB serial input and the I2S data out.** Commands are read only between
  two sounds: the sketch stops the I2S and restarts `Serial` after each one. Keys typed during a sound
  are lost. The serial output (TX) works all the time.
- Typing while a sound plays is harmless: the D1 mini has 470 Ω between the CH340 and GPIO3 (< 4 mA).

### Microphone

- The ESP8266 sends **32 clock cycles per I2S frame** (16 bits per channel); the INMP441 datasheet
  expects 64. If the recording stays silent even after `l` (other channel), suspect this first:
  try the 24-bit mode (`i2s_set_bits(24)`, 48 cycles per frame; the samples then come left-aligned).
- I2S clock 32 × 16 kHz = 512 kHz, right at the INMP441 minimum (~0.5 MHz). Don't lower `MIC_RATE`.
- L/R to GND = left channel. The data line floats during the other half of the frame: a constant
  reading on one channel is normal, a constant reading on both is a wiring fault (SD / SCK / WS).
- The level is low (speech ≈ ±30 counts on 16 bits): the sketch removes the DC offset and
  normalises before replaying. The `gain=x...` value printed after each recording tells how quiet it was.
- Recording length is limited by **RAM** (~2.5 s at 8 kHz, 16 bits): the buffer takes the largest free
  block minus 8 KB. The MP3 command frees it (the decoder needs ~30 KB of heap).

### Amplifier

- VIN on 5 V (USB). SD and GAIN not connected: the breakout's pull-up turns it on, gain 9 dB.
  The sketch sends the same sample on both channels.
- Volume `v`: 25 / 50 / 100 %. At 100 % on 5 V a small speaker can distort or draw USB current
  peaks: start at 50 %.

### Screen

- **Inversion / colour order depend on the module**: black and white swapped → `i`; red shows as blue → `c`.
- **1 px checkerboard**: it should look smooth grey. Glitches → shorter Dupont wires (the bit-banged
  SPI edges are fast), or more `nop` in `spi_byte()`.
- The frame pattern draws the outermost pixels (red top, green bottom, blue left, yellow right): use
  it to check that the whole 240 × 240 shows through the printed window.
- Long fills call `yield()`: the ESP8266 watchdog resets the board after ~3 s without one.

### Flash size

The build uses ~51 % of the 1 MB program slot, but almost none of it is the test code:

| Part | Size |
|---|---|
| Empty sketch (Arduino core + Espressif Wi-Fi stack, always linked) | 265 KB (25 %) |
| Photo 240 × 240 RGB565, uncompressed | 115 KB |
| MP3 decoder (tables) + ESP8266Audio | ~60 KB |
| The MP3 jingle | 26 KB |
| The sketch itself | ~10–15 KB |

The D1 mini has 4 MB of flash; the rest is reserved for OTA and LittleFS. Moving the photo and MP3
to LittleFS (`uvx platformio run -t uploadfs`) would bring it down to ~38 % and let them change
without recompiling. Not relevant for TARS: the S3 Mini has 4 MB and a different budget.

### Editor

VS Code "cannot open source file Arduino.h": IntelliSense doesn't know the PlatformIO paths, the
code compiles. Open `bench_test` with the PlatformIO extension, or run `uvx platformio init --ide vscode`
in it.
