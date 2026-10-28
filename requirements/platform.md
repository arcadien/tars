# Platform Requirements

<!-- Requirements are added here during Phase 2 of the RBD workflow. -->
<!-- Format: req(ID): title -->

### PLAT-POWER-CHARGE-001
**Title:** Protected TP4056 module charged through a separate micro-USB breakout
**Status:** validated
**Dependencies:** [TECH-POWER-CELL-001](technical.md#tech-power-cell-001)
derives_from: [FUNC-POWER-CHARGE-001](functional.md#func-power-charge-001)
**Description:** The charger is one protected TP4056 module (U1, with DW01) lying flat in the left leg. Its own micro-USB is desoldered. A micro-USB breakout on the front wall of the left foot, reached through the floor opening, feeds its IN+ / IN− pads (net VUSB). Acceptance: pytest on the schematic (the breakout's VBUS/GND are on U1 IN+/IN−; U1 OUT+ is the only charger output); bench: plugging into the breakout charges the cells.


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
**Description:** The pack protection is the DW01 and its MOSFET pair on the TP4056 module, switching OUT−. Acceptance (bench, 3.7 V bench supply on B+/B−): OUT+ ≈ B+ and OUT− conducts to B−; when the supply is lowered, OUT− opens between 2.3 and 2.5 V; the module's quiescent current with USB out is < 10 µA (see [power_budget.md](../power_budget.md)). Pending: E-M5 (whether the DW01 switches on by itself when the cells are first connected) is still to record.


### PLAT-POWER-FUSE-001
**Title:** XF160 polyfuses F1 / F2 at each cell's + plate
**Status:** validated
**Dependencies:** [TECH-POWER-CELL-001](technical.md#tech-power-cell-001)
derives_from: [TECH-POWER-PROTECT-002](technical.md#tech-power-protect-002)
**Description:** Each cell's + lead goes through an XF160 polyfuse (1.6 A hold, ~3.2 A trip, 30 V): F1 in the left leg, F2 in the right leg. Each stands on the inner front wall in front of its cell, between the cradles, before the wire leaves the cell bay. Acceptance (bench): each fuse < 0.2 Ω cold; the drop across each fuse at a 1 A pack load is < 0.15 V; both branches read the same voltage.


### PLAT-POWER-PATH-001
**Title:** Power path Q1 / D1 / R1 on the power-path board
**Status:** draft
**Dependencies:** [PLAT-POWER-CHARGE-001](platform.md#plat-power-charge-001), [PERF-POWER-PATH-001](performance.md#perf-power-path-001)
derives_from: [FUNC-POWER-PATH-001](functional.md#func-power-path-001)
**Description:** The circuit is: a 1N5822 Schottky D1 from VUSB to VPATH; a logic-level P-MOSFET Q1 (AO3401A, D on OUT+, S on VPATH, G on VUSB); R1 10 kΩ from Q1's gate to GND. Acceptance: pytest on the schematic (these nets); bench: VUSB < 0.5 V within 1 s of unplugging; D1's reverse leakage at 4.2 V and 35 °C is ≤ 50 µA (otherwise R1 becomes 4.7 kΩ or D1 is replaced). Pending: E-M3 (D1 leakage) not measured yet.

