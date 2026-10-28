# Functional Requirements

<!-- Requirements are added here during Phase 2 of the RBD workflow. -->
<!-- Format: req(ID): title -->

### FUNC-POWER-CHARGE-001
**Title:** Battery charges from an external 5 V USB supply
**Status:** validated
**Dependencies:** [TECH-POWER-CHARGE-001](technical.md#tech-power-charge-001)
**Description:** When a 5 V USB supply is connected to the robot's charge port, the battery charges and the charge stops by itself when the battery is full ([TECH-POWER-CHARGE-001](technical.md#tech-power-charge-001)). The charge port can be reached from underneath the robot without opening any lid. Acceptance (bench): with a partly discharged battery, connecting the supply makes current flow into the battery (multimeter in series with B+) and the battery voltage rises; no lid is removed to plug the supply in.


### FUNC-POWER-PATH-001
**Title:** On an external supply, the system load does not draw from the battery
**Status:** validated
**Dependencies:** [FUNC-POWER-CHARGE-001](functional.md#func-power-charge-001), [TECH-POWER-CHARGE-001](technical.md#tech-power-charge-001)
**Description:** While an external supply is connected, the system rail is fed from that supply, not from the battery, so the charger only sees battery current and ends the charge normally while the robot runs. Acceptance (bench): with the supply connected and a 110 mA load (33 Ω) on the system rail, the battery-terminal current never flows out of the battery (≥ −0.1 mA), and a full charge ends as specified by [TECH-POWER-CHARGE-001](technical.md#tech-power-charge-001).


### FUNC-POWER-PATH-002
**Title:** Connecting or disconnecting the external supply does not reset the robot
**Status:** validated
**Dependencies:** [FUNC-POWER-PATH-001](functional.md#func-power-path-001)
**Description:** Plugging in or unplugging the external supply while the robot runs on a charged battery must not reset the controller. Acceptance: (a) bench: across 20 plug/unplug cycles at a 110 mA load and 20 at a 1 A load, the system rail never drops below 3.0 V (multimeter min-hold or scope); (b) on-target Unity test: after the same cycles a boot counter kept in RTC memory has not changed and the reset reason is never brown-out or power-on.

