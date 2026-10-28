"""Generate the TARS4 KiCad schematic (kicad/tars4.kicad_sch) from the netlist below.

usage: python3 -I tools/kicad_sch_gen.py

Standard symbols are copied from kicad/lib_src/<Lib>__<Name>.kicad_sym (taken from the KiCad 10 libraries) and embedded
in the schematic; every breakout module gets its own rectangular symbol (lib "tars"). Every signal is drawn
with real wires (A2 sheet): the power section is wired locally and the buses run in two channels on each side of the
S3, one vertical track per net; GND and +3V3 use power symbols. Every pin gets a net in the `nets` dict of its part;
the wires only decide how it is drawn (a pin left undrawn gets a net label, reported as a warning). After writing, the file is upgraded to the native KiCad 10 format with
kicad-cli and its exported netlist is compared with the `nets` dicts (any accidental wire short is reported).
Check it with: kicad-cli sch erc kicad/tars4.kicad_sch ; kicad-cli sch export pdf kicad/tars4.kicad_sch
"""
import os
import re
import subprocess
import tempfile
import uuid
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LIBSRC = os.path.join(ROOT, "kicad", "lib_src")
OUT = os.path.join(ROOT, "kicad", "tars4.kicad_sch")
KICAD = os.path.expanduser("~/bin/kicad-10.0.7-x86_64.AppImage")
ROOT_UUID = str(uuid.uuid5(uuid.NAMESPACE_URL, "tars4-root"))
_n = [0]


def U():
    _n[0] += 1
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"tars4-{_n[0]}"))


def font(size=1.27):
    return f"(effects (font (size {size} {size})))"


def r2(v):
    return round(v + 0.0, 2)


# ---------------- library symbols ----------------
def block(text, start):
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    raise ValueError("unbalanced")


PINRE = re.compile(r'\(pin (\w+) \w+\s*\(at ([-\d.]+) ([-\d.]+) ([-\d.]+)\).*?\(name "([^"]*)".*?\(number "([^"]*)"', re.S)
LIBS, PINS = {}, {}


def load_std(lib_id):
    lib, name = lib_id.split(":")
    text = open(os.path.join(LIBSRC, f"{lib}__{name}.kicad_sym")).read()
    b = block(text, text.index('(symbol "'))
    b = b.replace(f'(symbol "{name}"', f'(symbol "{lib_id}"', 1)
    LIBS[lib_id] = b
    PINS[lib_id] = {m.group(6): (float(m.group(2)), float(m.group(3)), float(m.group(4))) for m in PINRE.finditer(b)}


def module(name, left, right=(), width=17.78):
    """Rectangular symbol: left / right = lists of (pin name, pin number)."""
    lib_id = f"tars:{name}"
    n, pitch, plen = max(len(left), len(right)), 5.08, 5.08
    top = round((n - 1) * pitch / 2 / 2.54) * 2.54
    h2 = top + 2.54
    w2 = width / 2
    pins, pmap = [], {}
    for side, lst in ((-1, left), (1, right)):
        for i, (pn, num) in enumerate(lst):
            x, y, a = side * (w2 + plen), top - i * pitch, 0 if side < 0 else 180
            pmap[num] = (x, y, a)
            pins.append(f'(pin passive line (at {x:.2f} {y:.2f} {a}) (length {plen}) (name "{pn}" {font()}) (number "{num}" {font()}))')
    LIBS[lib_id] = (f'(symbol "{lib_id}" (pin_numbers (hide yes)) (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)'
                    f' (property "Reference" "U" (at 0 {h2 + 1.27:.2f} 0) {font()})'
                    f' (property "Value" "{name}" (at 0 {-h2 - 1.27:.2f} 0) {font()})'
                    f' (property "Footprint" "" (at 0 0 0) (hide yes) {font()})'
                    f' (property "Datasheet" "" (at 0 0 0) (hide yes) {font()})'
                    f' (symbol "{name}_0_1" (rectangle (start {-w2:.2f} {h2:.2f}) (end {w2:.2f} {-h2:.2f})'
                    f' (stroke (width 0.254) (type default)) (fill (type background))))'
                    f' (symbol "{name}_1_1" {" ".join(pins)}) (embedded_fonts no))')
    PINS[lib_id] = pmap
    return lib_id, h2


# ---------------- schematic items ----------------
items = []
PLACED = {}            # ref -> (lib_id, X, Y, rot, mirror)
NETS = {}              # (ref, pin) -> net
DONE = set()           # pins already drawn (wired, power symbol, label or no-connect)
SEGS = []              # wire segments ((x1, y1), (x2, y2))
POINTS = []            # connection points of every symbol pin (power symbols included)
_pwr = [0]
OUTWARD = {0: (-1, 0), 180: (1, 0), 90: (0, 1), 270: (0, -1)}  # pin angle -> free direction on the sheet (y down)


def pin_point(lib_id, num, X, Y, rot, mirror=None):
    px, py, pa = PINS[lib_id][num]
    if rot == 90:
        px, py, pa = -py, px, (pa + 90) % 360
    elif rot == 270:
        px, py, pa = py, -px, (pa + 270) % 360
    elif rot == 180:
        px, py, pa = -px, -py, (pa + 180) % 360
    if mirror == "x":            # flip top <-> bottom, applied after the rotation
        py, pa = -py, (360 - pa) % 360
    elif mirror == "y":          # flip left <-> right
        px, pa = -px, (180 - pa) % 360
    return r2(X + px), r2(Y - py), pa


def sym(lib_id, ref, value, X, Y, rot=0, mirror=None, hidden_ref=False, txt="ud", dy=6.35):
    """txt: 'ud' = reference above / value below, 'r' / 'l' = both on the right / left, or ((rx, ry), (vx, vy)) absolute."""
    pins = " ".join(f'(pin "{n}" (uuid "{U()}"))' for n in PINS[lib_id])
    hide = " (hide yes)" if hidden_ref else ""
    fa = 90 if rot in (90, 270) else 0          # field angles are relative to the symbol: keep the text horizontal
    if txt == "r":
        (rx, ry, rj), (vx, vy, vj) = (X + 2.54, Y - 1.27, " (justify left)"), (X + 2.54, Y + 1.27, " (justify left)")
    elif txt == "l":
        (rx, ry, rj), (vx, vy, vj) = (X - 2.54, Y - 1.27, " (justify right)"), (X - 2.54, Y + 1.27, " (justify right)")
    elif isinstance(txt, tuple):
        (rx, ry), (vx, vy) = txt
        rj = vj = ""
    else:
        (rx, ry, rj), (vx, vy, vj) = (X, Y - dy, ""), (X, Y + dy, "")
    mir = f" (mirror {mirror})" if mirror else ""
    items.append(f'(symbol (lib_id "{lib_id}") (at {X} {Y} {rot}){mir} (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (uuid "{U()}")'
                 f' (property "Reference" "{ref}" (at {r2(rx)} {r2(ry)} {fa}){hide} (effects (font (size 1.27 1.27)){rj}))'
                 f' (property "Value" "{value}" (at {r2(vx)} {r2(vy)} {fa}) (effects (font (size 1.27 1.27)){vj}))'
                 f' (property "Footprint" "" (at {X} {Y} 0) (hide yes) {font()})'
                 f' (property "Datasheet" "" (at {X} {Y} 0) (hide yes) {font()})'
                 f' {pins} (instances (project "tars4" (path "/{ROOT_UUID}" (reference "{ref}") (unit 1)))))')
    for n in PINS[lib_id]:
        POINTS.append(pin_point(lib_id, n, X, Y, rot, mirror)[:2])


def PW(kind, p, side=None):
    """Power symbol (GND, +3V3 or PWR_FLAG) on point p; side 'l' / 'r' turns it to point left / right (horizontal pins)."""
    _pwr[0] += 1
    lib = {"GND": "power:GND", "+3V3": "power:+3V3", "FLAG": "power:PWR_FLAG"}[kind]
    ref = f"#FLG{_pwr[0]:02d}" if kind == "FLAG" else f"#PWR{_pwr[0]:02d}"
    x, y = p
    if side:
        # GND points down at 0 deg (right at 90), +3V3 points up at 0 deg (left at 90)
        rot = {("GND", "r"): 90, ("GND", "l"): 270, ("+3V3", "l"): 90, ("+3V3", "r"): 270}[(kind, side)]
        tx = x + (6.35 if side == "r" else -6.35)
        sym(lib, ref, kind, x, y, rot, hidden_ref=True, txt=((tx, y), (tx, y)))
    else:
        sym(lib, ref, "PWR_FLAG" if kind == "FLAG" else kind, x, y, hidden_ref=True, dy=3.81 if kind == "GND" else -3.81)


def L(net, p, left=False):
    """Local net label on point p (text to the right, or to the left)."""
    ang, just = (180, "right bottom") if left else (0, "left bottom")
    items.append(f'(label "{net}" (at {p[0]} {p[1]} {ang}) (effects (font (size 1.27 1.27)) (justify {just})) (uuid "{U()}"))')


def pin(tok):
    ref, num = tok.split(".", 1)
    lib_id, X, Y, rot, mir = PLACED[ref]
    DONE.add((ref, num))
    return pin_point(lib_id, num, X, Y, rot, mir)


def pt(tok):
    return pin(tok)[:2] if isinstance(tok, str) else (r2(tok[0]), r2(tok[1]))


def W(*toks):
    """Polyline of wires through pins ('U1.IN+') and points ((x, y))."""
    ps = [pt(t) for t in toks]
    for a, b in zip(ps, ps[1:]):
        assert a[0] == b[0] or a[1] == b[1], f"wire not orthogonal: {a} {b}"
        SEGS.append((a, b))
    return ps[-1]


def stub(tok, n=2.54):
    x, y, pa = pin(tok)
    dx, dy = OUTWARD[pa]
    return W((x, y), (x + dx * n, y + dy * n))


def place(lib_id, ref, value, X, Y, nets, rot=0, mirror=None, txt=None, dy=6.35):
    PLACED[ref] = (lib_id, X, Y, rot, mirror)
    for k, v in nets.items():
        NETS[(ref, k)] = v
    if txt is None:
        txt = "r" if lib_id in ("Device:R", "Device:C", "Device:C_Polarized", "Device:Polyfuse", "Device:Battery_Cell") and rot == 0 else "ud"
    sym(lib_id, ref, value, X, Y, rot, mirror, txt=txt, dy=dy)


def mod(lib_id, h2, ref, value, X, Y, nets):
    place(lib_id, ref, value, X, Y, nets, dy=h2 + 1.27)


def rail(toks, n, kind=None, net=None, left=False):
    """Join several pins facing the same way with one line at distance n; power symbol / label on the first end."""
    ends = [stub(t, n) for t in toks]
    ends_sorted = sorted(ends)
    for a, b in zip(ends_sorted, ends_sorted[1:]):
        W(a, b)
    p = ends_sorted[-1] if left is None else ends_sorted[0]
    if kind:
        PW(kind, p)
    if net:
        L(net, p, left)
    return ends_sorted


TEES = set()


def T(p):
    """Declare a T joint on the middle of a wire (the wire is split there)."""
    TEES.add((r2(p[0]), r2(p[1])))


def bus(toks, x, extra=()):
    """One vertical track at x: each pin runs horizontally to it; extra = y of other wires joining the track."""
    ys = list(extra)
    for t in toks:
        px, py, pa = pin(t)
        assert (x - px) * OUTWARD[pa][0] > 0, f"{t} does not face the track at x={x}"
        W((px, py), (x, py))
        ys.append(py)
    ys = sorted(set(ys))
    for a, b in zip(ys, ys[1:]):
        W((x, a), (x, b))


def finish():
    """Draw every pin not drawn yet: no-connect, power symbol or label on a short stub."""
    for (ref, num), net in NETS.items():
        if (ref, num) in DONE:
            continue
        tok = f"{ref}.{num}"
        x, y, pa = pin(tok)
        if net == "NC":
            items.append(f'(no_connect (at {x} {y}) (uuid "{U()}"))')
        elif net in ("GND", "+3V3"):
            PW(net, stub(tok), {0: "l", 180: "r"}.get(pa))      # horizontal pins: symbol turned sideways
        else:
            print(f"WARNING: {tok} ({net}) not wired, net label added")
            L(net, stub(tok), left=(pa == 0))


def note(text, x, y, size=1.5):
    t = text.replace('"', "'")
    items.append(f'(text "{t}" (exclude_from_sim no) (at {x} {y} 0) (effects (font (size {size} {size})) (justify left)) (uuid "{U()}"))')


for lid in ["Device:R", "Device:C", "Device:C_Polarized", "Device:D_Schottky", "Device:D_Zener", "Device:Battery_Cell",
            "Device:Polyfuse", "Device:Q_PMOS", "Device:Q_NMOS", "Device:Speaker", "Switch:SW_SPST", "power:GND", "power:+3V3", "power:PWR_FLAG"]:
    load_std(lid)

P = lambda *names: [(n, n) for n in names]  # pin name = pin number
S3L = [("EN", "EN"), ("IO1", "1"), ("IO2", "2"), ("IO3", "3"), ("IO4", "4"), ("IO5", "5"), ("IO12", "12"), ("IO6", "6"),
       ("IO13", "13"), ("IO7", "7"), ("IO11", "11"), ("IO8", "8"), ("IO10", "10"), ("IO9", "9"), ("3V3", "3V"), ("IO14", "14")]
S3R = [("IO33", "33"), ("IO43", "43"), ("IO37", "37"), ("IO44", "44"), ("IO38", "38"), ("IO36", "36"), ("IO34", "34"), ("IO35", "35"),
       ("IO21", "21"), ("IO18", "18"), ("IO17", "17"), ("IO16", "16"), ("GND", "G1"), ("GND", "G2"), ("IO15", "15"), ("VBUS", "V")]
s3, s3h = module("LOLIN_S3_Mini", S3L, S3R, 25.4)
tp, tph = module("TP4056_DW01", P("IN+", "IN-"), P("OUT+", "OUT-", "B+", "B-"), 15.24)
bk, bkh = module("TPS63020_3V3", P("VIN", "EN", "PS", "GND"), P("VOUT"), 15.24)
lcd, lcdh = module("ST7789_1.3_CS", P("GND", "VCC", "SCL", "SDA", "RES", "DC", "CS", "BLK"), (), 15.24)
amp, amph = module("MAX98357A", P("LRC", "BCLK", "DIN", "GAIN", "SD", "GND", "VIN"), P("OUT+", "OUT-"), 15.24)
mic, mich = module("INMP441", P("SCK", "WS", "SD", "L/R", "VDD", "GND"), (), 15.24)
rtc, rtch = module("DS3231_ZS-042", P("32K", "SQW", "SCL", "SDA", "VCC", "GND"), (), 15.24)
acc, acch = module("ADXL345_GY-291", P("GND", "VCC", "CS", "INT1", "INT2", "SDO", "SDA", "SCL"), (), 15.24)
pir, pirh = module("AM312_PIR", P("VIN", "OUT", "GND"), (), 15.24)
bme, bmeh = module("BME280_GY", P("VCC", "GND", "SCL", "SDA"), (), 15.24)
sd, sdh = module("microSD_3V3", P("CLK", "CMD", "D0", "D1", "D2", "D3", "VCC", "GND"), (), 15.24)

# ---------------- power (fully wired) ----------------
VU, PATH = 35.56, 55.88            # VUSB line, power path line (OUTP -> Q1 -> VPATH -> SW1 -> VSYS)
note("POWER — ground star on the power-path board (left leg)", 15.24, 17.78, 2)
note("VUSB (J1: micro-USB breakout at the foot of the left leg; D3 + C9 on the TP4056 IN pads)", 12.7, 33.02, 1.27)
place("Device:D_Zener", "D3", "SMAJ5.0A (TVS)", 20.32, 46.99, {"1": "VUSB", "2": "GND"}, rot=270, txt=((20.32, 62.23), (20.32, 64.77)))
place("Device:C_Polarized", "C9", "22µ 16V", 12.7, 46.99, {"1": "VUSB", "2": "GND"}, txt=((12.7, 57.15), (12.7, 59.69)))
place("Device:R", "R1", "10k", 30.48, 46.99, {"1": "VUSB", "2": "GND"})
place("Device:R", "R15", "68k", 40.64, 46.99, {"1": "VUSB", "2": "USB_DET"})
place("Device:R", "R16", "100k", 40.64, 62.23, {"1": "USB_DET", "2": "GND"})
mod(tp, tph, "U1", "TP4056 + DW01, R_PROG 2,4k", 73.66, PATH + 7.62,
    {"IN+": "VUSB", "IN-": "GND", "OUT+": "OUTP", "OUT-": "GND", "B+": "BAT+", "B-": "BAT-"})
place("Device:Q_PMOS", "Q1", "AO3401A", 101.6, PATH - 2.54, {"D": "OUTP", "G": "VUSB", "S": "VPATH"}, rot=90, mirror="x",
      txt=((95.25, 48.26), (101.6, 60.96)))
place("Device:D_Schottky", "D1", "1N5822", 116.84, 46.99, {"1": "VPATH", "2": "VUSB"}, rot=90,
      txt=((110.49, 45.72), (110.49, 48.26)))
place("Switch:SW_SPST", "SW1", "inter. ≥ 1 A", 132.08, PATH, {"1": "VPATH", "2": "VSYS"}, dy=-5.08)
mod(bk, bkh, "U9", "TPS63020 3,3 V", 170.18, PATH + 7.62, {"VIN": "VSYS", "EN": "VSYS", "PS": "GND", "GND": "GND", "VOUT": "+3V3"})
place("Device:R", "R2", "1M", 142.24, 62.23, {"1": "BAT+", "2": "VBAT_2"})
place("Device:R", "R3", "1M", 142.24, 74.93, {"1": "VBAT_2", "2": "GND"})
place("Device:Polyfuse", "F1", "PPTC 1.6A", 104.14, 91.44, {"1": "BAT+", "2": "BT1P"})
place("Device:Polyfuse", "F2", "PPTC 1.6A", 124.46, 91.44, {"1": "BAT+", "2": "BT2P"})
place("Device:Battery_Cell", "BT1", "18650 G", 104.14, 104.14, {"1": "BT1P", "2": "BAT-"})
place("Device:Battery_Cell", "BT2", "18650 D", 124.46, 104.14, {"1": "BT2P", "2": "BAT-"})

# VUSB line on top: TVS, R1, R15, TP4056 IN+, Q1 gate, D1 anode
drops = [stub("U1.IN+", 5.08), pt("C9.1"), pt("D3.1"), pt("R1.1"), pt("R15.1"), pt("Q1.G"), pt("D1.2")]
tops = []
for p in drops:
    tops.append(W(p, (p[0], VU)))
tops.sort()
for a, b in zip(tops, tops[1:]):
    W(a, b)
for t in ("C9.2", "D3.2", "R1.2", "U1.IN-", "U1.OUT-", "R16.2", "R3.2"):
    PW("GND", pt(t))
W("R15.2", (40.64, 54.61), "R16.1")
# power path: OUTP -> Q1 -> VPATH (+ D1 cathode) -> SW1 -> VSYS
W("U1.OUT+", "Q1.D")
W("Q1.S", (116.84, PATH), "SW1.1")
W("D1.1", (116.84, PATH))
W("SW1.2", (142.24, PATH), (147.32, PATH), (152.4, PATH), "U9.VIN")
W("U9.EN", (152.4, 60.96), (152.4, PATH))                 # EN tied to VIN
W("U9.PS", (149.86, 66.04), (149.86, 71.12), (149.86, 73.66))
W("U9.GND", (149.86, 71.12))
W((149.86, 73.66), (149.86, 78.74), (154.94, 78.74))
PW("GND", (149.86, 78.74)); PW("FLAG", (154.94, 78.74))
PW("+3V3", stub("U9.VOUT", 2.54))
W((185.42, PATH), (185.42, 63.5), (190.5, 63.5)); PW("FLAG", (190.5, 63.5))
# divider B+ / 2 -> GPIO1: on the cells, not VSYS (VSYS is the USB rail when plugged in); 1M / 1M = 2 µA standing,
# its filter capacitor C6 sits at the S3, see the lanes
W((124.46, 83.82), (134.62, 83.82), (134.62, 58.42), "R2.1")
W("R2.2", (142.24, 68.58), "R3.1")
W((142.24, 68.58), (139.7, 68.58))
# batteries: TP4056 B+ -> F1 / F2 -> cells -> B-
W("U1.B+", (93.98, 66.04), (93.98, 83.82), (104.14, 83.82), (124.46, 83.82))
W((104.14, 83.82), "F1.1"); W((124.46, 83.82), "F2.1")
W("F1.2", "BT1.1"); W("F2.2", "BT2.1")
W("U1.B-", (88.9, 71.12), (88.9, 111.76), (104.14, 111.76), (124.46, 111.76))
W((104.14, 111.76), "BT1.2"); W((124.46, 111.76), "BT2.2")
note("R15 / R16: charger plugged in → USB_DET ≈ 3 V (GPIO21, wake-up).", 15.24, 134.62, 1.27)

# ---------------- controller + peripherals, fully wired ----------------
# The S3 sits between two wiring channels; every net has its own vertical track there. The left column (screens,
# RTC, accelerometer) is mirrored so its pins face the S3, the right column (amplifier, microphone, microSD) faces
# it as usual. Peripheral pin rows sit on odd multiples of 2.54 and the S3 rows on even ones, lanes on x.27 /
# x.73, so no two horizontal wires of different nets ever share a line.
S3X, S3Y = 271.78, 200.66
note("BRAIN — LOLIN S3 Mini (left middle)", 248.92, 17.78, 2)
note("SCREENS, I2C SENSORS →", 132.08, 139.7, 1.5)
note("SOUND, MIC, microSD", 345.44, 17.78, 2)
mod(s3, s3h, "U2", "LOLIN S3 Mini", S3X, S3Y, {
    "EN": "NC", "1": "VBAT_2", "2": "INT1", "3": "PIR", "4": "AMP_SD_S3", "5": "SDA", "12": "SCK_S3", "6": "SCL", "13": "DC",
    "7": "BL_EN", "11": "MOSI_S3", "8": "RST", "10": "CS1", "9": "CS2", "3V": "+3V3", "14": "MIC_BCLK",
    "33": "SD_CLK_S3", "43": "NC", "37": "NC", "44": "NC", "38": "MIC_WS", "36": "SD_EN", "34": "SD_CMD", "35": "SD_D0",
    "21": "USB_DET", "18": "BCLK_S3", "17": "LRC_S3", "16": "DIN", "G1": "GND", "G2": "GND", "15": "MIC_SD", "V": "NC"})
row = lambda r: r2(S3Y - 38.1 + 5.08 * r)
# 33 ohm series resistors right at the S3 pins; SCK split on the carrier: R12 -> screen 1, R19 -> screen 2 (own wire
# through the middle tube, no T at P1)
place("Device:R", "R12", "47 (carrier)", S3X - 24.13, row(6), {"1": "SCK_S3", "2": "SCK1"}, rot=270, dy=2.54)
W("U2.12", "R12.1")
place("Device:R", "R20", "33 (carrier)", S3X - 24.13, row(10), {"1": "MOSI_S3", "2": "MOSI"}, rot=270, dy=2.54)
W("U2.11", "R20.1")
LANE_K = 257.81
place("Device:R", "R19", "47 (carrier)", 245.11, LANE_K, {"1": "SCK_S3", "2": "SCK2"}, rot=270,
      txt=((245.11, LANE_K - 2.54), (245.11, LANE_K + 2.54)))
T((252.73, row(6)))
W((252.73, row(6)), (252.73, LANE_K), "R19.1")
for ref, a, b, r, p in [("R11", "SD_CLK_S3", "SD_CLK", 0, "33"), ("R13", "BCLK_S3", "BCLK", 9, "18"), ("R14", "LRC_S3", "LRC", 10, "17")]:
    place("Device:R", ref, "33", S3X + 24.13, row(r), {"1": a, "2": b}, rot=90,
          txt=((S3X + 22.86, row(r) - 2.54), (S3X + 26.67, row(r) - 2.54)))   # both above: R13 / R14 are one row apart
    W(f"U2.{p}", f"{ref}.1")

XL = [r2(S3X - 33.02 - 2.54 * k) for k in range(15)]     # left channel tracks, k = 0 next to the S3
XR = [r2(S3X + 33.02 + 2.54 * k) for k in range(13)]     # right channel tracks
PXL, PXR, PXJ = r2(XL[-1] - 15.24 - 12.7), r2(XR[-1] + 15.24 + 12.7), r2(XR[-1] + 15.24 + 12.7 + 48.26)
LCD = lambda cs, sck: {"GND": "GND", "VCC": "+3V3", "SCL": sck, "SDA": "MOSI", "RES": "RST", "DC": "DC", "CS": cs, "BLK": "BL_EN"}
modm = lambda lib_id, h2, ref, value, X, Y, nets: place(lib_id, ref, value, X, Y, nets, mirror="y", dy=h2 + 1.27)
modm(lcd, lcdh, "U3", "Screen 1 (left middle)", PXL, 152.4, LCD("CS1", "SCK1"))
modm(lcd, lcdh, "U4", "Screen 2 (right middle)", PXL, 203.2, LCD("CS2", "SCK2"))
modm(rtc, rtch, "U7", "DS3231 ZS-042 (right leg)", PXL, 248.92, {"32K": "NC", "SQW": "NC", "SCL": "SCL", "SDA": "SDA", "VCC": "+3V3", "GND": "GND"})
modm(acc, acch, "U8", "ADXL345 GY-291", PXL, 294.64, {"GND": "GND", "VCC": "+3V3", "CS": "+3V3", "INT1": "INT1", "INT2": "NC", "SDO": "GND", "SDA": "SDA", "SCL": "SCL"})
modm(bme, bmeh, "U11", "BME280 (right leg)", PXL, 340.36, {"VCC": "+3V3", "GND": "GND", "SCL": "SCL", "SDA": "SDA"})
v = stub("U8.VCC")                                         # CS high = I2C mode: tie it to VCC
W(stub("U8.CS"), v)
PW("+3V3", v, "r")
mod(amp, amph, "U5", "MAX98357A (right middle)", PXR, 160.02, {"LRC": "LRC", "BCLK": "BCLK", "DIN": "DIN", "GAIN": "NC", "SD": "AMP_SD", "GND": "GND", "VIN": "VSYS", "OUT+": "SPK+", "OUT-": "SPK-"})
mod(mic, mich, "U6", "INMP441 (left middle)", PXR, 213.36, {"SCK": "MIC_BCLK", "WS": "MIC_WS", "SD": "MIC_SD", "L/R": "GND", "VDD": "+3V3", "GND": "GND"})
mod(sd, sdh, "J2", "microSD (left leg)", PXJ, 279.4, {"CLK": "SD_CLK", "CMD": "SD_CMD", "D0": "SD_D0", "D1": "SD_D1", "D2": "SD_D2", "D3": "SD_D3", "VCC": "SD_3V3", "GND": "GND"})

# BL_EN pull-down R4 (P1) and the amplifier's own shutdown line (GPIO4 -> R10 1 k -> SD, R18 10 k to GND, both on P2)
# sit under the S3
LANE_A = 270.51
place("Device:R", "R4", "10k (P1)", 262.89, 259.08, {"1": "BL_EN", "2": "GND"})
place("Device:R", "R10", "1k (P2)", 289.56, LANE_A, {"1": "AMP_SD_S3", "2": "AMP_SD"}, rot=90, dy=2.54)
place("Device:R", "R18", "10k (P2)", 300.99, 275.59, {"1": "AMP_SD", "2": "GND"})
# left channel
LANE_V, LANE_U, LANE_S, LANE_M, LANE_B = 120.65, 125.73, 26.67, 247.65, 252.73   # VBAT_2, USB_DET, VSYS, MIC_BCLK, BL_EN
bus(["U2.14"], XL[0], [LANE_M])
bus(["U2.7", "U3.BLK", "U4.BLK"], XL[1], [LANE_B])
bus(["U2.9", "U4.CS"], XL[2])
bus(["U2.10", "U3.CS"], XL[3])
bus(["U2.8", "U3.RES", "U4.RES"], XL[4])
bus(["R20.2", "U3.SDA", "U4.SDA"], XL[5])
bus(["U2.13", "U3.DC", "U4.DC"], XL[6])
bus(["R12.2", "U3.SCL"], XL[7])
bus(["U4.SCL"], XL[14], [LANE_K])
W("R19.2", (XL[14], LANE_K))
bus(["U2.6", "U7.SCL", "U8.SCL", "U11.SCL"], XL[8])
bus(["U2.5", "U7.SDA", "U8.SDA", "U11.SDA"], XL[9])
bus(["U2.2", "U8.INT1"], XL[11])
bus(["U2.1"], XL[12], [LANE_V])
W((139.7, 68.58), (139.7, LANE_V), (XL[12], LANE_V))     # VBAT_2 from the divider
# ADC / wake filters at the S3 pins: C6 on VBAT_2 (GPIO1), C8 on USB_DET (GPIO21, high-impedance divider beside the amp pair)
place("Device:C", "C6", "0.1µ (S3)", 200.66, 116.84, {"1": "VBAT_2", "2": "GND"}, rot=180, txt=((190.5, 115.57), (190.5, 118.11)))
T((200.66, LANE_V)); W((200.66, LANE_V), "C6.1"); PW("GND", pt("C6.2"), "r")
place("Device:C", "C8", "0.1µ (S3)", 152.4, 129.54, {"1": "USB_DET", "2": "GND"}, txt="l")
T((152.4, LANE_U)); PW("GND", pt("C8.2"))
# AM312 motion sensor (front of the right middle column, 3V3 / GND from P2): push-pull output straight to GPIO3
# through R17 1 k on P2 (middle tube); wakes the S3 on EXT1 ANY_HIGH with the ADXL345 INT1 and USB_DET
modm(pir, pirh, "U10", "AM312", 124.46, 335.28, {"VIN": "PIR_VDD", "OUT": "PIR_OUT", "GND": "GND"})
LANE_P = 326.39
o = pin("U10.OUT")
place("Device:R", "R17", "1k (P2)", 144.78, 330.2, {"1": "PIR", "2": "PIR_OUT"})
W("U10.OUT", (144.78, o[1]), "R17.2")
# RC on its supply (on P2): R21 100 R + C12 10 µ tantalum, against the backlight PWM ripple on the shared 3V3
place("Device:R", "R21", "100 (P2)", 139.7, 313.69, {"1": "+3V3", "2": "PIR_VDD"}, txt="r")
place("Device:C_Polarized", "C12", "10µ tant. (P2)", 130.81, 320.04, {"1": "PIR_VDD", "2": "GND"}, rot=270,
      txt=((130.81, 314.3), (130.81, 316.84)))
W(stub("U10.VIN"), (139.7, 320.04), "R21.2")
T((139.7, 320.04)); W((139.7, 320.04), "C12.1")
PW("+3V3", pt("R21.1"))
PW("GND", pt("C12.2"), "l")
PW("GND", stub("U10.GND"))
W("R17.1", (XL[13], LANE_P))
bus(["U2.3"], XL[13], [LANE_P])
note("U10: front hole at the top (right middle), R17 on P2; U7, U11 in the right leg (SQW not wired).", 30.48, 356.87, 1.27)
# right channel
bus(["R13.2", "U5.BCLK"], XR[0])
bus(["R14.2", "U5.LRC"], XR[1])
bus(["U2.16", "U5.DIN"], XR[2])
bus(["R10.2", "U5.SD"], XR[3])
T((300.99, LANE_A)); W((300.99, LANE_A), "R18.1"); PW("GND", pt("R18.2"))
bus(["U2.4"], XL[10], [LANE_A])
W((XL[10], LANE_A), "R10.1")
bus(["U5.VIN"], XR[4], [LANE_S])
W((147.32, PATH), (147.32, LANE_S), (XR[4], LANE_S))      # VSYS from the switch, over the top
bus(["U2.38", "U6.WS"], XR[5])
bus(["U2.15", "U6.SD"], XR[6])
bus(["U6.SCK"], XR[7], [LANE_M])
W((XL[0], LANE_M), (XR[7], LANE_M))                        # MIC_BCLK under the S3
bus(["U2.21"], XR[8], [LANE_U])
W((40.64, 54.61), (45.72, 54.61), (45.72, LANE_U), (XR[8], LANE_U))   # USB_DET from R15 / R16
bus(["R11.2", "J2.CLK"], XR[9])
bus(["U2.34", "J2.CMD"], XR[10])
bus(["U2.35", "J2.D0"], XR[11])
# BL_EN under the S3: R4 pull-down (P1)
W((XL[1], LANE_B), (262.89, LANE_B), "R4.1")
PW("GND", pt("R4.2"))
# amplifier output, bulk capacitor on VIN
place("Device:Speaker", "LS1", "39×22×10 8Ω", PXR + 25.4, 144.78, {"1": "SPK+", "2": "SPK-"}, dy=-5.08)
W("U5.OUT+", "LS1.1")
o = pin("U5.OUT-")
W(o[:2], (o[0] + 5.08, o[1]), (o[0] + 5.08, 147.32), "LS1.2")
place("Device:C_Polarized", "C7", "470µ 10V", PXR - 17.78, 181.61, {"1": "VSYS", "2": "GND"})
T((PXR - 17.78, 175.26))
W((PXR - 17.78, 175.26), "C7.1")
PW("GND", pt("C7.2"))
# microSD pull-ups on the lines, decoupling at the socket
for i, (ref, net, rr) in enumerate([("R5", "SD_CMD", 266.7), ("R6", "SD_D0", 271.78), ("R7", "SD_D1", 276.86), ("R8", "SD_D2", 281.94), ("R9", "SD_D3", 287.02)]):
    x = r2(PXR + 10.16 + 7.62 * i)
    place("Device:R", ref, "10k", x, 248.92, {"1": "SD_3V3", "2": net})
    if i < 2:
        T((x, rr))
        W(f"{ref}.2", (x, rr))
    else:
        W(f"{ref}.2", (x, rr), f"J2.{net[3:]}")
rail(["R5.1", "R6.1", "R7.1", "R8.1", "R9.1"], 2.54)
# microSD supply cut in deep sleep (on the power-path board): Q5 high side, R22 keeps it off while GPIO36 floats
SDQ = r2(PXR + 10.16 + 7.62 * 4 - 2.54)
place("Device:Q_PMOS", "Q5", "AO3401A", SDQ, 234.95, {"G": "SD_EN", "S": "+3V3", "D": "SD_3V3"}, mirror="x",
      txt=((SDQ + 8.89, 232.41), (SDQ + 8.89, 236.22)))
W("Q5.D", (SDQ + 2.54, 242.57))
L("SD_3V3", (SDQ + 2.54, 242.57))
PW("+3V3", stub("Q5.S"))
place("Device:R", "R22", "100k", SDQ - 10.16, 231.14, {"1": "+3V3", "2": "SD_EN"}, txt="l")
PW("+3V3", pt("R22.1"))
bus(["U2.36"], XR[12], [234.95])
W((XR[12], 234.95), (SDQ - 10.16, 234.95), "Q5.G")
T((SDQ - 10.16, 234.95)); pin("R22.2")
L("SD_3V3", stub("J2.VCC"), left=True)
place("Device:C_Polarized", "C4", "10µ tant.", PXJ - 27.94, 314.96, {"1": "SD_3V3", "2": "GND"})
place("Device:C", "C5", "0.1µ", PXJ - 15.24, 314.96, {"1": "SD_3V3", "2": "GND"})
rail(["C4.1", "C5.1"], 2.54, net="SD_3V3", left=None)
rail(["C4.2", "C5.2"], 2.54, "GND", left=None)
# P1 decoupling (on the 3V3 strip, next to the S3 wires)
place("Device:C_Polarized", "C1", "220µ tant. CMS", 40.64, 190.5, {"1": "+3V3", "2": "GND"})
place("Device:C_Polarized", "C2", "10µ tant. (P1)", 66.04, 190.5, {"1": "+3V3", "2": "GND"})
place("Device:C", "C3", "0.1µ (P1)", 91.44, 190.5, {"1": "+3V3", "2": "GND"})
place("Device:C_Polarized", "C10", "10µ tant. (P2)", 116.84, 190.5, {"1": "+3V3", "2": "GND"})
place("Device:C", "C11", "0.1µ (P2)", 142.24, 190.5, {"1": "+3V3", "2": "GND"})
rail(["C1.1", "C2.1", "C3.1", "C10.1", "C11.1"], 2.54, "+3V3", left=None)
rail(["C1.2", "C2.2", "C3.2", "C10.2", "C11.2"], 2.54, "GND", left=None)
note("C1 (SMD 7343 tantalum lying under the S3) on its carrier, C2 / C3 on the P1 3V3 strip, C10 / C11 on P2; plans renders/tars4_board_*.svg.", 30.48, 203.2, 1.27)

NY = 365.76
for i, t in enumerate([
        "Q1 + D1 + R1: power path (mains / battery). R2 / R3 (1M, on B+: the real cell voltage, even on mains) on the power-path board; C6 (GPIO1) and C8 (GPIO21) at the S3 pins. Q5 + R22 on the power-path board: microSD cut in sleep (GPIO36 low = on).",
        "U9: EN tied to VIN, PS/SYNC to GND (never drive it high). Its VSYS/GND pair leaves from the star; the logic GND to P1 leaves from its GND pad.",
        "S3: V (VBUS) = the S3 USB-C only. EN = S3 reset (≠ BL_EN). 33 Ω series at the S3 (R20 on MOSI); SCK split on the carrier: R12 → screen 1, R19 → screen 2 (direct wire in the tube), 47 Ω (up to 100 if the image jitters).",
        "BL_EN (GPIO7): backlight of both screens only (PWM possible). AMP_SD (GPIO4): R10 1k + R18 10k on P2 → amplifier SD (off at boot and in sleep). P1 / P2: stripboards under the screens. I2C chain: S3 → ADXL345 → middle tube → P2 → right tube → DS3231 + BME280 (right leg); sensor supply P1 → mic → ADXL345, P2 → right leg.",
        "LEDs: remove every status LED fed by the battery (ZS-042, TPS63020, GY-291, microSD reader…); keep the TP4056 charge LEDs.",
        "Silicone wire: power in 26 AWG (B+/B−, amplifier pair, 3V3 and GND to P1), signals and screen / sensor supply in 30 AWG. Tubes: 13 / 19 / 6 wires.",
        "Connectors X1–X15 (keyed Dupont / JST) between each module and the harness, S3 plugged into a carrier: not drawn, see tars4_wiring.html. D3: unidirectional TVS (Zener symbol). A crossing without a dot is not a connection. Generated by tools/kicad_sch_gen.py (netlist checked at every generation)."]):
    note(t, 15.24, NY + 5.08 * i, 1.5 if i < 6 else 1.27)

finish()

# ---------------- checks: junctions and accidental contacts ----------------
for p in TEES:                                             # split the wires at the declared T joints
    for i, (a, b) in enumerate(SEGS):
        if (a[0] == b[0] == p[0] and min(a[1], b[1]) < p[1] < max(a[1], b[1])) or \
           (a[1] == b[1] == p[1] and min(a[0], b[0]) < p[0] < max(a[0], b[0])):
            SEGS[i] = (a, p)
            SEGS.append((p, b))
            break
ends = Counter()
for a, b in SEGS:
    ends[a] += 1
    ends[b] += 1
for p in POINTS:
    ends[p] += 1
for p, k in ends.items():
    if k >= 3:
        items.append(f'(junction (at {p[0]} {p[1]}) (diameter 0) (color 0 0 0 0) (uuid "{U()}"))')


def inside(p, a, b):
    if a[0] == b[0] == p[0]:
        return min(a[1], b[1]) < p[1] < max(a[1], b[1])
    if a[1] == b[1] == p[1]:
        return min(a[0], b[0]) < p[0] < max(a[0], b[0])
    return False


for p in ends:
    for a, b in SEGS:
        if inside(p, a, b):
            print(f"WARNING: point {p} touches the middle of wire {a}-{b}")
for a, b in SEGS:
    if a == b:
        print(f"WARNING: zero-length wire at {a}")
    items.append(f'(wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})) (stroke (width 0) (type default)) (uuid "{U()}"))')

lib_symbols = "\n".join(LIBS[k] for k in LIBS)
doc = f"""(kicad_sch
	(version 20250610)
	(generator "eeschema")
	(generator_version "10.0")
	(uuid "{ROOT_UUID}")
	(paper "A2")
	(title_block (title "TARS4 — electronics") (date "2026-10-21") (rev "3") (comment 1 "LOLIN S3 Mini, TPS63020, 2 × 18650"))
	(lib_symbols
{lib_symbols}
	)
{chr(10).join(items)}
	(sheet_instances (path "/" (page "1")))
	(embedded_fonts no)
)
"""
open(OUT, "w").write(doc)
# project library with the module symbols (names without the "tars:" prefix), project file and library table
mods = [v.replace(f'(symbol "{k}"', f'(symbol "{k.split(":")[1]}"', 1) for k, v in LIBS.items() if k.startswith("tars:")]
open(os.path.join(ROOT, "kicad", "tars.kicad_sym"), "w").write(
    '(kicad_symbol_lib (version 20251024) (generator "kicad_symbol_editor") (generator_version "10.0")\n' + "\n".join(mods) + "\n)\n")
open(os.path.join(ROOT, "kicad", "sym-lib-table"), "w").write(
    '(sym_lib_table (version 7) (lib (name "tars") (type "KiCad") (uri "${KIPRJMOD}/tars.kicad_sym") (options "") (descr "TARS4 modules")))\n')
pro = os.path.join(ROOT, "kicad", "tars4.kicad_pro")
if not os.path.exists(pro):
    open(pro, "w").write('{\n  "meta": {\n    "filename": "tars4.kicad_pro",\n    "version": 3\n  }\n}\n')
print(f"{OUT}: {len(items)} items, {len(SEGS)} wires, {len(set(NETS.values()) - {'NC'})} nets")

# ---------------- native format + netlist comparison ----------------
if os.path.exists(KICAD):
    subprocess.run([KICAD, "kicad-cli", "sch", "upgrade", OUT], check=True, capture_output=True)
    with tempfile.TemporaryDirectory() as tmp:
        net = os.path.join(tmp, "t.net")
        subprocess.run([KICAD, "kicad-cli", "sch", "export", "netlist", "--format", "kicadsexpr", "-o", net, OUT], check=True, capture_output=True)
        text = open(net).read()
    got = defaultdict(set)
    for m in re.finditer(r'\(net\s+\(code "(\d+)"\)\s+\(name "([^"]*)"\)(.*?)\n\t\t\)', text, re.S):
        for r, p in re.findall(r'\(ref "([^"]+)"\)\s+\(pin "([^"]+)"\)', m.group(3)):
            if not r.startswith("#"):
                got[m.group(1)].add((r, p))
    want = defaultdict(set)
    for k, v in NETS.items():
        if v != "NC":
            want[v].add(k)
    gs, ws = {frozenset(s) for s in got.values() if len(s) > 1 or not any(NETS.get(x) == "NC" for x in s)}, {frozenset(s) for s in want.values()}
    if gs == ws:
        print(f"netlist OK: {len(ws)} nets match the nets dicts")
    else:
        for s in ws - gs:
            print("WARNING: expected net not found:", sorted(s), NETS[next(iter(s))])
        for s in gs - ws:
            print("WARNING: unexpected net:", sorted(s))
