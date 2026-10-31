# Bench test FUNC-POWER-PATH-001 — on the external supply, the system load does not draw from the battery

Requirement: [FUNC-POWER-PATH-001](../../requirements/functional.md#func-power-path-001). Manual test, run at bring-up step **3.4** ([bring-up.md](bring-up.md)); add a line to *Results* every time it is run.

With a cell still charging, its ~+500 mA charge current would hide a 110 mA draw from it: the test runs on a full cell, once the charge has ended, so any current the load takes from the cell shows as a negative reading.

## Equipment
- The power block with one **full** cell (charged until the TP4056 stopped).
- A multimeter on its **mA range** (sign shown).
- A 33 Ω ≥ 1 W resistor (≈ 110 mA on VSYS) with crocodile leads.
- A 5 V ≥ 2 A USB charger and a micro-USB cable.

## Setup
1. Nothing on the 3V3 (TPS63020 output unloaded). Unplug **X16** (right cell); keep only the full cell on **X12**.
2. Unplug X12, join its two B− contacts with a short jumper, and put the meter in series in B+: **A socket on the board-side B+, COM on the cell-side B+**. A positive reading is current into the cell, a negative one current out of it.
3. Plug the charger into the charge port and wait until the TP4056 shows the end of charge (cell current ≈ 0).
4. SW1 on.

## Steps
1. Without the load: read the cell current.
2. Connect the 33 Ω load across VSYS and GND (X13 VSYS / GND amp contacts); after 10 s read the cell current.
3. Disconnect and reconnect the load three times, reading the cell current each time.
4. Unplug the charger with the load on: the reading must swing to about −110 mA (the cell now feeds the load: this proves the wiring).

## Pass criteria
- Steps 1–3: the cell current stays ≥ −0.1 mA, load on and off (no load current comes from the cell while the supply is connected).
- Step 4: about −110 mA (sanity check).
- The end of charge itself follows [TECH-POWER-CHARGE-001](TECH-POWER-CHARGE-001.md).

## Results
| Date | Commit / build | No load | Load on (lowest) | Charger unplugged | Pass | By | Notes |
|---|---|---|---|---|---|---|---|
