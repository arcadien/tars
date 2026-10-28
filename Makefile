# TARS: `make check` rebuilds and validates what changed since the last pass (see scripts/check.sh; `make check-all`
# runs every stage but overhang and orca); `make check-<stage>` runs one stage (model, stl, erc, renders, docs,
# overhang, orca), even if unchanged: `make check-stl` exports the STLs before a print (they are not in git);
# overhang and orca are never part of `make check` (done by hand in Orca);
# `make hook` installs the git hooks (shims to the branch's scripts/): pre-commit (fast checks), commit-msg (RBD),
# pre-push (slow checks).
STAGES := model stl overhang orca erc renders docs

.PHONY: check check-all $(addprefix check-,$(STAGES)) hook

check:
	scripts/check.sh

check-all:
	FORCE=1 scripts/check.sh

$(addprefix check-,$(STAGES)): check-%:
	FORCE=1 scripts/check.sh $*

# the hooks are shared by every worktree: each one is scripts/hook-shim, which runs the checked-out branch's own
# scripts/<hook> (none: nothing to run)
hook:
	d=$$(git rev-parse --git-common-dir)/hooks; for h in pre-commit commit-msg pre-push; do \
	  install -m 755 scripts/hook-shim $$d/$$h; done
