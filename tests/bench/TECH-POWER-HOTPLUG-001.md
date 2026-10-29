# Bench test TECH-POWER-HOTPLUG-001 — no overshoot when the supply is hot-plugged

Requirement: [TECH-POWER-HOTPLUG-001](../../requirements/technical.md#tech-power-hotplug-001). Manual test, run at bring-up step **3.1 (D3, C9 fitted)** ([bring-up.md](bring-up.md)); add a line to *Results* every time it is run.

## Equipment
- The TP4056 module with D3 and C9 on its IN pads, wired to the charge port J1 with its real ~16 cm of wire.
- An oscilloscope (10× probe, short ground spring).
- A 5 V ≥ 2 A USB charger and a micro-USB cable.

## Setup
1. Probe on IN+, ground on IN−, at the TP4056 pads.
2. Single-shot trigger, rising edge at 5.5 V, 1 V / div, 10 µs / div.

## Steps
1. Plug the charger cable into J1; note the peak. Unplug, wait 5 s.
2. Repeat 10 times.

## Pass criteria
- Every peak ≤ 7.0 V.

## Results
| Date | Commit / build | Highest peak of 10 | Pass | By | Notes |
|---|---|---|---|---|---|
