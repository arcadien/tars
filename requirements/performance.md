# Performance Requirements

<!-- Requirements are added here during Phase 2 of the RBD workflow. -->
<!-- Format: req(ID): title -->

### PERF-POWER-REG-001
**Title:** 3.3 V rail static regulation
**Status:** validated
**Dependencies:** [TECH-POWER-REG-001](technical.md#tech-power-reg-001)
**Description:** The 3.3 V rail stays at 3.30 V ± 3 % (3.20–3.40 V) for loads from 0 to 500 mA and system-rail inputs from 3.0 V to 5.0 V. Acceptance (bench, multimeter at the regulator output): at 0 mA, 100 mA (33 Ω) and ~500 mA (6.8 Ω), input swept 3.0 → 4.2 V and set to 5.0 V, every reading is within 3.20–3.40 V.

