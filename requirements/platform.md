# Platform Requirements

<!-- Requirements are added here during Phase 2 of the RBD workflow. -->
<!-- Format: req(ID): title -->

### PLAT-POWER-CHARGE-001
**Title:** Protected TP4056 module charged through a separate micro-USB breakout
**Status:** validated
**Dependencies:** [TECH-POWER-CELL-001](technical.md#tech-power-cell-001)
derives_from: [FUNC-POWER-CHARGE-001](functional.md#func-power-charge-001)
**Description:** The charger is one protected TP4056 module (U1, with DW01) lying flat in the left leg. Its own micro-USB is desoldered. A micro-USB breakout on the front wall of the left foot, reached through the floor opening, feeds its IN+ / IN− pads (net VUSB). Acceptance: pytest on the schematic (the breakout's VBUS/GND are on U1 IN+/IN−; U1 OUT+ is the only charger output); bench: plugging into the breakout charges the cells.

