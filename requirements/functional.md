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


### FUNC-POWER-SWITCH-001
**Title:** The power switch turns the robot off
**Status:** validated
**Dependencies:** [TECH-POWER-VBUS-001](technical.md#tech-power-vbus-001)
**Description:** A user-operated switch disconnects the system rail from both the battery and the external supply. Acceptance (bench): with the switch off, the system rail reads < 0.1 V both on battery alone and with the external supply connected. Exception: a host plugged into the programming port powers the controller only ([TECH-POWER-VBUS-001](technical.md#tech-power-vbus-001)).


### FUNC-POWER-SWITCH-002
**Title:** Charging works with the power switch off
**Status:** validated
**Dependencies:** [FUNC-POWER-CHARGE-001](functional.md#func-power-charge-001), [FUNC-POWER-SWITCH-001](functional.md#func-power-switch-001)
**Description:** The robot recharges when plugged in, whether it is switched on or off: switching it off neither stops nor slows the charge, and while it is on, its own consumption is taken from the external supply, not from the charge. Acceptance (bench, same partly discharged battery): the current flowing into the battery with the robot switched off and with it switched on and idle differ by no more than 10 %.


### FUNC-POWER-MONITOR-001
**Title:** Firmware measures the battery voltage
**Status:** validated
**Dependencies:** [PERF-POWER-MONITOR-001](performance.md#perf-power-monitor-001)
**Description:** The firmware measures the voltage at the battery terminals (not the system rail), both on battery and with the external supply connected. Acceptance (on-target Unity test + multimeter): on battery and on the external supply, the value the firmware reports is the B+ voltage within the accuracy of [PERF-POWER-MONITOR-001](performance.md#perf-power-monitor-001); on the external supply it does not follow the system rail (~4.7 V).


### FUNC-POWER-MONITOR-002
**Title:** Battery level classification ("hunger")
**Status:** validated
**Dependencies:** [FUNC-POWER-MONITOR-001](functional.md#func-power-monitor-001), [CONF-POWER-THRESH-001](configuration.md#conf-power-thresh-001)
**Description:** On battery, the firmware averages the battery voltage over a 60 s sliding window and classifies it as: fed (≥ 3.90 V), peckish (3.70–3.90 V), hungry (3.50–3.70 V), starving (3.30–3.50 V), empty (≤ 3.30 V). The 60 s average is the only hysteresis: there is no extra band, so one sample (a Wi-Fi or amplifier peak) cannot change the level. Acceptance (native Unity test with injected samples): each band gives its level at the boundaries; a 2 s dip of 0.3 V inside a stable window does not change the level.


### FUNC-POWER-MONITOR-003
**Title:** Charging and full states replace the level on an external supply
**Status:** validated
**Dependencies:** [FUNC-POWER-DETECT-001](functional.md#func-power-detect-001), [FUNC-POWER-MONITOR-001](functional.md#func-power-monitor-001)
**Description:** While the external supply is present, the firmware reports the battery state as "charging" instead of a level, then "full" once the charge has ended. The end of charge is inferred from the battery voltage alone; the charger's status output is not wired. Acceptance (native Unity test, injected supply flag and voltages): supply present and rising → charging; supply present and the voltage relaxed to ≤ 4.17 V after reaching ≥ 4.19 V → full; supply removed → back to the [FUNC-POWER-MONITOR-002](functional.md#func-power-monitor-002) level.


### FUNC-POWER-DETECT-001
**Title:** Firmware detects the external supply
**Status:** validated
**Dependencies:** none
**Description:** The firmware knows whether an external supply is connected to the charge port, whatever the battery state. Acceptance (on-target Unity test, supply plugged and unplugged 10 times): the detection flag becomes true within 1 s of plugging in and false within 1 s of unplugging.


### FUNC-POWER-DETECT-002
**Title:** Connecting the external supply wakes the robot
**Status:** validated
**Dependencies:** [FUNC-POWER-DETECT-001](functional.md#func-power-detect-001), [FUNC-POWER-SWITCH-001](functional.md#func-power-switch-001)
**Description:** With the power switch on, connecting the external supply wakes the controller from deep sleep, including after a low-battery shutdown ([FUNC-POWER-CUTOFF-002](functional.md#func-power-cutoff-002)). With the switch off, plugging in only charges the battery ([FUNC-POWER-SWITCH-002](functional.md#func-power-switch-002)): the robot stays off. Acceptance (on-target, bench): switch on, controller in deep sleep, supply unplugged: plugging it in wakes the controller within 1 s and the wake cause reported is the supply-detect source; switch off: plugging it in leaves the controller unpowered (system rail < 0.1 V).


### FUNC-POWER-VSENSE-001
**Title:** Firmware detects that the system rail is powered
**Status:** validated
**Dependencies:** none
**Description:** The firmware knows whether the system rail (after the power switch) is powered, independently of the battery voltage and of the external supply. This covers the case "switch off, controller powered from the programming port". Acceptance (on-target Unity test, bench supply on the system rail): the flag is true for 3.0–5.0 V, false below 1.0 V, and it follows a switch toggle within 100 ms.


### FUNC-POWER-CUTOFF-001
**Title:** Low-battery shutdown
**Status:** validated
**Dependencies:** [FUNC-POWER-MONITOR-002](functional.md#func-power-monitor-002), [FUNC-POWER-DETECT-001](functional.md#func-power-detect-001), [CONF-POWER-THRESH-001](configuration.md#conf-power-thresh-001)
**Description:** When the averaged battery voltage reaches the empty level (≤ 3.30 V) and no external supply is present, the firmware puts the robot into deep sleep. No shutdown happens while the external supply is present, nor when the battery reading is < 2.50 V (no cells: controller powered from the programming port). Acceptance (native Unity test): empty without supply → shutdown requested; empty with supply → none; reading 2.4 V → none.


### FUNC-POWER-CUTOFF-002
**Title:** An empty battery stays asleep until it is charging and above 3.5 V
**Status:** validated
**Dependencies:** [FUNC-POWER-CUTOFF-001](functional.md#func-power-cutoff-001), [FUNC-POWER-DETECT-002](functional.md#func-power-detect-002)
**Description:** After a low-battery shutdown, the firmware records an "empty" state that survives deep sleep. While it is set, every wake returns to deep sleep without turning on the screens, the amplifier or the radio. It is cleared only when the external supply is present and the battery is above 3.50 V. While the supply is present, the controller wakes on a timer every re-check interval ([CONF-POWER-THRESH-001](configuration.md#conf-power-thresh-001)) to test this; on battery alone no timer wake is armed, so an empty battery is not drained further. Acceptance (on-target Unity test): with the state set, a wake goes back to sleep within 200 ms with the enables low; supply present: the next timer wake comes after the re-check interval ±10 %; supply absent: no timer wake within 2 intervals; supply + 3.4 V keeps the state set; supply + 3.6 V clears it.


### FUNC-POWER-GATE-001
**Title:** Firmware can cut the supply of the removable storage card
**Status:** validated
**Dependencies:** none
**Description:** The removable storage card's supply is switched by the firmware and is off while the controller is in reset or has not yet driven the switch. Before cutting it, the firmware stops driving the card's signal lines. Acceptance: bench: card supply < 0.1 V when commanded off and while the controller is held in reset; on-target Unity test: the card signal pins are inputs whenever the supply is commanded off.
