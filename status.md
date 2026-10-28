# Branch `tech-orca-sync`

## Goal
The Orca projects kept their old meshes after the teardrop pivot bores (2a92245): the mesh refresh only ran on a
manual `make check-orca`. The pre-push hook now refreshes them when the STLs changed
([TECH-BUILD-CHECKS-001](requirements/technical.md#tech-build-checks-001), amended and validated 2026-10-28).

## State
- `req` e89d49b: TECH-BUILD-CHECKS-001 amended (pre-push refreshes the Orca meshes, no rewrite when up to date).
- `tech` 2a55295: `meshes` stage in `scripts/check.sh`, run by `scripts/pre-push`; `update_orca_project.py` leaves an
  up-to-date project untouched; README, CONTRIBUTING, CLAUDE.md, Makefile updated.
- `tech` deaa318: both Orca projects refreshed (meshes stage), layout of main kept.
- Verified: first run rewrites both projects, `--check` then reports no UPDATED; second run leaves them byte-identical.

## Open questions
- The hand arrangement saved in Orca at 22:50 on `test-schematic` (uncommitted `mechanical/3mf/tars4.3mf`) is not in
  this branch: it will conflict with deaa318. Keep that arrangement (refresh it with the meshes stage) or drop it?

## Next step
Push (pre-push: stl, renders, meshes), PR, CI green, merge by the user; then remove this file.
