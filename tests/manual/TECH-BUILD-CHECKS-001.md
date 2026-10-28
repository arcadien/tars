# Manual test TECH-BUILD-CHECKS-001 — fast checks on commit, slow on push, CI gate on main

Requirement: [TECH-BUILD-CHECKS-001](../../requirements/technical.md#tech-build-checks-001). Manual test of the check
pipeline, run once on each machine after `make hook`, and again when the hooks, `scripts/check.sh` or the CI workflow
change; add a line to *Results* every time it is run.

## Equipment
- A clone of the repository with the tools of `CONTRIBUTING.md` installed, and `make hook` run.
- Access to the GitHub repository (pull requests).

## Setup
1. Create a throw-away branch: `git switch -c check-pipeline-test`.

## Steps
1. Change a comment in `mechanical/scad/tars4.scad`, `git add` it and time `git commit -m "plan: test"` (the
   pre-commit hook runs).
2. Add the line `echo("WARNING: pipeline test");` at the end of `tars4.scad`, `git add` it and try to commit.
3. Remove that line. Set `D = 60;` in `tars4.scad` (parts grow off their bed), commit with `--no-verify`, then
   `git push -u origin check-pipeline-test`.
4. Push it with `git push --no-verify`, open a pull request to main and wait for the `check` job.
5. Try to merge the pull request.
6. Close the pull request without merging; delete the branch locally and on GitHub.

## Pass criteria
- Step 1: the commit goes through in ≤ 30 s.
- Step 2: the commit is refused (model WARNING).
- Step 3: the push is refused (a part off its bed).
- Step 4: the `check` job fails.
- Step 5: GitHub blocks the normal merge. As a repository admin you can still bypass the rule (the bypass is meant
  for direct pushes such as measurement commits): the test passes if the merge is only possible through that bypass.

## Results
| Date | Commit / build | Machine | Commit time | WARNING refused | Push refused | CI failed | Merge blocked | Pass | By | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
