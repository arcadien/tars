# Bench test PLAT-AUDIO-AMP-001 — MAX98357A clone breakout, SD held low

Requirement: [PLAT-AUDIO-AMP-001](../../requirements/platform.md#plat-audio-amp-001). The board size in its slot is
checked by `tests/test_mechanical.py`; this sheet is the bench part (E-M1). Manual test, the sound step runs at bring-up
([bring-up.md](bring-up.md)); add a line to *Results* every time it is run.

## Equipment
- The breakout, bench supply, multimeter, a 10 kΩ resistor (R18).
- For step 2: the amplifier wired to the S3 and the speaker soldered to the OUT+ / OUT− pads.

## Setup
1. Supply at 4 V on Vin / GND, 10 kΩ from SD to GND, nothing else connected.

## Steps
1. Read the voltage on SD (shutdown below 0.16 V on the MAX98357A).
2. Wired on the robot: play the same sample on both I2S channels.

## Pass criteria
- Step 1: SD < 0.1 V (with the board's 1 MΩ pull-up, 36–40 mV).
- Step 2: sound from the speaker, none at boot or with GPIO4 low.

## Results
| Date | Commit / build | Vin | SD | Sound | Pass | By | Notes |
|---|---|---|---|---|---|---|---|
| 2026-10-31 | breakout alone | 4 V | 36 mV | not run | step 1 only | Aurelien | pull-up marked 105 (1 MΩ); 36 mV matches 1 MΩ against 10 kΩ in parallel with the chip's internal pull-down (~100 kΩ, from memory of the datasheet, to confirm) |
