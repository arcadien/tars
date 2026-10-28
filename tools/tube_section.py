"""Cross-sections of the pivot tubes filled with their wires (renders/tars4_tube_sections.svg).

usage: python3 -I tools/tube_section.py

Wire outer diameters measured on the user's stock (silicone insulation): 26 AWG 1.5 mm, 28 AWG 1.2 mm, 30 AWG 0.8 mm.
Each panel packs the wires inside the 7 mm bore by relaxation (circles pushed apart and towards the centre until
nothing overlaps); every module is fitted (microSD, motion and weather sensors included). Colours follow the wiring sketch (tars4_wiring.html).
"""
import math
import os
import random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "renders", "tars4_tube_sections.svg")
BORE = 7.0
OD = {26: 1.5, 28: 1.2, 30: 0.8}
COL = {"pos": "#d0352c", "neg": "#262b30", "sys": "#df8500", "gnd": "#2c68cf", "3v3": "#0f8f96", "spi": "#1c9653",
       "i2s": "#8b4bd0", "i2c": "#c2185b", "en": "#8d6e00", "sd": "#9e9d24", "usb": "#8a5a2b"}


def middle(sig):
    w = [("B+", 26, "pos"), ("B−", 26, "neg"), ("VSYS", 26, "sys"), ("GND", 26, "gnd"),
         ("3V3", sig, "3v3"), ("GND", sig, "gnd")]
    w += [(n, sig, "spi") for n in ("SCK", "MOSI", "DC", "CS2", "RST")]
    w += [("BL", sig, "en"), ("ASD", sig, "en")] + [(n, sig, "i2s") for n in ("BCLK", "LRC", "DIN")]
    opt = [("PIR", sig, "i2c"), ("SDA", sig, "i2c"), ("SCL", sig, "i2c")]
    return w, opt


def left(sig):
    w = [("B+", 26, "pos"), ("B−", 26, "neg"), ("VSYS", 26, "sys"), ("GND", 26, "gnd"), ("3V3", 26, "3v3"),
         ("GND", 26, "gnd"), ("VB/2", sig, "sys"), ("USB", sig, "usb"), ("SDEN", sig, "sd")]
    opt = [("CLK", sig, "sd"), ("CMD", sig, "sd"), ("D0", sig, "sd"), ("GND", sig, "gnd")]
    return w, opt


def right(sig):
    w = [("B+", 26, "pos"), ("B−", 26, "neg"), ("SDA", sig, "i2c"), ("SCL", sig, "i2c"), ("3V3", sig, "3v3"), ("GND", sig, "gnd")]
    return w, []


def pack(radii, seed=1):
    """Relaxation packing inside the bore; returns centres and the worst remaining overlap (mm)."""
    rnd = random.Random(seed)
    R = BORE / 2
    best = None
    for attempt in range(40):
        pts = [[rnd.uniform(-1.5, 1.5), rnd.uniform(-1.5, 1.5)] for _ in radii]
        for it in range(4000):
            pull = 0.03 * (1 - it / 4000) + 0.002
            for i, p in enumerate(pts):          # gentle pull towards the centre (compact bundle)
                p[0] -= pull * p[0]; p[1] -= pull * p[1]
            for i in range(len(pts)):
                for j in range(i + 1, len(pts)):
                    dx, dy = pts[j][0] - pts[i][0], pts[j][1] - pts[i][1]
                    d = math.hypot(dx, dy) or 1e-6
                    m = radii[i] + radii[j] - d
                    if m > 0:
                        k = m / d / 2
                        pts[i][0] -= dx * k; pts[i][1] -= dy * k
                        pts[j][0] += dx * k; pts[j][1] += dy * k
            for i, p in enumerate(pts):          # keep inside the bore
                d = math.hypot(*p)
                lim = R - radii[i]
                if d > lim:
                    p[0] *= lim / d; p[1] *= lim / d
        worst = 0
        for i in range(len(pts)):
            worst = max(worst, math.hypot(*pts[i]) + radii[i] - R)
            for j in range(i + 1, len(pts)):
                worst = max(worst, radii[i] + radii[j] - math.hypot(pts[j][0] - pts[i][0], pts[j][1] - pts[i][1]))
        if best is None or worst < best[1]:
            best = (pts, worst)
        if worst < 0.01:
            break
    return best


def fill(wires):
    return sum(math.pi * (OD[g] / 2) ** 2 for _, g, _ in wires) / (math.pi * (BORE / 2) ** 2)


PANELS = [
    ("Middle tube · if signals in 28 AWG", "power 26 AWG, signals 28 AWG (dropped)", middle(28)),
    ("Middle tube · chosen", "power 26 AWG, signals + screen supply 30 AWG", middle(30)),
    ("Left tube · chosen", "power 26 AWG, signals 30 AWG", left(30)),
    ("Right tube · chosen", "B+ / B− 26 AWG, I2C + sensor supply 30", right(30)),
]
S, PW, PH = 34, 330, 330          # px per mm, panel size
cols = []
for title, sub, (base, opt) in PANELS:
    wires = base + opt
    radii = [OD[g] / 2 for _, g, _ in wires]
    pts, worst = pack(radii, seed=len(wires))
    cols.append((title, sub, wires, len(wires), pts, worst, True))

W = PW * len(cols)
H = PH + 60
out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="IBM Plex Mono, Consolas, monospace">',
       f'<rect width="{W}" height="{H}" fill="#fbfbf9"/>']
for k, (title, sub, wires, nb, pts, worst, with_opt) in enumerate(cols):
    ox, cy = k * PW + PW / 2, 175
    out.append(f'<text x="{ox}" y="24" font-size="15" font-weight="600" text-anchor="middle" fill="#1d2226">{title}</text>')
    out.append(f'<text x="{ox}" y="42" font-size="11.5" text-anchor="middle" fill="#5e676d">{sub}</text>')
    out.append(f'<circle cx="{ox}" cy="{cy}" r="{BORE / 2 * S + 0.5 * S}" fill="#e7d7a6" stroke="#b8902a" stroke-width="1.5"/>')
    out.append(f'<circle cx="{ox}" cy="{cy}" r="{BORE / 2 * S}" fill="#ffffff" stroke="#b8902a" stroke-width="1.2"/>')
    for i, ((name, g, fam), p) in enumerate(zip(wires, pts)):
        r = OD[g] / 2 * S
        dash = ' stroke-dasharray="4 3"' if i >= nb else ""
        c = COL[fam]
        out.append(f'<circle cx="{ox + p[0] * S:.1f}" cy="{cy + p[1] * S:.1f}" r="{r - 1:.1f}" fill="{c}" fill-opacity=".22" stroke="{c}" stroke-width="2"{dash}/>')
        fs = 7 if g == 30 else 8.5 if g == 28 else 10
        out.append(f'<text x="{ox + p[0] * S:.1f}" y="{cy + p[1] * S + fs * 0.35:.1f}" font-size="{fs}" text-anchor="middle" fill="#1d2226">{name}</text>')
    f = fill(wires)
    tag = "comfortable" if f <= 0.42 else "tight" if f <= 0.52 else "very hard"
    out.append(f'<text x="{ox}" y="{cy + BORE / 2 * S + 0.5 * S + 28}" font-size="13" font-weight="600" text-anchor="middle" fill="#1d2226">{len(wires)} wires · {f * 100:.0f} %</text>')
    out.append(f'<text x="{ox}" y="{cy + BORE / 2 * S + 0.5 * S + 46}" font-size="11.5" text-anchor="middle" fill="#5e676d">{tag}{"" if worst < 0.02 else " · does not fit flat"}</text>')
    if worst >= 0.02:
        print(f"note: {title} {'+opt' if with_opt else ''}: packing left {worst:.2f} mm overlap")
    if k < len(cols) - 1:
        out.append(f'<line x1="{(k + 1) * PW}" y1="10" x2="{(k + 1) * PW}" y2="{H - 10}" stroke="#c9cec9"/>')
out.append(f'<text x="{W / 2}" y="{H - 10}" font-size="11" text-anchor="middle" fill="#5e676d">Section through the Ø7 bore of the 8/7 brass tube · measured silicone wires: 26 AWG Ø1.5, 28 AWG Ø1.2, 30 AWG Ø0.8 · all modules fitted (microSD, PIR, BME280)</text>')
out.append("</svg>")
open(OUT, "w").write("\n".join(out))
for title, sub, wires, nb, pts, worst, with_opt in cols:
    print(f"{title:36s} {len(wires):2d} wires {fill(wires) * 100:4.0f} %  overlap {worst:.3f}")
print(OUT)
