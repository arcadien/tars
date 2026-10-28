# Performance Requirements

<!-- Requirements are added here during Phase 2 of the RBD workflow. -->
<!-- Format: req(ID): title -->

### PERF-POWER-REG-001
**Title:** 3.3 V rail static regulation
**Status:** validated
**Dependencies:** [TECH-POWER-REG-001](technical.md#tech-power-reg-001)
**Description:** The 3.3 V rail stays at 3.30 V ± 3 % (3.20–3.40 V) for loads from 0 to 500 mA and system-rail inputs from 3.0 V to 5.0 V. Acceptance (bench, multimeter at the regulator output): at 0 mA, 100 mA (33 Ω) and ~500 mA (6.8 Ω), input swept 3.0 → 4.2 V and set to 5.0 V, every reading is within 3.20–3.40 V.


### PERF-POWER-REG-002
**Title:** 3.3 V rail under load transients
**Status:** validated
**Dependencies:** [PERF-POWER-REG-001](performance.md#perf-power-reg-001), [TECH-POWER-DIST-001](technical.md#tech-power-dist-001)
**Description:** At the controller's 3.3 V pin, the rail stays ≥ 3.10 V during Wi-Fi transmit bursts and during full-volume audio playback, with the battery at 3.4 V. Acceptance (bench, scope at the controller 3V3 pin, firmware sending continuous Wi-Fi TX and playing a full-scale tone at the same time for 60 s): minimum ≥ 3.10 V and no controller reset.


### PERF-POWER-PATH-001
**Title:** Power-path voltage drop
**Status:** validated
**Dependencies:** [FUNC-POWER-PATH-001](functional.md#func-power-path-001)
**Description:** At a 110 mA system load, the system rail is within 0.10 V of the battery voltage on battery, and within 0.50 V of the external-supply voltage on the external supply. Acceptance (bench, multimeter, 33 Ω load, switch on): both drops are measured and within limits; a 0.5–0.7 V drop on battery fails.


### PERF-POWER-CHARGE-001
**Title:** Full charge time
**Status:** validated
**Dependencies:** [FUNC-POWER-CHARGE-001](functional.md#func-power-charge-001)
**Description:** A full charge of the pack, from the 3.30 V cut-off to the end of charge, with the robot switched off, takes ≤ 12 h at the 0.5 A charge current, or ≤ 16 h if the 0.33 A fallback (R_PROG 3.6 kΩ) is used. The choice between them (and D13) is made after E-M8. Acceptance (bench): timed charge of the assembled pack from 3.30 V (rested) to end of charge, against the limit for the current fitted.

