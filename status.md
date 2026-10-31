# audit-lot3 — build pipeline (audit 2026-10-29, lot C)

## Goal
Fix the build-pipeline findings C1–C10 of `audits/2026-10-29-audit-full.md`, one commit each.

## State
- Done: C1 (stl digest includes its STLs), C2 (erc regenerates the schematic, generator fails on mismatch / no KiCad,
  exports the PDF), C3 (CI diffs the SVG / HTML outputs), C4 (hooks compare content hashes; pre-commit refuses unstaged
  check inputs: partial commits go through `git stash push --keep-index`), C5 (meshes fails on an object without STL),
  C6 (section drawings removed), C7 (harness PDF through Ghostscript only, deterministic), C8 (pre-push checks commit
  prefixes and IDs), C9 (erc inputs: firmware sources, .gitignore), C10 (one part <-> STL mapping and STL reader,
  Linux-only Orca paths labelled, portable file URL, overhang_allow.json).
- Not pushed: GitHub SSH unreachable on 2026-10-31 (also `mech-chargeport-front`, `audit-lot2` PR not opened).

## Open questions
| # | Question | Answer |
|---|---|---|
| L3-1 | C6: tube_section.py hard-codes stale wire lists. Derive them from harness.py (tube routes), or drop the tube / column section SVGs? | drop them (2026-10-31): done |

## Next
Lot C done. Push, PR, merge (merge commit), then audit-lotE on top.
