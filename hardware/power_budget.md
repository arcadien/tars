# TARS4 power budget

Current drawn by every module, **estimated** (datasheet typical or README figure) and **measured** on the bench
as soon as the part is wired. Fill the *Measured* columns with the date; keep the estimate for comparison.
Requirements in `requirements/performance.md` (PERF-POWER-*) refer to this table for module currents.

Conventions:
- Currents are at the module's own supply pin (rail in the second column), not at the cells.
- *Sleep* = TARS deep sleep: S3 in deep sleep, screens in SLPIN with BL_EN low, AMP_SD low, microSD cut
  by Q5, sensors in their low-power mode (README *Deep sleep*).
- `?` = no reliable figure yet: measure first. *To check* = estimate from memory of the datasheet, confirm
  against the datasheet when the module is measured.

## Modules

| Module | Rail | Active (estimate) | Peak (estimate) | Sleep (estimate) | Source / note | Active measured | Sleep measured |
|---|---|---|---|---|---|---|---|
| LOLIN S3 Mini (ESP32-S3 + PSRAM) | 3V3 | 80–120 mA average with Wi-Fi | ~400 mA Wi-Fi TX burst | ~10–20 µA (S3) + board LDO quiescent, to check | README *Rough runtime*, C1 sizing | | |
| ST7789 1.3" screen × 2, logic | 3V3 | a few mA each, to check | | ~10 µA each in SLPIN, to check | | | |
| ST7789 backlight × 2 (BLK) | 3V3 | 20–30 mA each if BLK drives an on-board transistor; 40–60 mA each if BLK feeds the LEDs | | 0 (BL_EN low); ~0.66 mA if an on-board BLK pull-up exists (remove it) | README *BL_EN*, checklist E-M2 | | |
| MAX98357A amplifier | VSYS | ~2.5 mA idle (SD high, no sound), to check | several hundred mA at full volume (speaker dependent) | < 1 µA (SD low), to check | own VSYS pair, C7 470 µF | | |
| INMP441 microphone | 3V3 | ~1.4 mA, to check | | no clock = power-down, µA range, to check | | | |
| AM312 PIR | 3V3 (R21) | ~15 µA | | ~15 µA (always on, wakes the S3) | README *AM312* | | |
| ADXL345 accelerometer | 3V3 | 40–140 µA (rate dependent), to check | | ~25 µA in activity-detect mode at low rate, to check | wake source INT1 | | |
| BME280 | 3V3 | ~3.6 µA at 1 forced reading/s, to check | ~0.7 mA during a conversion | ~0.1 µA (sleep mode), to check | forced mode | | |
| DS3231 (ZS-042) | 3V3 | ~0.1–0.2 mA, to check | | same (always on); 32 kHz output disabled | README *Deep sleep*; charging resistor removed | | |
| ZS-042 power LED | 3V3 | 1–3 mA | | 1–3 mA → **removed** | README (drains the cells otherwise) | | |
| ZS-042 EEPROM (AT24C32) | 3V3 | µA range idle | | µA range, to check | | | |
| microSD card + reader | 3V3 (Q5) | 20–100 mA reading / writing, card dependent | ~100 mA+ at insertion / writes | 0 (cut by Q5) | D10, E-M7 | | |
| TPS63020 buck-boost (U9) | VSYS | efficiency ~85–90 % on the 3V3 load | | ~25–50 µA idle (PS/SYNC to GND) | README *TPS63020* | | |
| TP4056 + DW01 module | B+ | charging: 0.5 A in (R_PROG 2.4k) | | < 10 µA from the cells, USB out | checklist 3.1 | | |
| D1 1N5822 (power path) | B+ | | | reverse leakage up to tens of µA, warm | E-M3 | | |
| VBAT/2 divider R2 / R3 1 M / 1 M | B+ | ~2 µA | | ~2 µA (before SW1: also when off) | README *VBAT/2* | | |
| USB_DET divider R15 / R16 | VUSB | ~30 µA, only on the external supply | | 0 on battery | | | |
| VSYS sense: Q4 BC547B + R23 / R24 1 M base divider (GPIO37) | VSYS | ~2–3 µA base current; GPIO37 pull-up on only while reading | | ~2–3 µA | PLAT-POWER-VSENSE-001 (draft) | | |

## Totals

| State | Estimate | Measured | Note |
|---|---|---|---|
| Deep sleep, from the cells | ≤ 0.65 mA target (PERF-POWER-SLEEP-001); sum of the rows above ≈ 0.3–0.5 mA | | E-M7 |
| Switch off, from the cells | ≤ 60 µA target (PERF-POWER-OFF-001): TP4056/DW01 + R2/R3 + D1 leakage | | E-M3, E-M5 |
| Active, Wi-Fi idle, both backlights full, no sound | ~130–220 mA on 3V3 → ~150–260 mA from the cells (3.7 V, buck-boost losses) | | runtime profile of PERF-POWER-RUNTIME-001 (≥ 20 h on 2 × 2500 mAh) |
| Active + sound at full volume | add the amplifier peak | | PERF-POWER-REG-002, PERF-POWER-MAINS-001 |

## Measurement log

| Date | Module / state | Setup (supply, meter, range) | Value | Who |
|---|---|---|---|---|
| | | | | |
