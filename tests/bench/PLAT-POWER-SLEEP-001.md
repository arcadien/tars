# Bench test PLAT-POWER-SLEEP-001 — battery-fed status LEDs removed

Requirement: [PLAT-POWER-SLEEP-001](../../requirements/platform.md#plat-power-sleep-001). Manual test, run at bring-up step **2** ([bring-up.md](bring-up.md)); add a line to *Results* every time it is run.

## Equipment
- A magnifier or a phone camera.
- The ZS-042, TPS63020, GY-291 and microSD boards, the S3 Mini, the TP4056 module.

## Setup
1. Boards unpowered, before wiring.

## Steps
1. Look at each board: ZS-042, TPS63020 module, GY-291, microSD breakout: the power / status LED is removed (empty pads).
2. S3 Mini: the RGB LED (GPIO47) is removed.
3. TP4056: its two charge LEDs are still there (USB-fed only).
4. Take one photo per board for the record.

## Pass criteria
- Every listed LED removed; the TP4056 charge LEDs kept.
- The deep-sleep current is checked by [PERF-POWER-SLEEP-001](../../requirements/performance.md#perf-power-sleep-001) (with the firmware).

## Results
| Date | Commit / build | Boards checked | Photos | Pass | By | Notes |
|---|---|---|---|---|---|---|
