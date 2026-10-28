# TARS: `make check` rebuilds and validates what changed since the last pass (see scripts/check.sh; `make check-all`
# runs every stage but overhang and orca); `make check-<stage>` runs one stage (stl, erc, renders, docs, overhang,
# orca), even if unchanged; overhang and orca are never part of `make check` (done by hand in Orca);
# `make hook` installs the git pre-commit hook.
STAGES := stl overhang orca erc renders docs

.PHONY: check check-all $(addprefix check-,$(STAGES)) hook

check:
	scripts/check.sh

check-all:
	FORCE=1 scripts/check.sh

$(addprefix check-,$(STAGES)): check-%:
	FORCE=1 scripts/check.sh $*

hook:
	install -m 755 scripts/pre-commit .git/hooks/pre-commit
