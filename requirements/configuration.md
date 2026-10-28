# Configuration Requirements

<!-- Requirements are added here during Phase 2 of the RBD workflow. -->
<!-- Format: req(ID): title -->

### CONF-POWER-THRESH-001
**Title:** Battery thresholds are configuration values
**Status:** validated
**Dependencies:** none
**Description:** The battery thresholds are configuration constants defined in one place, with these defaults: level bounds 3.90 / 3.70 / 3.50 V, cut-off 3.30 V, no-battery limit 2.50 V, averaging window 60 s, charge-full relaxation 4.19 → 4.17 V, empty-lockout release 3.50 V, lockout re-check interval 10 min. The values measured on the bench must be settable without touching the logic. Acceptance (native Unity test): the logic reads the constants; overriding one at build time moves the matching boundary.

