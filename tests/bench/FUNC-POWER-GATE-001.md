# Bench test FUNC-POWER-GATE-001 — the card supply is off in reset and when commanded off

Requirement: [FUNC-POWER-GATE-001](../../requirements/functional.md#func-power-gate-001). Manual test, run at bring-up step **3.8** ([bring-up.md](bring-up.md)); add a line to *Results* every time it is run. Step 1 needs no firmware; step 2 needs a firmware that drives SD_EN (GPIO36). The Unity part of the acceptance (signal pins as inputs) is a firmware test.

## Equipment
- The power block and the S3 Mini on its carrier, P1 and the microSD reader wired (card inserted).
- A multimeter (V range).
- A wire or tweezers to hold the S3 in reset (its EN pin to GND), or its RST button.

## Setup
1. SW1 on, the system powered (cells or the bench supply on B+ / B−).
2. Meter (V) on the microSD reader's VCC and GND pins (SD_3V3).

## Steps
1. Hold the S3 in reset (EN to GND, or keep RST pressed) and read SD_3V3. Release.
2. With the firmware running: command the card supply off (SD_EN high), read SD_3V3; command it on, read again.

## Pass criteria
- Step 1: SD_3V3 < 0.1 V while the controller is held in reset (R22 keeps Q5 off).
- Step 2: SD_3V3 < 0.1 V when commanded off, ≈ 3.3 V when commanded on.

## Results
| Date | Commit / build | SD_3V3 in reset | Commanded off / on | Pass | By | Notes |
|---|---|---|---|---|---|---|
