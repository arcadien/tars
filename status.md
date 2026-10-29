# Branch audit-lot2 — audit lot 2: bench sheets and tests that measure the wrong thing

Branch state file (CLAUDE.md, *Branches*): read it first when the branch is picked up again, keep it
current, answer the questions here. Based on `power-safety` (PR #13, audit lot 1): merge main in once #13 is merged.
Audit report: `audits/2026-10-29-audit-full.md` (untracked, in the main worktree), section B and A1.

## Done (2026-10-29)
- B10: coverage test — a pytest named in an acceptance is never deferred as "firmware pending".
- B11: TECH-POWER-REG-001 test whitelists the two indirect 3V3 feeds (Q5 → microSD, R21 → PIR); mutation-checked.
- FUNC-POWER-GATE-001: new bench sheet (card supply off in reset: no firmware needed; commanded off: firmware).
- B1 / B8: loads re-rated (3.9 Ω ≥ 10 W on battery, 4.7 Ω ≥ 10 W ≈ 1 A on mains; 6.8 Ω ≥ 5 W on VSYS for the
  charge-time discharge, start = rested B+ after the loaded cut-off).
- B2: bring-up 3.2 1 A check with the bench supply limit at 1.5 A (the lab supply gives 5 A).
- B3: scope with a normal falling-edge trigger instead of min-hold (FUNC-POWER-PATH-002, PERF-POWER-REG-002).
- B4: 10 A socket stated in every series charge-current measurement.
- B5: bring-up VBAT/2 expected 0.476 × B+ with a 10 MΩ meter.
- B7: TPS63020 idle test powered up on the A range, LEDs removed first (bring-up order swapped).

## To do
- B6: write tests/bench/TECH-POWER-GROUND-001.md (bring-up 3.4 already links it): mV drop from B−, OUT−, TPS GND,
  amp GND to the star at a 1 A load, < 100 mV (= < 0.1 Ω), protection on.
- A1: FUNC-POWER-PATH-001 acceptance cannot fail (charge current masks a 110 mA draw). Proposed: full cell, charge
  terminated, meter on mA: any load draw reads negative (≥ −0.1 mA); or |ΔI_cell| ≤ 1 mA with the 33 Ω load on / off
  while charging. Requirement change → Aurelien validates, then rewrite tests/bench/FUNC-POWER-PATH-001.md.
- B9: TECH-POWER-PROTECT-001 names overcharge / overcurrent but tests over-discharge only. Proposed: add an
  overcurrent check (bench supply up to 5 A, ~3 A pulse on OUT) or narrow the title. Requirement change → validate.
- Then: make check, PR. Next lots: C (tooling), D (requirements coherence), E (docs); A3 (4 Ω speaker, SW1 ≥ 2 A,
  volume cap at 2 W / 4.7 V, X6 JST-XH 2 or Dupont) in branch mech-audio.

## Open questions
| # | Question | Answer |
|---|---|---|
| L1 | A1: which acceptance for FUNC-POWER-PATH-001? | |
| L2 | B9: add an overcurrent test or narrow the PROTECT-001 title? | |
