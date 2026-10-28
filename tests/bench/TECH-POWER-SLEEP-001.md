# Bench test TECH-POWER-SLEEP-001 — no always-on indicator on battery-fed rails

Requirement: [TECH-POWER-SLEEP-001](../../requirements/technical.md#tech-power-sleep-001). Manual test, run at bring-up step **2 and 3.9** ([bring-up.md](bring-up.md)); add a line to *Results* every time it is run.

## Equipment
- The boards, before wiring; later the assembled robot.

## Setup
1. Boards unpowered.

## Steps
1. Run [PLAT-POWER-SLEEP-001](PLAT-POWER-SLEEP-001.md) (LEDs removed).
2. Check that the DS3231 32 kHz output is not wired (X8 32K is a keyed, empty position).
3. Check that no other board fed from B+, VSYS or 3V3 has an LED or a clock output left running.

## Pass criteria
- Nothing found; the TP4056 charge LEDs (USB-fed) are allowed.
- The deep-sleep current is checked by [PERF-POWER-SLEEP-001](../../requirements/performance.md#perf-power-sleep-001), and the DS3231 32 kHz output is disabled by the firmware ([PLAT-POWER-SLEEP-002](../../requirements/platform.md#plat-power-sleep-002)).

## Results
| Date | Commit / build | Checked | Pass | By | Notes |
|---|---|---|---|---|---|
