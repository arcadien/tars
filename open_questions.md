# TARS4 — open questions (updated 2026-10-28)

Collects what is still open after the three review rounds (`reviews/2026-10-21-review.md`, `reviews/2026-10-21-review2.md`,
`reviews/2026-10-22-review3-boards.md`).
Blockers B1–B2, decisions D1–D12, improvements and doc fixes are **applied** (recommended options, D11: switch kept);
the README describes the current state (no decision log any more: history in `reviews/` and in git).

## 1. Blockers — settled

| # | Problem | What was done |
|---|---|---|
| B1 | Dupont housings without keying | useless pin removed + cavity plugged (X2 INT2, X8 32K, X5 GAIN with X5 as 4 + 3); one more cavity plugged on the female side of the inline pairs (X3, X7, X15); screens: right-angle header + rib glued on the housing; X14 as JST-PH 3; X6 and X9 unkeyed (reversed, nothing breaks). Pin order in the README (*Connectors*) |
| B2 | TP4056 against the lip of its groove | no upper lip any more (support underneath only) for the TP4056 and the TPS63020, a lid tab holds the back edge; since 2026-10-27 the TP4056 (trimmed to 26.3, micro-USB desoldered) sits on 0.5 ledges without grooves; C9 / D3 lying on the IN end (`charger_h` 5.5) |

## 2. Decisions — taken

D1 right-angle header · D2 continuous rib · D3 X10–X14 parked above the TP4056, boards one by one · D4 split SCK on
the carrier (R12 / R19 47 Ω) · D5 15 printed clips · D6 vent slots · D7 R21 + C12 on the AM312, C10 + C11 on P2,
PWM 20 kHz · D8 C1 SMD 7343 polymer tantalum (POSCAP 10TPE220ML) lying under the S3, on its carrier (2026-10-24) · D9
lid `lid_mid_left` · D10 Q5 on the microSD 3V3 (GPIO36) · D11 switch kept · D12 5 V ≥ 2 A charger.

## 3. Open now

| # | Question | Status |
|---|---|---|
| T1 | **Tube test3** (teardrop bores, G7.95 / 8.0 / 8.05, R8.05 / 8.1 / 8.15) | print and measure → `tube_od` 7.93 + clearances + teardrop pivots, then **one single** STL pass + `tools/update_orca_project.py` on `mechanical/3mf/tars4.3mf`. Don't print the columns before |
| D13 | **Switching charger instead of the TP4056** | TP4056 kept for now (500 mA, R_PROG 2.4k). If E-M8 runs too hot: R_PROG 3.6k (330 mA) or the lower left leg in PETG; alternative TP5100 1 A + separate DW01. IP2312: doesn't fit flat (34.4 × 15) |
| E-M8 | **TP4056 temperature** (PLA legs) | measure the wall after 15 and 30 min of charge: > 45 °C → R_PROG 3.6k. Copper RPi heatsink ≤ ~3 mm + 0.5–1 mm thermal pad between chip and heatsink, never between board and PLA |
| CP1 | **Charge port at the heel** (branch `mech-usb-heel`, [PLAT-MECH-CHARGEPORT-001](requirements/platform.md#plat-mech-chargeport-001)) | modelled with `usbb_out` 1.0 and `usbb_rec` 7.5 × 2.6 still MEASURE: measure the breakout's receptacle (mouth past the PCB edge, shell width × height), update the model; **the branch is merged only after these measurements** |
| VS1 | **VSYS sense** (PLAT-POWER-VSENSE-001, branch `rbd`) | small NPN (BC547 / 2N3904 / 2N2222 / S8050…) + 1 M / 1 M base divider, collector to GPIO37: to add to the schematic, carrier and harness once the POWER requirements are validated |

## 4. Remaining measurements

**Dimensions** (`hardware/measurements.md`): `bk_h` (TPS63020 inductor height), `pir_pcb_dn`, screen active area checked lit,
solder tails on the wall side (ADXL345, MAX98357A, micro-USB), 0.85" screen if used, D-M9 (S3 first pin row, `my0`
margins).

**Electrical**, on the bench (README list *to do when the parts arrive*; currents in `hardware/power_budget.md`): E-M1 SD
pull-up of the amplifier (R18), E-M2 screens' BLK, E-M3 D1 leakage when warm, E-M4 AM312 high level, E-M5 DW01
wake-up, E-M6 SW1 rating, E-M7 sleep current with and without microSD.

**Other**: wanted swing angle for the legs (free wire length at the twist).

## 5. First review items and doc fixes — applied

Nothing open apart from the measurements above.

## 6. Board review no. 3 (2026-10-22) — applied

All boards are **single-sided**. Applied: M1 OUT+ alone in B4 + anti-blob rule extended to every power / other net
pair; M2 R2 lying J8 → J5 (J7 empty next to Q5); M3 Q1 / Q5 legs in insulated 30 AWG wire-wrap wire, gluing
orientation drawn (seen from the top, flipped); M4 carrier wires leaving inwards; m1 carrier cut 1.2 mm below row 1
(`s3_dummy` at 8.8); m2 `pp_lip` 0.6 + R2 as 1/8 W (upper left leg re-exported); m3 check values; m4 V contact removed
from the header; m5 schematic names everywhere (AMP_SD_S3 / AMP_SD, PIR / PIR_OUT, SCK_S3, *_S3 on the S3 side) +
automatic check of the boards against `kicad_sch_gen.py`; m6 P1 without 26 AWG in column A, P2 jumper on the copper
side; m7 C12 ≤ 7 mm → 10 µF 16 V tantalum (2026-10-24); m8 double Dupont contacts documented; m9 wire-wrap wire, tinned
wire, glue in the BOM; m10 doc fixes (C10 non-polarised in KiCad); remarks R1, R3, R4, R6, R7. D14 (30 AWG B+ sense
wire, R2 on the perfboard): **kept as is** (decision of 2026-10-22).

| # | Still open | Options |
|---|---|---|
| D-M9 | Actual position of the S3's first pin row (8.8 mm from the USB edge per the LOLIN drawing) | carrier cut margins (`my0` in `tools/boards.py`) |

## 7. Wiring guide review (2026-10-24) — applied

No blocking point. Applied: heat-shrink closed on every free end before any power-up (steps 3–6); microSD reader
preparation at step 5 (C4 tantalum **lying**: ~6.6 mm up to the TPS63020, C5, R5–R9); polarities in the guide (C9 /
D3 on IN+, C7 + on VIN); C2 / C10 drawn polarised (tantalum, + at G9 / F9) on the plans and in KiCad, C4 too; X12 / X16
on the block side capped with an empty XH housing while unplugged; splices before the TP4056 IN+ / B+ / B− pads;
< 10 µA test on the TP4056 alone; **R20 33 Ω in series on MOSI** (carrier C9–C10, jumper J4 from A6); I2C scan with
0x57 / 0x77; EXT1 mask without the sources already high; double contacts of X2, twists in the right tube, "without
folding back" for two wires per contact, lengths per colour from the README, h ≤ 9 rule on P1 / P2.
Not applied: R2 on the B+ pad (D14, decision of 2026-10-22 kept).

- D-M1 AM312 settled (2026-10-24): cap glued from the inside, Ø11.5 hole (flush dome, Pro Micro test); printed holes ~0.6 mm too small.
- `sd_fwd` = 2 (2026-10-24): microSD card 3 mm out of the lid, 4.5 mm in front of the reader.
