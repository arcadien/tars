# tars4 — measurements to take

Parts all received (2026-10-27). Fill the **Measured** column as you go; everything is merged into `mechanical/scad/tars4.scad` in one
pass at the end, then STL / 3MF are regenerated once. Electrical bench checks stay in the README checklist
(*to do when the parts arrive*), they don't change the model.

**Merged into `mechanical/scad/tars4.scad` on 2026-10-27 (23:50)**; every print part renders
with no WARNING. Side effects: polyfuse holders on the front walls, TPS63020 slot cut 0.15 into the walls (`bk_clr`),
TP4056 grooves gone, screen connector box 8 deep (bundle corridor moved back to y 13.5–25), BME280 0.3 lower, AM312
re-centred in its band (asymmetric extents), `active_dz` −1.1. **Still open**: tube bores (test3, then `tube_od` 7.93 +
clearances + teardrop pivots), `bk_h`, `pir_pcb_dn`, active area checked lit, solder tails. STL / 3MF not regenerated
yet (after test3, one pass).

## Already merged

| Part | Parameter | Value | Date |
|---|---|---|---|
| LOLIN S3 Mini | `d1[1]` length | 34.5 measured → 34.6 | 2026-10-27 |
| LOLIN S3 Mini | `d1_boot_out`: only BOOT sticks out, 1.6 (27 across it) | window through the high-x wall (`d1_boot_window`, 3.6 × 4) | 2026-10-27 |
| LOLIN S3 Mini | `d1_pcb_t` | 1.0 | 2026-10-27 |
| LOLIN S3 Mini | `d1[0]` PCB width without the buttons | 25.4 measured → 25.6 (unchanged, = drawing + margin) | 2026-10-27 |
| Battery spring | solid height | 2.85 (comment only, `spring_work` stays 4) | 2026-10-27 |

## Blocking the columns

| Part | Parameter | Current | Measured | Notes |
|---|---|---|---|---|
| Brass tube | `tube_test`: tightest glued bore that takes the tube (G8.1 / 8.3 / 8.5) | `tube_glue_clr` 0.1 | printed G8.1 / 8.3 / 8.5 → **8.00 / 8.20 / 8.45**; tube **turns even in G8.1** (8.00 printed): too loose for gluing → second test `tube_test2` | holes only ~0.05–0.1 undersize here (not the 0.5 of the PIR plate) |
| Brass tube | `tube_test`: tightest bore that turns freely (R8.3 / 8.5 / 8.7) | `tube_run_clr` 0.3 | printed R8.3 / 8.5 / 8.7 → **8.30 / 8.40 / 8.60**: all turn → second test | |
| Brass tube | outer Ø | `tube_od` 8 | **7.93** | `mechanical/stl/tars4_tube_test3.stl` (teardrop bores, 108 long like test 1): G7.95 / 8.0 / 8.05, R8.05 / 8.1 / 8.15 → measure across + fit. Before: `tube_test2` (no longer exported): G7.9 (glued) + R8.0 (turning) → printed **7.7 / 7.7** (−0.2 / −0.3, vs −0.05…−0.1 on the 1st print): printing session: slicer ~unchanged (Arachne, no hole compensation, which would not act anyway). Bores are **horizontal** (front face down, like the real columns): the ceiling sags → measure each bore **across (Y) and vertically (Z)**; fix in the model at merge (teardrop / flat-top bore, or oversize on Z). Measured: G7.9 → **7.70 across / 7.41 vertical**, R8.0 → **7.74 / 7.49** (the short part cools less: 1st test, 107 mm long like the columns, lost only ~0.1). **Proposal**: teardrop bores, `tube_od` 7.93, glued drawn 8.0, turning drawn 8.1 (1st test: 8.1 → 8.00 turned), tight then sand; confirm with a teardrop test3 as long as test 1 |
| LOLIN S3 Mini | RST-side notch at the USB end: depth, height | `d1_notch` [1.2, 7] | **[2, 7]** (approx.) | the front rib at z = `d1_btn` reaches 2 mm further on the RST side |
| LOLIN S3 Mini | buttons: top edge above the USB end; depth in front of the PCB; **which side BOOT sticks out** (high x = right seen from the front, per the LOLIN drawing) | `d1_btn` 4.5, `d1_btn_y` 3 | BOOT on the right (confirmed); 3 high in front of the PCB (below the USB-C); sticks out **1.3** → `d1_boot_out` 1.3; z extent not measured (drawing: 1–3.9, `d1_btn` stays 4.5) | still 0.4 into the wall: window kept |
| S3 headers | female header body height | `s3_sock_h` 8.5 | **8.4** | male header (11.10 = 3.1 tail + 2.4 spacer + 5.6 pin) is not this one |
| S3 headers | plastic spacer of the male headers on the S3 | `s3_pin_base` 2.5 | **2.40** | |
| S3 carrier (pad perfboard) | thickness | `s3_carrier_t` 1.6 | **1.5** | S3 sits 0.1 closer to the lid |
| 18650 cells | length, Ø | `bat` [18.6, 65] | length **65** (= model); Ø **18.3** → keep 18.6 (0.3 extra play absorbs the printed-hole shrink) | ≤ 65.5 long or the cell won't go in |

## Power leg modules

| Part | Parameter | Current | Measured | Notes |
|---|---|---|---|---|
| TP4056 | board length, width | `charger` 28 × 17.1 | **28.7 × 17.15**, trimmed to **26.3** × 17.15 | 2026-10-27 re-measure (was 28 × 17.1 on 10-24). 27.2 with its micro-USB socket, **26.3 with the socket desoldered** (unused: charging goes through the separate micro-USB breakout on the IN pads). 28.7 = 27.2 + two panel-break nubs (~0.75 each end, no traces): file them off → fits the 27.2 interior with 0.45 side play: drop the side-wall grooves (`charger_groove`), plain lower ledges like the TPS63020; check `charger_lip` still clears the pads after trimming |
| TP4056 | IN-end pads distance from the board end | ≥ 0.65 assumed | pad **centre 1.43** from the edges that sit on the ledges (pad edge ~0.6) | see `charger_lip` |
| TP4056 | free edge under the side grooves | `charger_lip` 0.9 | 0.9 would run under the pads (edge ~0.6 from the board edge) | at merge: **`charger_lip` 0.5**, and the pads' underside joints kept flat |
| Micro-USB breakout | width (x), length (z), PCB | `usbb` [15, 13, 1.6] | **14.3 × 16 × 1.5** (x × z assumed) | receptacle at the bottom edge; top at z 18.6 + 0.3, under the bottom shelf (22) |
| Micro-USB breakout | plug overmold | ≤ 11.6 × 8 (floor opening) | **7.9 × 5.5** → fits (wide side along x); opening kept |  |
| MAX98357A amplifier | board width × length | `amp` [19.4, 18, 1.6] | **22.4 × 38.4** (2026-10-28) | **not merged into the model**: twice the modelled length; the width fits the 27.2 interior, its slot above the splint must be redesigned (branch + requirement) |
| Speaker | box width × height × thickness | `spk` [22, 10, 39] (22 × 39 × 10) | **66 × 30 × 17** (2026-10-28) | **not merged; does not fit**: 30 is wider than the middle column interior (27.2) and deeper than the space behind the splint (~26), 66 is longer than the lower black panel. Check whether 30 includes mounting ears; otherwise another speaker or another place (open question) |
| TPS63020 | width, depth, PCB | `bk` [26.2, 17.4, 1.6] | **[26.7, 17.7, 1.6]** | no model warning; only 0.25 side play in the 27.2 interior (printed walls shrink it): widen the slot into the walls at merge |
| TPS63020 | inductor height | `bk_h` 4 | | |
| TPS63020 | free edge under the grooves | `bk_lip` 0.9 | a pad pair at each corner: centres 1.3 and 4 from the side edge (nearest pad edge ~0.5) → 0.9 runs under them | decided: wire only the inner pad of each pair (centre 4 from the edge), the outer one stays bare (no solder underneath) → `bk_lip` 0.9 unchanged, full length |
| microSD reader | free edge under the grooves | `sd_lip` 1.2 | **1.0** (more room for the GND pad) | 0.8 min grip with the 0.2 groove play; socket check OK |
| Polyfuses | width, height, thickness | `fuse` [12, 14, 3.2] | **[15, 16, 2.5]**, marked XF160 (1.6 A hold / ~3.2 A trip: same rating as the MF-R160) | thinner: 2.1 under the DS3231 stop (OK). **Conflict**: 15 wide > 14.2 between the top-shelf screw posts (x 4.6 / 25.8, Ø7, row z 103) → model WARNING. **Proposal (2026-10-27)**: move each fuse off the top shelf, standing flat against the inner front wall in front of the cell, between the two cradles (free: y 1.6–9.9 = 8.3 deep, z 38.7–85.7 = 47 high, full width), high up (z ~68–85) so the B+ loop from the + tab stays short; two ribs + a dab of glue. Frees the top shelf and the DS3231 stop. **Validated** |
| Power-path perfboard | width, depth, thickness | `pp_b` [26.6, 20, 1.6] | thickness **1.5** (pad perfboard); size = cut to the plan | |
| Power-path perfboard | tallest part (D1 lying) | `pp_parts` 6 | D1 lying **5.2** → keep 6 (leads / solder above it) | |
| Stripboard P1 / P2 | thickness | `hub_b[2]` 1.6 | **1.61** → keep 1.6 | cut to 24 × 32 |

## Sensors, screens, connectors

| Part | Parameter | Current | Measured | Notes |
|---|---|---|---|---|
| AM312 | board mid-plane offset from the detector axis | `pir_pcb_dn` 1.85 | | |
| BME280 | width, length, PCB + can | `bme_b` [11.5, 15, 2.6] | **[12, 15.6, 2.6]** (PCB 1.62, 2.58 with the can) | header removed |
| BME280 | sensor can centre above board centre | `bme_port_dz` 0 | **0** (centred, 7.7 of 15.6) | |
| DS3231 (ZS-042) | right-angle header row depth in front of the board back | `rtc_hdr_y` 3 | **~4** (lid-side face → pin axis; standard right-angle header: plastic body then the bend) | |
| 1.3" screen | board, thickness, glass position (`active_dz`, `active_dx`), holes | `lcd130cs` module [27, 42], thickness 4 | board **27.35 × 42.12**, **3.3** with the protective film; 4 holes Ø2.54, centres ~1.7 from the long edges, **4.7** from the short edge on the pad side, **1.5** from the opposite one. Glass **27.35 × ~29.9**: flush with the long edges, 7.2 from the pad-side short edge, 5 from the other → glass centre 1.1 off the board centre, away from the pads → `active_dz` ≈ **−1.1** (pads at the top, active area assumed centred in the glass; check lit), `active_dx` 0 | holes asymmetric: not centred standoffs |
| 0.85" screen | glass position | — | | if used |
| Screens | back side parts | — | **3 high, from 8.7 below the pad row centre** | **No conflict** (dry fit 2026-10-27: right-angle header + female Dupont housings in place, clear of the parts). At merge: check the model's keep-out box against the parts so it does not flag a false clash; overall height PCB back → housing top **~6.9** (model box: ~3.9 incl. 1 mm key rib → raise to ~8 with the rib; check against the lid and parts behind the screens) |
| Screens | header pin row below the board top edge | `scr_hdr_dz` 2 | **1.4** (pad centre → short edge) | |
| C7 470 µF | Ø, length | `c7` [8, 12] | **8 × 11.5** → keep [8, 12] (margin) | |
| JST-XH | crimped male housing behind the shroud | `xh_male_back` 4 | **1.0** (male 8 overall − the model's 7 shroud) | plastic only; the wire bend is added separately in the keep-out boxes |
| JST-XH | XHP female: length, part outside the shroud once mated | `xh_female` [9.8, 4.3] | **[7, 1.7]** (female 7; mated 9.7 − male 8 = 1.7 out) | mated stack 1 + 7 + 1.7 = 9.7 = measured; 9.8 / 4.3 were datasheet guesses |
| Boards on the wall side | solder tails | ≤ 1 (`pcb_gap` 1.2) | | ADXL345, MAX98357A, micro-USB |
