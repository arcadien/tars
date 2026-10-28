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

### PERF-POWER-THERMAL-001
**Title:** Leg wall temperature while charging
**Status:** validated
**Dependencies:** [FUNC-POWER-CHARGE-001](functional.md#func-power-charge-001), [FUNC-POWER-PATH-001](functional.md#func-power-path-001)
**Description:** While charging at the maximum charge current, the outer wall of the PLA leg next to the charger stays ≤ 45 °C (PLA softens at ~55–60 °C). Lids are closed and the ambient is 20–25 °C. Two cases: robot off, and robot running at a 1 A load on the external supply. Acceptance (bench, thermocouple or IR thermometer on the wall, at 15 min and at 30 min): every reading ≤ 45 °C.

### PERF-POWER-MAINS-001
**Title:** External supply voltage under the maximum combined load
**Status:** validated
**Dependencies:** [FUNC-POWER-PATH-001](functional.md#func-power-path-001)
**Description:** With a 5 V ≥ 2 A supply, the battery charging at maximum current and a 1 A system load, the voltage at the charger input stays ≥ 4.60 V for 30 min. Acceptance (bench, multimeter at the charger IN pads, readings every 5 min).

### PERF-POWER-MONITOR-001
**Title:** Battery voltage measurement accuracy
**Status:** draft
**Dependencies:** [FUNC-POWER-MONITOR-001](functional.md#func-power-monitor-001), [CONF-POWER-ADCCAL-001](configuration.md#conf-power-adccal-001)
**Description:** After calibration ([CONF-POWER-ADCCAL-001](configuration.md#conf-power-adccal-001)), the battery voltage reported by the firmware is within ±3 % of a multimeter reading at B+ over 3.0–4.2 V. Pending: the ADC calibration has not been done yet. Acceptance (on-target Unity test plus a multimeter; bench supply in place of the cells at 3.0, 3.3, 3.7 and 4.2 V; the value is the mean of 16 samples).

### PERF-POWER-SLEEP-001
**Title:** Deep-sleep current from the battery
**Status:** draft
**Dependencies:** [TECH-POWER-SLEEP-001](technical.md#tech-power-sleep-001), [FUNC-POWER-GATE-001](functional.md#func-power-gate-001)
**Description:** In deep sleep, with every wake source armed and the storage card supply cut, the robot draws ≤ 0.65 mA from the battery (breakdown per module: [power_budget.md](../power_budget.md)). With ~5–10 % of capacity left after the cut-off, this keeps the pack above the protection's 2.4 V threshold for weeks. Provisional limit: to be tightened once E-M7 has been measured. Acceptance (bench, µA-range meter in series with B+, value logged 60 s after the controller has gone to sleep).

### PERF-POWER-OFF-001
**Title:** Battery drain with the switch off
**Status:** draft
**Dependencies:** [FUNC-POWER-SWITCH-001](functional.md#func-power-switch-001)
**Description:** With the power switch off and no external supply, the battery drain is ≤ 60 µA: charger and protection quiescent current, the battery divider and power-path diode leakage (breakdown: [power_budget.md](../power_budget.md)). Pending: the limit depends on E-M3 (D1 leakage), not measured yet. Acceptance (bench, µA meter in series with B+, at room temperature and at 35 °C, a hot room: D1 only blocks on battery, when the charger is off and does not heat the leg).

### PERF-POWER-RUNTIME-001
**Title:** Runtime on a full charge
**Status:** validated
**Dependencies:** [PERF-POWER-CHARGE-001](performance.md#perf-power-charge-001)
**Description:** From a full charge to the low-battery shutdown, the robot runs ≥ 20 h under the reference profile: Wi-Fi connected and idle, both screens at full backlight, no audio. The expected average current per module is in [power_budget.md](../power_budget.md). Acceptance (bench run with the reference firmware profile, start and shutdown times logged; on-target the firmware logs the time of the shutdown).
