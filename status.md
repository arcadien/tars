# Branch mech-audio — speaker and amplifier housing

Branch state file (CLAUDE.md, *Branches*): read it first when the branch is picked up again, keep it
current, answer the questions here.

## Goal
Fit the speaker and the I2S amplifier actually bought into the right middle column (column 2), and write the AUDIO /
MECH requirements for them before any model change.

## State (2026-10-28)
- Branch opened from main; no requirement, no model change yet.
- Measured (on main, `hardware/measurements.md`): amplifier board 22.4 × 38.4, speaker 66 × 30 × 17 (with its box).
- Model still has the old parts: `spk` 22 × 10 × 39 (z 30–69, behind the lower black panel 32.7–66.2), `amp`
  MAX98357A 19.4 × 18 (z 76.7–94.7), C7 at z 80. Column interior 27.2 wide × 26 deep behind the splint; lid screw
  rows at z 4.6, 99.2, 135.9; free z 100–136; P2 at 139.9.

## Findings
- **Speaker**: the 30 mm is the width of the box itself (the ears are at the ends, inside the 66): it fits neither
  way in 27.2 × 26, nor turned at an angle. Options: (1) take the bare oval driver out of its box (irreversible) and use
  the column as the enclosure, as the model intended; (2) a smaller speaker from stock (≤ 27 wide, ideally ~22 × 39 × 10);
  (3) wider columns (D 31 → 34): ruled out (proportions, whole model).
- **Amplifier**: generic "I2S DAC AMP" module, SOIC-8 chip, so probably **not a MAX98357A** (often an NS4168).
  - Header G / V / BCLK / LRCLK / DIN: **no shutdown pin**, so AMP_SD (GPIO4) cannot turn it off and its idle current
    (a few mA) would stay on VSYS in deep sleep (budget assumes < 1 µA). Fix with stock parts: NS4168 CTRL pin (cut
    its trace, wire it to GPIO4 through a divider for the channel level), or a P-MOSFET high-side switch on its supply.
  - "Power" LED: remove (LED requirement).
  - JST-PH 2.0 connectors (only XH in stock): desolder, solder the wires; remove the speaker screw terminal too.
  - 22.4 wide fits (26 with rails); 38.4 long: move to the free zone z 100–136 or lay it flat.
- Requirements touched later: [PLAT-POWER-DIST-001](requirements/platform.md#plat-power-dist-001) (MAX98357A on its own
  VSYS pair, C7), [TECH-POWER-BACKFEED-001](requirements/technical.md#tech-power-backfeed-001) (amplifier enable low at start-up),
  `hardware/power_budget.md` amplifier row.

## Open questions
| # | Question | Answer |
|---|---|---|
| A1 | Marking of the amplifier chip (the SOIC-8 in the middle)? | |
| A2 | The two holes: Ø 4.7 at 16 mm between centres, or is 4.7 the width of the white band? | |
| A3 | Buy a MAX98357A breakout (~8 €) instead of adapting the current board? | recommended: keeps the design as is (SD pin on GPIO4, < 1 µA in sleep, 19.4 × 18 slot, schematic, budget and requirements unchanged); a clone (purple board, SD / GAIN pins) at 1–3 € does the same; the current board stays the fallback (CTRL trace cut or P-MOSFET switch). User picked a purple clone 19 × 17 (LRC, BCLK, DIN, GAIN, SD, GND, Vin; Adafruit pinout) on 2026-10-28: fits the modelled 19.4 × 18 slot, nothing else changes; leave its screw terminal off (speaker wires soldered); measure the board on arrival (→ `amp`), bench E-M1 (SD pull-up) still applies |
| S1 | Speaker: open its box and use the bare driver (option 1), or another speaker from stock (option 2)? | looking in the drawers (2026-10-28) |
| S4 | Round speaker candidate: diameter, impedance, power? | depth 5 mm (2026-10-28): fits easily (≤ 15); diameter must be ≤ Ø23; diameter and impedance still to read |
| S3 | Which impedance, which shape if bought new? | **8 Ω** (4 Ω also works but doubles the current peaks on VSYS: ~1 A at full volume vs ~0.5 A), 0.5–2 W. Face against the lower black panel (27.2 wide inside, minus the side rails ≈ 23; panel 33.5 tall): **oval 20 × 30, long axis vertical**, fits; **round Ø28 does not** (wider than the interior); a round one must be ≤ Ø23. Depth ≤ ~15 with its wires |
| S2 | If option 1: bare driver long axis, short axis, depth with the magnet, flange if any | bare driver **28.6 × 40 × 11.6** (2026-10-28): depth fits (26 behind the splint), but 28.6 is 1.4 wider than the column interior (27.2) and 5.6 wider than the room between the side rails (~23); no angle helps; thinning the side walls to fit would leave 0.75 mm. Fits only if the basket under the frame is ≤ ~23 wide and the frame lips can be trimmed (S5) |
| S5 | Bare driver: width of the basket / magnet under the frame (without the stamped lips or ears)? | |

## Next
Answers A1–S2 → draft the AUDIO / MECH requirements (housing, shutdown, connectors) → validation → model.
