# Branch fix-audit — fixes from the 2026-10-28 repo audit

Branch state file (CLAUDE.md, *Branches*): read it first when the branch is picked up again, keep it
current, answer the questions here.

## Goal
Fix the audit findings 1–3 and 5–10 (one commit each); finding 4 (pytest acceptance tests for the 17 requirements
that announce them) is planned with Aurelien afterwards.

## State (2026-10-28)
- Branch opened from main.

## Findings
1. CR-10 bed fit never checked · 2. harness.py silently uses a stale geometry cache · 3. check.sh stage inputs miss
files (kicad_sch_gen.py, connectors.scad) · 5. pose scene copies model dimensions · 6. KiCad / Ghostscript only found
at the Linux AppImage paths · 7. harness PDF byte-different on every run · 8. render errors discarded · 9. hooks check
the working tree, not what is pushed · 10. KiCad backup zip and local .kicad_prl versioned.

## Open questions
| # | Question | Answer |
|---|---|---|

## Next
Commits 1, 2, 3, 5–10, then PR.
