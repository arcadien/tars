# Technical Requirements

<!-- Requirements are added here during Phase 2 of the RBD workflow. -->
<!-- Format: req(ID): title -->

### TECH-POWER-CELL-001
**Title:** One 1S2P lithium-ion pack behind a single charger and protection circuit
**Status:** validated
**Dependencies:** none
**Description:** The battery is two 18650 lithium-ion cells in parallel (1S2P), connected to one charger and one protection circuit. Two chargers or two protection circuits in parallel are not allowed. Acceptance (pytest on kicad/tars4.kicad_sch): exactly one charger/protection module; both cell branches end on the same BAT+ net and the same B− net.

### TECH-POWER-CELL-002
**Title:** Cells matched before they are put in parallel
**Status:** validated
**Dependencies:** [TECH-POWER-CELL-001](technical.md#tech-power-cell-001)
**Description:** The two cells are the same model and age, and each is charged on its own to the same voltage within ±0.05 V before they are first connected in parallel. Acceptance (bench record): both cell voltages, measured with a multimeter just before the first insertion, are logged in the bring-up notes and differ by ≤ 0.05 V.

### TECH-POWER-CHARGE-001
**Title:** Lithium-ion CC/CV charge with termination at 4.20 V
**Status:** validated
**Dependencies:** [TECH-POWER-CELL-001](technical.md#tech-power-cell-001)
**Description:** The charger charges at constant current and then at constant voltage, with a final voltage of 4.20 V ± 1 % (4.158–4.242 V) at the cell terminals, and stops on its own at the end of the charge. Acceptance (bench): from a half-empty cell, the charge ends with B+ between 4.158 and 4.242 V and the charge current falls to ≤ 10 % of the set current, then stops.

### TECH-POWER-PROTECT-001
**Title:** Hardware protection of the pack against over-discharge, overcharge and overcurrent
**Status:** validated
**Dependencies:** [TECH-POWER-CELL-001](technical.md#tech-power-cell-001)
**Description:** A hardware circuit, independent of the firmware, disconnects the pack on over-discharge (2.4 V ± 0.1 V), overcharge and overcurrent. It is a last resort: the firmware cut-off ([FUNC-POWER-CUTOFF-001](functional.md#func-power-cutoff-001)) is at least 0.8 V higher. Acceptance (bench, bench supply in place of the cells): lowering the supply opens the pack output between 2.3 and 2.5 V.

### TECH-POWER-PROTECT-002
**Title:** Resettable fuse on each cell branch
**Status:** validated
**Dependencies:** [TECH-POWER-CELL-001](technical.md#tech-power-cell-001)
**Description:** The pack protection circuit only guards the pack's negative output, not a short in the cell wires that run through the rotating pivot tubes. So each cell's positive lead carries its own resettable fuse, placed next to the cell's + contact. Acceptance: pytest on the schematic (one polyfuse in series between each cell + and BAT+); visual check that each fuse sits in the cell bay.

### TECH-POWER-HOTPLUG-001
**Title:** Charger input protected against hot-plug overshoot
**Status:** validated
**Dependencies:** [FUNC-POWER-CHARGE-001](functional.md#func-power-charge-001)
**Description:** Hot-plugging the external supply through the ~16 cm of wire from the charge port must not overshoot the charger's input. Acceptance (bench, scope at the charger IN pads, 10 hot-plugs of a 5 V ≥ 2 A supply): the peak voltage stays ≤ 7.0 V.

### TECH-POWER-VBUS-001
**Title:** The programming port never powers the system rail or the battery
**Status:** draft
**Dependencies:** none
**Description:** A USB host on the controller's programming port powers only the controller, never the system rail or the battery, and flashing works with the power switch on or off. Acceptance (bench): cells out, switch on, no external supply, host on → system rail < 0.1 V; on battery, host off and cable still in → current from the cells into the host's VBUS ≤ 1 mA; flashing succeeds with the switch in both positions. Pending: the ≤ 1 mA back-leak limit is provisional until measured.

### TECH-POWER-BACKFEED-001
**Title:** Outputs to rail-powered peripherals stay low until the system rail is present
**Status:** validated
**Dependencies:** [FUNC-POWER-VSENSE-001](functional.md#func-power-vsense-001)
**Description:** From reset, the amplifier enable, the amplifier's I2S lines and the backlight enable stay low or idle until [FUNC-POWER-VSENSE-001](functional.md#func-power-vsense-001) reports the system rail present. This stops a peripheral on an unpowered rail from being back-powered through its input pins (e.g. switch off, controller on a PC). If the rail disappears they are driven low again within 100 ms. Acceptance (on-target Unity test, rail sense injected or toggled with the switch): pins low with the rail absent; released only with the rail present; low within 100 ms of the rail dropping.

### TECH-POWER-GROUND-001
**Title:** Star ground on the pack output
**Status:** validated
**Dependencies:** [TECH-POWER-PROTECT-001](technical.md#tech-power-protect-001)
**Description:** All power returns meet at one star point on the protected pack output (system GND). No load returns to the raw cell negative (B−), because the protection switches sit between B− and GND. Acceptance: pytest on the schematic (no load ground pin on the B− net); bench: B−, pack OUT−, the regulator GND and the amplifier GND are each < 0.1 Ω from the star point, with the protection switched on.

### TECH-POWER-DIST-001
**Title:** Separate supply pairs for the 3.3 V regulator and the audio amplifier
**Status:** validated
**Dependencies:** [TECH-POWER-GROUND-001](technical.md#tech-power-ground-001)
**Description:** The 3.3 V regulator and the audio amplifier each get their own system-rail/GND wire pair from the star point, so that amplifier current peaks do not flow through the controller's supply wires. The logic GND leaves from the regulator's GND pad, next to its 3.3 V wire. Acceptance: pytest on the harness wire list (tools/harness.py) and the schematic: two distinct VSYS/GND pairs start at the star; the 3V3 pair starts at the regulator.

### TECH-POWER-REG-001
**Title:** A single 3.3 V logic rail from a buck-boost converter
**Status:** validated
**Dependencies:** none
**Description:** All 3.3 V loads (controller, screens, sensors, storage card) are fed by one regulated rail, made from the system rail by a buck-boost converter that regulates whether the input is above or below 3.3 V (2.5 V cells up to the ~4.7 V of the external supply). No linear regulator is fed from the system rail. Acceptance: pytest on the schematic (every 3V3 load pin is on the +3V3 net; one regulator sourcing it, input on VSYS).

### TECH-POWER-REG-002
**Title:** The 3.3 V rail tolerates a second source from the controller's LDO
**Status:** validated
**Dependencies:** [TECH-POWER-REG-001](technical.md#tech-power-reg-001), [TECH-POWER-VBUS-001](technical.md#tech-power-vbus-001)
**Description:** When a host is plugged into the programming port, the controller's on-board LDO also drives the 3.3 V rail. The main regulator must then not sink current from the rail into the system rail. Acceptance (bench): switch on, on battery, host plugged in with the controller idle: the main regulator's input current stays ≥ 0, and the 3.3 V rail stays within [PERF-POWER-REG-001](performance.md#perf-power-reg-001).

### TECH-POWER-SLEEP-001
**Title:** No always-on indicator loads on battery-fed rails
**Status:** validated
**Dependencies:** [PERF-POWER-SLEEP-001](performance.md#perf-power-sleep-001)
**Description:** No status LED or free-running clock output that draws current permanently is fed from the battery or from rails fed by the battery. LEDs fed only from the external supply (charger status) are allowed. Acceptance: visual inspection against the bring-up checklist, plus the deep-sleep current of [PERF-POWER-SLEEP-001](performance.md#perf-power-sleep-001).

### TECH-BUILD-ARTIFACTS-001
**Title:** Print files are generated from the model, not versioned
**Status:** validated
**Dependencies:** none
**Description:** The STL parts (`mechanical/stl/`) and the raw plates (`mechanical/3mf/tars4_plate*.3mf`) are build outputs of `mechanical/scad/tars4.scad`: git ignores them, and they are regenerated on demand before a print (`make check-stl`, `tools/build4.sh 3mf`). The hand-arranged Orca projects (`mechanical/3mf/tars4.3mf`, `tars4_cr10.3mf`), the renders and the wiring / harness / schematic documents stay versioned. The OpenSCAD version used for the exports is pinned, in [CONTRIBUTING.md](../CONTRIBUTING.md) and in CI. Acceptance: `git ls-files mechanical/stl 'mechanical/3mf/tars4_plate*'` is empty and both paths are in `.gitignore`; on a fresh clone, `make check-stl` produces every part listed in `tools/build4.sh` with no OpenSCAD WARNING and every plate on its bed.

