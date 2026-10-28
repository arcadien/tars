"""Side sections of the four columns (renders/tars4_column_sections.svg).

usage: python3 -I tools/column_sections.py
Cuts each column and its lid in the mid plane (OpenSCAD projection(cut = true) through tools/column_sections.scad),
draws every module as its side silhouette, colours and labels them. Uses the model's defaults (every module fitted).
"""
import os, re, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAD = os.path.join(ROOT, "tools", "column_sections.scad")
OUT = os.path.join(ROOT, "renders", "tars4_column_sections.svg")
KEYS = "col lid ins env screen s3 sock carrier spk amp rtc acc mic pir bme hub cell contact fuse tp usb sd buck pp sw tube".split()
# connectors: read the CONN list from the model (column, ref, what)
_e = os.path.join(tempfile.mkdtemp(), "c.echo")
_t = os.path.join(os.path.dirname(_e), "c.scad")
open(_t, "w").write(f'include <{os.path.join(ROOT, "tars4.scad")}>\nfor (c = CONN) echo(str("CONN|", c[0], "|", c[1], "|", c[2]));\n')
subprocess.run(["openscad", "-D", 'part="none"', "-o", _e, "--export-format", "echo", _t], capture_output=True)
CONN = [l.split('"')[1].split("|")[1:] for l in open(_e) if "CONN|" in l]
S = tempfile.mkdtemp()


def export(job):
    i, k = job
    j = int(k[4:]) if k.startswith("conn") else 0
    f = os.path.join(S, f"c{i}_{k}.svg")
    subprocess.run(["openscad", "-D", f"I={i}", "-D", f"J={j}", "-D", f'K="{k[:4] if k.startswith("conn") else k}"', "-D", f"CUT={'true' if k in ('col', 'lid', 'ins') else 'false'}",
                    "-D", 'part="none"', "-o", f, SCAD], capture_output=True)
    if os.path.exists(f) and "<path" not in open(f).read():
        os.remove(f)


with ThreadPoolExecutor(8) as ex:
    list(ex.map(export, [(i, k) for i in range(4) for k in KEYS] + [(int(c[0]), f"conn{j}") for j, c in enumerate(CONN)]))
K = 3.2                       # px per mm
PW, TOP, BOT = 375, 70, 50    # panel width, margins
H = 248
NAMES = ["Left leg", "Left middle", "Right middle", "Right leg"]
PARTS = {  # key: (label, fill, stroke)
    "cell": ("18650 cell", "#9db7e8", "#3d64b0"), "contact": ("contacts", "#c9c9c9", "#888"),
    "tp": ("TP4056 + DW01", "#9fd3a5", "#2e7d3a"), "pp": ("power-path board", "#e3c99a", "#9a7432"),
    "sw": ("switch", "#555", "#222"), "sd": ("microSD reader", "#a8d8c8", "#2f8a6c"),
    "buck": ("TPS63020", "#c9b5e8", "#6b4bb0"), "screen": ("screen", "#30343a", "#111"),
    "s3": ("LOLIN S3 Mini (plugged in)", "#9ed6d6", "#1f7f80"), "sock": ("female 2 × 8 headers", "#333", "#000"),
    "carrier": ("S3 carrier (wires soldered behind)", "#e6b98a", "#a0622a"), "fuse": ("fuse F1 / F2", "#f2c14e", "#a07a10"), "hub": ("P1 / P2 (stripboards)", "#e6b98a", "#a0622a"),
    "rtc": ("DS3231 (ZS-042)", "#a9b7e0", "#2c3f8a"), "acc": ("ADXL345", "#f0a3a8", "#b0303b"),
    "mic": ("INMP441", "#cfd08f", "#7c7d1f"), "spk": ("speaker", "#9a9a9a", "#555"),
    "amp": ("MAX98357A", "#d2a8e3", "#7b3a99"), "pir": ("AM312", "#f4f4ee", "#888"),
    "usb": ("micro-USB socket", "#9a9a9a", "#444"), "bme": ("BME280", "#e0b0e8", "#9a3aa8"),
    "tube": ("brass tube 8/7", "#e8c766", "#a8862a"),
}
for j, (col, ref, what) in enumerate(CONN):
    PARTS[f"conn{j}"] = (f"{ref} {what}", "#ff9b3d", "#c2560a")
SHELL = {"col": ("#d9d8d3", "#8e8c86"), "lid": ("#a9a7a1", "#6e6c66"), "ins": ("#222", "#000"), "env": ("url(#hatch)", "none")}
def paths(f):
    t = open(f).read()
    return re.findall(r'<path d="(.*?)"', t, re.S)
def bbox(ds):
    xs, ys = [], []
    for d in ds:
        nums = [float(v) for v in re.findall(r'-?\d+(?:\.\d+)?(?:e-?\d+)?', d)]
        xs += nums[0::2]; ys += nums[1::2]
    return min(xs), max(xs), min(ys), max(ys)
W = PW * 4
Ht = TOP + H * K + BOT
o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {Ht:.0f}" width="{W}" height="{Ht:.0f}" font-family="IBM Plex Sans, Segoe UI, sans-serif">',
     f'<rect width="{W}" height="{Ht:.0f}" fill="#fbfbf9"/>',
     '<defs><pattern id="hatch" width="1.2" height="1.2" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
     '<rect width="1.2" height="1.2" fill="#f6ebc4"/><line x1="0" y1="0" x2="0" y2="1.2" stroke="#c9a640" stroke-width=".35"/></pattern></defs>']
for i in range(4):
    ox = i * PW + 46
    g = f'<g transform="translate({ox},{TOP + H * K}) scale({K})">'
    o.append(f'<text x="{ox + 15.5 * K}" y="28" font-size="17" font-weight="600" text-anchor="middle" fill="#1d2226">{NAMES[i]}</text>')
    o.append(f'<text x="{ox}" y="50" font-size="11" fill="#5e676d">avant</text><text x="{ox + 31 * K}" y="50" font-size="11" text-anchor="end" fill="#5e676d">couvercle</text>')
    body = [g]
    for k in ("col", "lid", "ins", "env"):
        f = os.path.join(S, f"c{i}_{k}.svg")
        if os.path.exists(f):
            fill, st = SHELL[k]
            for d in paths(f): body.append(f'<path d="{d}" fill="{fill}" stroke="{st}" stroke-width="0.15" fill-rule="evenodd"/>')
    labels = []
    for k, (lab, fill, st) in PARTS.items():
        f = os.path.join(S, f"c{i}_{k}.svg")
        if not os.path.exists(f): continue
        ds = paths(f)
        for d in ds: body.append(f'<path d="{d}" fill="{fill}" fill-opacity=".85" stroke="{st}" stroke-width="0.25" fill-rule="evenodd"/>')
        x0, x1, y0, y1 = bbox(ds)
        labels.append(((y0 + y1) / 2, x1, lab, st))
    body.append('</g>')
    o += body
    # z ticks
    for z in range(0, 249, 50):
        y = TOP + (H - z) * K
        o.append(f'<line x1="{ox - 6}" y1="{y}" x2="{ox - 1}" y2="{y}" stroke="#8e8c86"/><text x="{ox - 9}" y="{y + 4}" font-size="10" text-anchor="end" fill="#5e676d">{z}</text>')
    # labels on the right, spread so they never overlap
    labels.sort()
    placed = []
    for yc, x1, lab, st in labels:
        ty = TOP + H * K + yc * K
        placed.append([ty, x1, lab, st])
    placed.sort()
    for a in range(1, len(placed)):
        if placed[a][0] - placed[a - 1][0] < 14: placed[a][0] = placed[a - 1][0] + 14
    lx = ox + 31 * K + 14
    for ty0, (yc, x1, lab, st) in zip([p[0] for p in placed], [(p[0], p[1], p[2], p[3]) for p in placed]):
        pass
    for p, (yc, x1, lab, st) in zip(placed, sorted(labels)):
        ty = p[0]; ay = TOP + H * K + yc * K; ax = ox + x1 * K
        o.append(f'<polyline points="{ax:.1f},{ay:.1f} {lx - 4},{ay:.1f} {lx},{ty:.1f}" fill="none" stroke="{st}" stroke-width=".8"/>')
        o.append(f'<text x="{lx + 3}" y="{ty + 4:.1f}" font-size="11.5" fill="#1d2226">{lab}</text>')
o.append(f'<text x="{W / 2}" y="{Ht - 16:.0f}" font-size="11.5" text-anchor="middle" fill="#5e676d">Middle section, seen from the left of TARS (front on the left) · z in mm · orange: X1–X15 connectors mated + wire bends · hatching: room kept for the wires</text>')
o.append('</svg>')
open(OUT, "w").write("\n".join(o))
print(OUT)
