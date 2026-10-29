# Platform Requirements

<!-- Requirements are added here during Phase 2 of the RBD workflow. -->
<!-- Format: req(ID): title -->

### PLAT-POWER-CHARGE-001

**Title:** Protected TP4056 module charged through a separate micro-USB breakout

**Status:** validated

**Dependencies:** [TECH-POWER-CELL-001](technical.md#tech-power-cell-001)

derives_from: [FUNC-POWER-CHARGE-001](functional.md#func-power-charge-001)

**Description:** The charger is one protected TP4056 module (U1, with DW01) lying flat in the left leg. Its own micro-USB is desoldered. A micro-USB breakout in the left foot, its receptacle facing backwards through an opening at the bottom of the leg's lid, feeds its IN+ / IN− pads (net VUSB). Acceptance: pytest on the schematic (the breakout's VBUS/GND are on U1 IN+/IN−; U1 OUT+ is the only charger output); bench: plugging into the breakout charges the cells.

### PLAT-POWER-CHARGE-002

**Title:** Charge current set to 0.5 A by R_PROG 2.4 kΩ

**Status:** validated

**Dependencies:** [PLAT-POWER-CHARGE-001](platform.md#plat-power-charge-001), [PERF-POWER-CHARGE-001](performance.md#perf-power-charge-001), [PERF-POWER-THERMAL-001](performance.md#perf-power-thermal-001)

derives_from: [TECH-POWER-CHARGE-001](technical.md#tech-power-charge-001)

**Description:** The TP4056 module's R_PROG (1.2 kΩ "122" from the factory) is replaced by 2.4 kΩ ("242"), which sets the charge current to 0.5 A. If E-M8 fails (wall > 45 °C), the fallback is 3.6 kΩ (0.33 A); D13 is decided after E-M8. Acceptance (bench): with the module unpowered, the fitted R_PROG is within ± 5 %; the charge current into a half-empty cell is 0.45–0.55 A (fallback 0.30–0.36 A); in open air, the TP4056 case is < 60 °C after 15 min.

### PLAT-POWER-HOTPLUG-001

**Title:** TVS D3 and capacitor C9 on the TP4056 input pads

**Status:** validated

**Dependencies:** [PLAT-POWER-CHARGE-001](platform.md#plat-power-charge-001)

derives_from: [TECH-POWER-HOTPLUG-001](technical.md#tech-power-hotplug-001)

**Description:** A unidirectional SMAJ5.0A TVS (D3) and a 22 µF electrolytic (C9) are soldered across the TP4056 IN+ / IN− pads, with D3's cathode band and C9's + on IN+. Acceptance: pytest on the schematic (D3 and C9 between VUSB and GND, with the right orientation); bench: VUSB unchanged, no heating, IN+ not shorted to IN−.

### PLAT-POWER-PROTECT-001

**Title:** The DW01 on the TP4056 module protects the pack

**Status:** draft

**Dependencies:** [PLAT-POWER-CHARGE-001](platform.md#plat-power-charge-001)

derives_from: [TECH-POWER-PROTECT-001](technical.md#tech-power-protect-001)

**Description:** The pack protection is the DW01 and its MOSFET pair on the TP4056 module, switching OUT−. Acceptance (bench, 3.7 V bench supply on B+/B−): OUT+ ≈ B+ and OUT− conducts to B−; when the supply is lowered, OUT− opens between 2.3 and 2.5 V; the module's quiescent current with USB out is < 10 µA (see [power_budget.md](../hardware/power_budget.md)). Pending: E-M5 (whether the DW01 switches on by itself when the cells are first connected) is still to record.

### PLAT-POWER-FUSE-001

**Title:** XF160 polyfuses F1 / F2 at each cell's + plate

**Status:** validated

**Dependencies:** [TECH-POWER-CELL-001](technical.md#tech-power-cell-001)

derives_from: [TECH-POWER-PROTECT-002](technical.md#tech-power-protect-002)

**Description:** Each cell's + lead goes through an XF160 polyfuse (1.6 A hold, ~3.2 A trip, 30 V): F1 in the left leg, F2 in the right leg. Each stands on the inner front wall in front of its cell, between the cradles, before the wire leaves the cell bay. Acceptance (bench): each fuse < 0.2 Ω cold; the drop across each fuse at a 1 A pack load is < 0.15 V; both branches read the same voltage.

### PLAT-POWER-PATH-001

**Title:** Power path Q1 / D1 / R1 on the power-path board

**Status:** validated

**Dependencies:** [PLAT-POWER-CHARGE-001](platform.md#plat-power-charge-001), [PERF-POWER-PATH-001](performance.md#perf-power-path-001)

derives_from: [FUNC-POWER-PATH-001](functional.md#func-power-path-001)

**Description:** The circuit is: a 1N5822 Schottky D1 from VUSB to VPATH; a logic-level P-MOSFET Q1 (AO3401A, D on OUT+, S on VPATH, G on VUSB); R1 4.7 kΩ from Q1's gate to GND, chosen so that a warm D1 leaking up to 50 µA still leaves the gate below 0.25 V (Q1 fully on, no leakage measurement needed); it also discharges VUSB twice as fast on unplugging. Acceptance: pytest on the schematic (these nets, Q1 and D1 the right way round); bench: VUSB < 0.5 V within 1 s of unplugging.

### PLAT-POWER-SWITCH-001

**Title:** Slide switch SW1 between VPATH and VSYS

**Status:** draft

**Dependencies:** [PLAT-POWER-PATH-001](platform.md#plat-power-path-001)

derives_from: [FUNC-POWER-SWITCH-001](functional.md#func-power-switch-001)

**Description:** SW1, a mini slide switch in the floor of the left leg, sits after the power-path merge (VPATH) and before VSYS. Its contacts are rated ≥ 1 A. Acceptance: pytest on the schematic (SW1 between VPATH and VSYS); bench: datasheet or marking ≥ 1 A; a temperature rise of ≤ 10 °C after 10 min at 1 A (3.9 Ω 5 W load). Pending: E-M6 (the actual rating of SW1) not checked yet.

### PLAT-POWER-REG-001

**Title:** TPS63020 module U9 makes the 3.3 V rail

**Status:** validated

**Dependencies:** [PERF-POWER-REG-001](performance.md#perf-power-reg-001)

derives_from: [TECH-POWER-REG-001](technical.md#tech-power-reg-001)

**Description:** A TPS63020 buck-boost module (U9, left leg) is fed from VSYS on its own pair, with EN tied to VIN (always on after SW1). Its output goes to P1 and then the S3 Mini's 3V3 pin. Acceptance (bench, nothing on the output): VOUT 3.3 V ± 3 % (never 5 V); input idle current < 0.1 mA (see [power_budget.md](../hardware/power_budget.md)). A few mA means it is stuck in PWM.

### PLAT-POWER-REG-002

**Title:** TPS63020 PS/SYNC tied to GND (power-save mode)

**Status:** validated

**Dependencies:** [PLAT-POWER-REG-001](platform.md#plat-power-reg-001)

derives_from: [TECH-POWER-REG-002](technical.md#tech-power-reg-002)

**Description:** The TPS63020's PS/SYNC pin is tied to GND (power-save mode) and is never pulled high: forced PWM could sink current from the 3.3 V rail when the S3's ME6211 LDO drives it too. Acceptance: pytest on the schematic (U9 PS on GND); bench continuity check from PS/SYNC to GND.

### PLAT-POWER-REG-003

**Title:** C1 220 µF low-ESR polymer capacitor at the S3 3V pin

**Status:** validated

**Dependencies:** [PLAT-POWER-REG-001](platform.md#plat-power-reg-001), [PERF-POWER-REG-002](performance.md#perf-power-reg-002)

derives_from: [TECH-POWER-REG-001](technical.md#tech-power-reg-001)

**Description:** C1, a 220 µF polymer tantalum (Panasonic 10TPE220ML, 10 V, ESR ≤ 25 mΩ), sits at the S3 Mini's 3V pin on the carrier, about 35 cm of wire away from the TPS63020, with + on 3V3. Acceptance: pytest on the schematic (C1 between +3V3 and GND at the S3); bench polarity check before the first power-up.

### PLAT-POWER-DIST-001

**Title:** MAX98357A fed from its own VSYS pair, with C7 470 µF (Panasonic EEUFC1A471, 470 µF, 10 V, low ESR)

**Status:** validated

**Dependencies:** [TECH-POWER-GROUND-001](technical.md#tech-power-ground-001)

derives_from: [TECH-POWER-DIST-001](technical.md#tech-power-dist-001)

**Description:** The MAX98357A's VIN / GND get their own twisted VSYS / GND pair from the star point, with C7 470 µF at VIN (+ on VIN). The amplifier's GND goes to system GND, never to B−. Acceptance: pytest on the schematic and harness (amplifier VIN on VSYS, GND on GND, C7 across them); bench: VIN = VSYS, C7 polarity checked.

### PLAT-POWER-MONITOR-001

**Title:** VBAT/2 divider R2 / R3 into GPIO1 (ADC1)

**Status:** validated

**Dependencies:** [CONF-POWER-ADCCAL-001](configuration.md#conf-power-adccal-001)

derives_from: [FUNC-POWER-MONITOR-001](functional.md#func-power-monitor-001)

**Description:** R2 / R3 (1 MΩ / 1 MΩ) divide the TP4056 B+ pad voltage. R2 is soldered in line in the harness at the B+ pad end, so the sense wire to the power-path board carries B+ only behind 1 MΩ; R3 sits on the power-path board. The midpoint (VBAT/2) goes to GPIO1, an ADC1 channel usable with Wi-Fi on. C6 100 nF ceramic (never tantalum) sits from GPIO1 to GND at the S3. Acceptance: pytest on the schematic (these values and nets); bench: VBAT/2 = B+ / 2 ± 2 % with the switch on, the switch off and the charger plugged in.

### PLAT-POWER-DETECT-001

**Title:** USB_DET divider R15 / R16 into GPIO21

**Status:** validated

**Dependencies:** [PLAT-POWER-PATH-001](platform.md#plat-power-path-001)

derives_from: [FUNC-POWER-DETECT-001](functional.md#func-power-detect-001)

**Description:** R15 68 kΩ from VUSB and R16 100 kΩ to GND make USB_DET, which goes to GPIO21, with C8 100 nF to GND at the S3. Acceptance: pytest on the schematic (these values and nets); bench: USB_DET is 2.8–3.3 V with the supply plugged in (never > 3.3 V) and < 0.2 V within 1 s of unplugging.

### PLAT-POWER-VSENSE-001

**Title:** VSYS sense: NPN level detector into GPIO37

**Status:** validated

**Dependencies:** [PLAT-POWER-SWITCH-001](platform.md#plat-power-switch-001), [TECH-POWER-BACKFEED-001](technical.md#tech-power-backfeed-001)

derives_from: [FUNC-POWER-VSENSE-001](functional.md#func-power-vsense-001)

**Description:** BC547: base from VSYS through 1 MΩ, 330 kΩ base to GND, emitter to GND, collector to GPIO37 with the internal pull-up enabled only while reading. Rail present = GPIO37 low, from a VSYS threshold of 2.3–2.7 V over the NPN's V_BE and gain spread (above the 2.5 V the amplifier needs, below the ~3.2 V minimum of the rail on battery); no voltage above 3V3 reaches the pin. Fitted: BC547B (Q4). R23 (VSYS side) is soldered in line in the harness at the power-path board end, so the wire through the left tube carries VSYS only behind 1 MΩ; R24 and Q4 stand on the S3 carrier, the base line reaching it through X14. Acceptance: pytest on the schematic; bench: GPIO37 low at VSYS 3.0 and 5.0 V, high at 0 V. Standing current ~3–4 µA: [power_budget.md](../hardware/power_budget.md).

### PLAT-POWER-VBUS-001

**Title:** S3 Mini VBUS contact removed from the carrier header

**Status:** draft

**Dependencies:** none

derives_from: [TECH-POWER-VBUS-001](technical.md#tech-power-vbus-001)

**Description:** The S3 Mini's VBUS pin reaches only its own USB-C connector: the matching contact is pulled out of the carrier's female header, so VBUS touches no carrier net. Acceptance: pytest on the schematic (S3 pin V is no-connect); bench: no continuity between the S3's VBUS pin and any carrier pad.

### PLAT-POWER-GATE-001

**Title:** Q5 switches the microSD 3V3 from SD_EN on GPIO36

**Status:** validated

**Dependencies:** [PLAT-POWER-REG-001](platform.md#plat-power-reg-001)

derives_from: [FUNC-POWER-GATE-001](functional.md#func-power-gate-001)

**Description:** Q5 (AO3401A, on the power-path board) switches +3V3 to SD_3V3 on the high side. Its gate is on SD_EN (GPIO36, low = card powered), and R22 100 kΩ pulls the gate up to 3V3 so the card stays off while the pin floats. Acceptance: pytest on the schematic (these nets); bench: SD_3V3 < 0.1 V with GPIO36 high and with the S3 held in reset.

### PLAT-POWER-SLEEP-001

**Title:** Battery-fed status LEDs removed

**Status:** validated

**Dependencies:** none

derives_from: [TECH-POWER-SLEEP-001](technical.md#tech-power-sleep-001)

**Description:** The power or status LEDs are removed from the ZS-042, the TPS63020 module, the GY-291 and the microSD breakout, and the S3 Mini's RGB LED (GPIO47) is removed too. The TP4056 charge LEDs stay (they run on USB power only). Acceptance: bench visual checklist, signed off in the bring-up notes, plus a deep-sleep current measurement ([PERF-POWER-SLEEP-001](performance.md#perf-power-sleep-001)).

### PLAT-POWER-SLEEP-002

**Title:** DS3231 32 kHz output disabled

**Status:** validated

**Dependencies:** none

derives_from: [TECH-POWER-SLEEP-001](technical.md#tech-power-sleep-001)

**Description:** At start-up the firmware clears the EN32kHz bit (bit 3) of the DS3231's control/status register 0x0F, and leaves the other bits unchanged. Acceptance (on-target Unity test): after initialisation, reading register 0x0F gives bit 3 = 0, and the other bits are the same as before.

### PLAT-MECH-CHARGEPORT-001

**Title:** Charge port at the heel of the left leg

**Status:** validated

**Dependencies:** [PLAT-POWER-CHARGE-001](platform.md#plat-power-charge-001)

derives_from: [FUNC-POWER-CHARGE-001](functional.md#func-power-charge-001)

**Description:** The micro-USB breakout stands against the outer side wall of the left foot, its receptacle axis horizontal along y. The receptacle mouth is at most 1 mm inside the back face, and its centre is ≥ 6 mm above the floor, so a plug overmold up to 11.6 × 8 mm clears both the table and the leg edges. The breakout is held so that the plug's insertion force (≤ 35 N, micro-USB spec) does not move it, and the lid can still be removed without unsoldering anything. The floor opening of the former port is closed. Acceptance: `make check` clean (geometry asserts in `tars4.scad` for the axis, mouth depth, height and clearances); print: a plug inserted and removed 10 times, with the breakout staying in place.

### PLAT-MECH-PIVOT-001

**Title:** Column pivot bores sized from tube_test3: teardrop bores, glued 8.00 / turning 8.05 for the 7.93 brass tube

**Status:** validated

**Dependencies:** none

**Description:** Each column joint turns on a brass tube (7.93 measured outer Ø), glued into one column and turning in the next. The pivot bores are horizontal when the columns print front face down, so they are teardrop-shaped (point toward the print top, self-supporting 45° ceiling, no support inside the bore). Drawn Ø: glued side 8.00 (tube held, no play), turning side 8.05 (turns, micro play only), from tube_test3 (2026-10-28, IBoss PLA Silk, 0.20 mm Ender3 profile). Tight beats loose: a bore that binds is sanded or reamed with an 8 mm drill. Acceptance: `make check` clean (no WARNING); `tube_od` = 7.93, `tube_glue_clr` = 0.07, `tube_run_clr` = 0.12; `pivot_cut` uses `xtear`; first printed joint: glued side holds, turning side turns without wobble.
