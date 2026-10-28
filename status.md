# Branch tech-build-artifacts — generated print files out of git, checks split by speed

Branch state file (CLAUDE.md, *Branches*): read it first when the branch is picked up again, keep it
current, answer the questions here.

## Goal
STLs and raw plates become build outputs (ignored, `make stl` / `make plates` on demand); fast checks on commit, slow
ones on push, full ones in a CI job that gates merges to main.

## State (2026-10-28)
- Validated and committed (2026-10-28): [TECH-BUILD-ARTIFACTS-001](requirements/technical.md#tech-build-artifacts-001),
  [TECH-BUILD-CHECKS-001](requirements/technical.md#tech-build-checks-001) (new domain BUILD).
- Finding: no hook is installed on the Windows clone (`.git/hooks` holds only samples): the pre-commit and commit-msg
  gates did not run there.

## Open questions
| # | Question | Answer |
|---|---|---|
| Q1 | OpenSCAD version to pin (Linux and Windows must match) | |
| Q2 | Renders: pre-push only, or in CI too (needs xvfb)? | |
| Q3 | Delete the STLs from history too (filter-repo, force push)? Proposed: no | |

Hooks were installed on the Windows clone with `make hook` (2026-10-28).

## Next step
Implementation: .gitignore + untrack, check.sh split (fast pre-commit / slow pre-push), pre-push hook, CI workflow,
branch protection, CLAUDE.md / CONTRIBUTING.md / README.
