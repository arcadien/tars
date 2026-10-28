# TARS: `make check` rebuilds and validates what changed since the last pass (see scripts/check.sh; `make check-all`
# runs every stage but overhang and orca); `make check-<stage>` runs one stage (model, stl, erc, renders, docs,
# overhang, orca), even if unchanged: `make check-stl` exports the STLs before a print (they are not in git);
# overhang and orca are never part of `make check` (done by hand in Orca);
# `make hook` installs the git hooks: pre-commit (fast checks), commit-msg (RBD), pre-push (slow checks).
STAGES := model stl overhang orca erc renders docs

.PHONY: check check-all $(addprefix check-,$(STAGES)) hook

check:
	scripts/check.sh

check-all:
	FORCE=1 scripts/check.sh

$(addprefix check-,$(STAGES)): check-%:
	FORCE=1 scripts/check.sh $*

hook:
	install -m 755 scripts/pre-commit .git/hooks/pre-commit
	install -m 755 scripts/commit-msg .git/hooks/commit-msg
	install -m 755 scripts/pre-push .git/hooks/pre-push
