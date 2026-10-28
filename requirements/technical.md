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

