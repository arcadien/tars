# audit-lotD — requirements coherence (audit 2026-10-29, lot D), stacked on audit-lotE

## Goal
Fix lot D of `audits/2026-10-29-audit-full.md` (D4, D7 belong to mech-audio).

## State
- Done (validated 2026-10-31): D1 (cycles FUNC/TECH ↔ PERF removed), D2 (validated requirements no longer depend
  on drafts; PLAT-POWER-DETECT-001 → PLAT-POWER-PATH-001 already fine), D3 (FUNC-MECH-JOINT-001, parent of
  PLAT-MECH-PIVOT-001, manual sheet), D5 (full = 20 mV below the peak ≥ 4.10 V), D6 (half-open hunger bands),
  D8 (runtime on 2 × ≥ 2500 mAh, kept at ≥ 20 h: the bench decides; sleep docs aligned on ≤ 0.65 mA), D9 (backfeed
  gated on GPIO37 in README / bring-up), D10 (VBAT/2 and VSENSE_B in grey 30 AWG, no ring).
- Pushed 2026-11-01 (the 2026-10-31 failure was Pageant without the key, not the network). PR #18, stacked on #17.

- Requirements slimmed (2026-11-05, user: principle in requirements, values in a log): CONF-POWER-THRESH-001
  (defaults → design_notes.md *Battery thresholds*), FUNC-POWER-MONITOR-002 and FUNC-POWER-CUTOFF-002 (bounds from
  CONF, no duplicated values), PLAT-POWER-CHARGE-002 (R_PROG value and fallback → measurements.md / open_questions.md).
  Done here, not on a new branch: this branch had rewritten three of them (no clash; mech-collar-bore merges it).
  Then PLAT-POWER-PATH-001, -VSENSE-001, -REG-003, -MONITOR-001: rationale / placement left to design_notes.md
  (*Parts*), acceptance unchanged; the B+ / VSYS-only-behind-1 MΩ wires stay as a safety property.

## Open questions
| # | Question | Answer |
|---|---|---|
| LD-1 | CLAUDE.md colour table: add `grey | analog sense (VBAT/2, VSENSE_B)` and drop VBAT/2 from brown? | Yes, done |

## Next
Merge order: audit-lot3, audit-lotE, audit-lotD (merge commits). Then mech-audio (A3, D4, D7, the amplifier rows).
