# Bench test TECH-POWER-HOTPLUG-001 — no overshoot when the supply is hot-plugged

Requirement: [TECH-POWER-HOTPLUG-001](../../requirements/technical.md#tech-power-hotplug-001). Manual test, run at bring-up step **3.9 (whole robot)** ([bring-up.md](bring-up.md)); add a line to *Results* every time it is run.

## Equipment
- The assembled robot: D3 and C9 on the TP4056 IN pads, the charge port J1 with its real ~16 cm of wire, D1, VSYS and the amplifier (with C7) wired.
- An oscilloscope, two channels (10× probes, short ground springs); with one channel, run the 10 plugs twice, once per probe point.
- A 5 V ≥ 2 A USB charger and a micro-USB cable.

## Setup
1. SW1 on (the overshoot reaches VSYS through D1 only then).
2. Channel 1 on the TP4056 IN+ pad, ground on IN−. Channel 2 on the amplifier VIN pin, ground on its GND pin.
3. Single-shot trigger on channel 1, rising edge at 5.5 V, 1 V / div, 10 µs / div.

## Steps
1. Plug the charger cable into J1; note both peaks. Unplug, wait 5 s.
2. Repeat 10 times.

## Pass criteria
- Every peak at the TP4056 IN pads ≤ 7.0 V.
- Every peak at the amplifier VIN ≤ 6.0 V (MAX98357A absolute maximum).

## Results
| Date | Commit / build | Highest peak, IN pads | Highest peak, amp VIN | Pass | By | Notes |
|---|---|---|---|---|---|---|
