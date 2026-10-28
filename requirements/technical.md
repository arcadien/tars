# Technical Requirements

<!-- Requirements are added here during Phase 2 of the RBD workflow. -->
<!-- Format: req(ID): title -->

### TECH-POWER-CELL-001
**Title:** One 1S2P lithium-ion pack behind a single charger and protection circuit
**Status:** validated
**Dependencies:** none
**Description:** The battery is two 18650 lithium-ion cells in parallel (1S2P), connected to one charger and one protection circuit. Two chargers or two protection circuits in parallel are not allowed. Acceptance (pytest on kicad/tars4.kicad_sch): exactly one charger/protection module; both cell branches end on the same BAT+ net and the same B− net.

