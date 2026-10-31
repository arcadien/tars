# audit-lotE — stale documentation (audit 2026-10-29, lot E), stacked on audit-lot3

## Goal
Bring the docs in line with the repo (`audits/2026-10-29-audit-full.md`, lot E).

## State
- Done: README (left tube 14 wires / ~38 %, VSENSE_B colours, 112 wires, X1–X16, 5 Orca plates, Orca refresh by
  the pre-push hook / `make check-orca`, Validation section with hooks, CI and a model row, requirement domains,
  build4.sh options, XF160 in the BOM); CONTRIBUTING (hook stages, KiCad at every commit, STLs not in git, uv);
  open_questions (T1 settled, X14 JST-XH 4); shopping list (XF160 in stock); build4.sh cr10 echo; boards.py notes.
- Already right: lid speaker tabs (README consistent), power_budget VSENSE (no "draft").
- Left to mech-audio: the amplifier row of measurements.md and the clone in the shopping list (the clone and its slot
  live on that branch).
- Not pushed: GitHub SSH unreachable on 2026-10-31.

## Open questions
| # | Question | Answer |
|---|---|---|
| LE-1 | CLAUDE.md: drop "STLs are re-exported byte-different" and the `hardware/tars4_schematic.html` mention? | already gone from CLAUDE.md |
| LE-2 | tars4.scad:367 comment still says 13 / 19 / 6 wires: fold into the next mechanical commit? | |

## Next
Merge audit-lot3 first, then this branch (merge commits).
