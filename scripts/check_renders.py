# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow", "numpy"]
# ///
"""Check that render PNGs exist, were written by this run and are not blank.

usage: uv run scripts/check_renders.py --since <epoch seconds> renders/a.png renders/b.png ...

Blank means almost every pixel has the background colour (taken from the four corners): less than MIN_INK of
the image differs from it by more than 24 levels, or the image is a single flat colour.
"""
import os
import sys

import numpy as np
from PIL import Image

MIN_INK = 0.02


def main():
    args = sys.argv[1:]
    since = 0.0
    if "--since" in args:
        i = args.index("--since")
        since = float(args[i + 1])
        del args[i:i + 2]
    bad = 0
    for path in args:
        if not os.path.exists(path):
            print(f"RENDER {path}: missing")
            bad += 1
            continue
        if os.path.getmtime(path) < since:
            print(f"RENDER {path}: not rewritten by this run (stale)")
            bad += 1
            continue
        a = np.asarray(Image.open(path).convert("RGB")).astype(int)
        bg = np.median(np.array([a[0, 0], a[0, -1], a[-1, 0], a[-1, -1]]), axis=0)
        ink = float((np.abs(a - bg).max(axis=2) > 24).mean())
        if a.std() < 1 or ink < MIN_INK:
            print(f"RENDER {path}: blank ({ink:.1%} drawn)")
            bad += 1
        else:
            print(f"   {path}: {a.shape[1]} x {a.shape[0]}, {ink:.0%} drawn")
    print(f"renders: {len(args)} PNG, {bad} problem(s)")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
