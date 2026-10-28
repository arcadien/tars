"""Flatten an OrcaSlicer preset (user or system) into one self-contained JSON for the CLI --load-settings.

usage: python3 -I scripts/orca_profile.py machine|process|filament "<preset name>" out.json

Presets are looked up in ~/.config/OrcaSlicer/user/default/<kind>/ then system/*/<kind>/ (recursive), and their
"inherits" chain is merged parent first. The CLI does not resolve the chain itself (it looks for the parent in the
wrong vendor folder), so the result carries every key.
"""
import glob
import json
import os
import sys

ROOT = os.path.expanduser("~/.config/OrcaSlicer")


def find(kind, name):
    pats = [f"{ROOT}/user/default/{kind}/**/*.json", f"{ROOT}/system/*/{kind}/**/*.json"]
    for pat in pats:
        for f in glob.glob(pat, recursive=True):
            if os.path.basename(f)[:-5] == name:
                return f
    for pat in pats:  # file name and "name" can differ
        for f in glob.glob(pat, recursive=True):
            try:
                if json.load(open(f)).get("name") == name:
                    return f
            except (OSError, ValueError):
                pass
    sys.exit(f"orca_profile: {kind} preset '{name}' not found under {ROOT}")


def resolve(kind, name, depth=0):
    if depth > 10:
        sys.exit(f"orca_profile: inherits loop at '{name}'")
    d = json.load(open(find(kind, name)))
    parent = d.get("inherits")
    merged = resolve(kind, parent, depth + 1) if parent else {}
    merged.update(d)
    return merged


def main():
    kind, name, out = sys.argv[1:4]
    d = resolve(kind, name)
    # keep "inherits" (now only a label): the CLI checks the process' compatible_printers against the printer's
    # system parent name, and refuses the pair without it
    d["inherits"] = json.load(open(find(kind, name))).get("inherits", "")
    d["name"], d["from"], d["type"] = name, "User", kind
    json.dump(d, open(out, "w"), indent=1)


if __name__ == "__main__":
    main()
