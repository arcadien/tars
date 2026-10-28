# Functional Requirements

<!-- Requirements are added here during Phase 2 of the RBD workflow. -->
<!-- Format: req(ID): title -->

### FUNC-POWER-CHARGE-001
**Title:** Battery charges from an external 5 V USB supply
**Status:** validated
**Dependencies:** [TECH-POWER-CHARGE-001](technical.md#tech-power-charge-001)
**Description:** When a 5 V USB supply is connected to the robot's charge port, the battery charges and the charge stops by itself when the battery is full ([TECH-POWER-CHARGE-001](technical.md#tech-power-charge-001)). The charge port can be reached from underneath the robot without opening any lid. Acceptance (bench): with a partly discharged battery, connecting the supply makes current flow into the battery (multimeter in series with B+) and the battery voltage rises; no lid is removed to plug the supply in.

