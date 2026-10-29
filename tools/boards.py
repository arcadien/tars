"""Build drawings of the hand-wired boards: the S3's carrier, P1, P2 and the power-path board.

usage: python3 -I tools/boards.py        (writes renders/tars4_board_*.svg)

Each board is described hole by hole (column letter A.. from the left of the component side, row number 1.. from
the bottom / front): parts, solder bridges, bare buses, insulated jumpers, strip cuts and the harness wires. The
script checks the description before drawing it:
- every net is one connected group (strips + bridges + buses + jumpers), and no group carries two nets;
- no two leads share a hole, no lead sits under another part's body;
- on the pad boards, no hole of a power net (VUSB, VPATH, VSYS, OUT+, B+) is next to a hole of any other net (GND,
  a GPIO line, 3V3 or another power net), so a stray solder blob cannot short the cells, bypass Q1 / SW1 or put the
  battery on a GPIO;
- every part that is also in the KiCad schematic (tools/kicad_sch_gen.py) has its pins on the schematic's nets,
  under the same names (ALIAS: 3V3 = +3V3, VBAT/2 = VBAT_2, OUT+ = OUTP, B+ = BAT+), and every harness wire's net
  is a schematic net.
It stops with the list of problems if any check fails.
"""
import ast
import math
import re
import sys

P = 2.54
KIT = {  # wire colours of the kits (same values as tars4_wiring.html)
    'red': '#d7262b', 'black': '#1b1b1d', 'yellow': '#f5c400', 'green': '#23964a', 'blue': '#2a62d6',
    'white': '#fbfbf7', 'orange': '#f07800', 'brown': '#8a5326', 'purple': '#8e44c4', 'grey': '#9aa3a8'}
NAME = {c: c for c in KIT}  # colour names shown in the docs
INK, MUTED, SHEET, RULE = '#1d2226', '#5e676d', '#fbfbf9', '#c9cec9'
# rings: an int = that many black heat-shrink rings (signal buses: 1 I2S / PIR, 2 I2C, 3 microSD); a colour name = one
# coloured heat-shrink band on the + wire and its GND (power rails sharing the red / black pair: white OUT+, yellow
# VPATH, orange VSYS, purple VUSB; B+ / B− and the white / blue 3V3 pairs have none)


def rings_text(r):
    if not r:
        return ''
    if isinstance(r, str):
        return f', {NAME[r]} band'
    return f', {r} ring{"s" if r > 1 else ""}'
POWER = {'VUSB', 'VPATH', 'VSYS', 'OUT+', 'B+'}
GPIO = {'USB_DET', 'VBAT/2', 'SD_EN'}
# Connectors X1–X15 (harness side), pins from pin 1: (name, net); net 'key' = module pin pulled and cavity plugged,
# None = contact left empty (pin tied on the module), '|' = gap between two housings. A wire's 7th field lists the
# contacts it is crimped into ('X1.CS'); its net must be the contact's. X6 (speaker), X12 / X16 (cells) meet no board.
CONNS = {
    'X1': ('screen 1 · Dupont 1 × 8 on a right-angle header', [('GND', 'GND'), ('VCC', '3V3'), ('SCL', 'SCK1'), ('SDA', 'MOSI'), ('RES', 'RST'), ('DC', 'DC'), ('CS', 'CS1'), ('BLK', 'BL_EN')]),
    'X2': ('ADXL345 · Dupont 1 × 8, 5 wires', [('GND', 'GND'), ('VCC', '3V3'), ('CS', None), ('INT1', 'INT1'), ('INT2', 'key'), ('SDO', None), ('SDA', 'SDA'), ('SCL', 'SCL')]),
    'X3': ('INMP441 · pigtail + inline Dupont 1 × 6', [('SCK', 'MIC_BCLK'), ('WS', 'MIC_WS'), ('SD', 'MIC_SD'), ('VDD', '3V3'), ('GND', 'GND'), ('—', 'key')]),
    'X4': ('screen 2 · Dupont 1 × 8 on a right-angle header', [('GND', 'GND'), ('VCC', '3V3'), ('SCL', 'SCK2'), ('SDA', 'MOSI'), ('RES', 'RST'), ('DC', 'DC'), ('CS', 'CS2'), ('BLK', 'BL_EN')]),
    'X5': ('MAX98357A · Dupont 1 × 4 + 1 × 3', [('LRC', 'LRC'), ('BCLK', 'BCLK'), ('DIN', 'DIN'), ('GAIN', 'key'), ('|', '|'), ('SD', 'AMP_SD'), ('GND', 'GND'), ('VIN', 'VSYS')]),
    'X7': ('AM312 · pigtail + inline Dupont 1 × 4', [('VIN', 'PIR_VDD'), ('OUT', 'PIR_OUT'), ('GND', 'GND'), ('—', 'key')]),
    'X8': ('DS3231 · Dupont 1 × 6 on a right-angle header, 4 wires', [('32K', 'key'), ('SQW', None), ('SCL', 'SCL'), ('SDA', 'SDA'), ('VCC', '3V3'), ('GND', 'GND')]),
    'X9': ('BME280 · Dupont 1 × 4 (daisy-chained to X8)', [('VCC', '3V3'), ('GND', 'GND'), ('SCL', 'SCL'), ('SDA', 'SDA')]),
    'X10': ('J1 + SW1 · inline JST-XH 4', [('VUSB', 'VUSB'), ('GND', 'GND'), ('VPATH', 'VPATH'), ('VSYS', 'VSYS')]),
    'X13': ('power block outputs · inline JST-XH 4', [('VSYS', 'VSYS'), ('GND amp', 'GND'), ('3V3', '3V3'), ('GND log', 'GND')]),
    'X14': ('measurements · inline JST-XH 4', [('VBAT/2', 'VBAT/2'), ('USB_DET', 'USB_DET'), ('SD_EN', 'SD_EN'), ('VSENSE_B', 'VSENSE_B')]),
    'X15': ('microSD · pigtail + inline Dupont 1 × 6', [('CLK', 'SD_CLK'), ('CMD', 'SD_CMD'), ('D0', 'SD_D0'), ('3V3', 'SD_3V3'), ('GND', 'GND'), ('—', 'key')]),
    'X6': ('speaker · Dupont 1 × 2 on a header', [('+', 'SPK+'), ('−', 'SPK−')]),
    'X12': ('left cell · inline JST-XH 2', [('B+', 'B+'), ('B−', 'B−')]),
    'X16': ('right cell · inline JST-XH 2', [('B+', 'B+'), ('B−', 'B−')]),
}
XH = {'X10', 'X12', 'X13', 'X14', 'X16'}
CCOL = {'X1': 1, 'X2': 1, 'X3': 1, 'X4': 2, 'X5': 2, 'X6': 2, 'X7': 2, 'X8': 3, 'X9': 3, 'X10': 0, 'X12': 0, 'X13': 0,
        'X14': 0, 'X15': 0, 'X16': 0}  # TARS column of each connector (0 = left leg … 3 = right leg)


def gender(ref, board_key=None, side=None):
    """contact gender at the harness end of a wire: female everywhere (onto the modules' pins, or the powered side of
    an inline pair) except the XH pairs' other side: X10 / X13 / X14 are female on the power block, X12 / X16 on the
    cells"""
    if side:
        return side
    if ref in ('X10', 'X13', 'X14'):
        return 'F' if board_key == 'power' else 'M'
    return 'F'


def pin_no(ref, name):
    """contact number from pin 1 (the gap between two housings is not counted)"""
    return [p for p, _ in CONNS[ref][1] if p != '|'].index(name) + 1


def h(name):
    """'B7' -> (column 1, row 6)"""
    return ord(name[0]) - 65, int(name[1:]) - 1


def hn(c, r):
    return f'{chr(65 + c)}{r + 1}'


# ----------------------------------------------------------------------------------------------------------------
# Board descriptions. Parts: (ref, kind, value, {pin: (hole, net)}, note). kinds: R (axial, flat), Rv (standing),
# C (radial electrolytic, pin '+' / '-'), Cc (ceramic), D (axial diode, pins A / K), Q (SOT-23 glued upside down at
# '_at', its D pin facing '_d' (N = back / up in the drawing, E, S, W), pins G / S / D wired with insulated 30 AWG
# wire-wrap wire, drawn through the holes listed in '_via'), HDR (female header, pins listed with their net). Pin keys
# starting with '_' are not pins.
# Links: (kind, [holes], label). kinds: bridge (solder bridge between neighbours), bus (bare tinned wire along the
# holes), jumper (insulated wire), link (bare wire on the component side). All on the copper side except 'link'.
# Wires: (hole, net, colour, gauge, rings, destination[, connector contacts]).
# ----------------------------------------------------------------------------------------------------------------

S3_PINS = {  # LOLIN S3 Mini, seen from its component side, USB-C at the bottom (rows 4-11 of the carrier)
    0: ['3V', 'IO10', 'IO11', 'IO13', 'IO12', 'IO4', 'IO2', 'EN'],
    1: ['IO14', 'IO9', 'IO8', 'IO7', 'IO6', 'IO5', 'IO3', 'IO1'],
    8: ['IO15', 'G', 'IO17', 'IO21', 'IO34', 'IO38', 'IO37', 'IO33'],
    9: ['V', 'G', 'IO16', 'IO18', 'IO35', 'IO36', 'IO44', 'IO43']}
S3_NET = {'3V': '3V3', 'G': 'GND', 'IO10': 'CS1', 'IO11': 'MOSI_S3', 'IO13': 'DC', 'IO12': 'SCK_S3', 'IO4': 'AMP_SD_S3',
          'IO2': 'INT1', 'IO14': 'MIC_BCLK', 'IO9': 'CS2', 'IO8': 'RST', 'IO7': 'BL_EN', 'IO6': 'SCL', 'IO5': 'SDA',
          'IO3': 'PIR', 'IO1': 'VBAT/2', 'IO15': 'MIC_SD', 'IO17': 'LRC_S3', 'IO21': 'USB_DET', 'IO34': 'SD_CMD',
          'IO38': 'MIC_WS', 'IO37': 'VSENSE', 'IO33': 'SD_CLK_S3', 'IO16': 'DIN', 'IO18': 'BCLK_S3', 'IO35': 'SD_D0', 'IO36': 'SD_EN'}
s3_hdr = {}
for c, names in S3_PINS.items():
    for k, n in enumerate(names):
        s3_hdr[n + ('' if n != 'G' else str(c))] = (hn(c, 3 + k), S3_NET.get(n))

CARRIER = dict(
    key='s3', title='P3 · LOLIN S3 Mini carrier', size=(25.6, 34.4), grid=(10, 13), strips=False, lpad=24, rowpad=24,
    my0=1.22,  # bottom margin: row 4 (first S3 pin row) 8.8 mm above the USB edge, as on the LOLIN drawing
    sub='single-sided pad perfboard (one pad per hole), 25.6 × 34.4 mm, 10 × 13 holes · left middle, z 8.1–42.5',
    comp='component side: TARS front (towards the S3), the headers and the standing parts under the S3',
    copper='solder side: towards the lid, all the wires and links',
    keep=[('A3', 'lid tab'), ('J3', 'lid tab'), ('A12', 'lid tab'),
          ('J12', 'lid tab'), ('J4', 'V (VBUS): contact pulled out of the header')],
    keep_note='bands 4.5–7 and 27.9–30.4 mm (rows 3 and 12): the lid tabs press on the edges, solder side; rows 12–13 under the antenna: nothing',
    parts=[
        ('X', 'HDR', '2 × 8 female', {k: v for k, v in s3_hdr.items() if v[0][0] in 'AB'}, 'left header (EN … 3V)'),
        ('X', 'HDR', '2 × 8 female', {k: v for k, v in s3_hdr.items() if v[0][0] in 'IJ'}, 'right header (33 … V)'),
        ('R12', 'Rv', '47 Ω', {'1': ('C8', 'SCK_S3'), '2': ('C7', 'SCK1')}, 'SCK → screen 1'),
        ('R19', 'Rv', '47 Ω', {'1': ('D8', 'SCK_S3'), '2': ('D7', 'SCK2')}, 'SCK → screen 2'),
        ('R20', 'Rv', '33 Ω', {'1': ('C9', 'MOSI_S3'), '2': ('C10', 'MOSI')}, 'MOSI, in series (softer edges, SPI at 40 MHz)'),
        ('C6', 'Cc', '100 nF', {'1': ('C11', 'VBAT/2'), '2': ('D11', 'GND')}, 'GPIO1 → GND, small ceramic (no tantalum, no film: too wide)'),
        ('C1', 'C', '220 µF CMS 7343', {'+': ('C2', '3V3'), '-': ('E2', 'GND')}, 'SMD tantalum 7.3 × 4.3 lying flat under the S3, band (+) on the C2 side; a lead offcut soldered on each end, through C2 / E2 (Panasonic POSCAP 10TPE220ML, 10 V polymer, ESR 25 mΩ)'),
        ('R11', 'Rv', '33 Ω', {'1': ('H11', 'SD_CLK_S3'), '2': ('G11', 'SD_CLK')}, 'SD_CLK'),
        ('C8', 'Cc', '100 nF', {'1': ('H7', 'USB_DET'), '2': ('G7', 'GND')}, 'GPIO21 → GND, small ceramic (no film: too wide)'),
        ('R14', 'Rv', '33 Ω', {'1': ('H6', 'LRC_S3'), '2': ('G6', 'LRC')}, 'LRC'),
        ('R13', 'Rv', '33 Ω', {'1': ('H4', 'BCLK_S3'), '2': ('G4', 'BCLK')}, 'BCLK'),
        ('Q4', 'T', 'BC547B', {'E': ('F10', 'GND'), 'B': ('G10', 'VSENSE_B'), 'C': ('H10', 'VSENSE'), '_flat': 'N'},
         'VSYS sense: standing, flat face towards row 11 (C B E from left to right seen from that side); C bridged to IO37'),
        ('R24', 'Rv', '330 kΩ', {'1': ('G9', 'VSENSE_B'), '2': ('F9', 'GND')}, 'VSYS sense: base → GND (threshold 2.3–2.7 V)'),
    ],
    links=[
        ('jumper', ['A8', 'C8'], 'J1 SCK'), ('bridge', ['C8', 'D8'], ''),
        ('jumper', ['A4', 'C2'], 'J2 3V3 → C1'),
        ('jumper', ['J7', 'H4'], 'J3 BCLK'), ('jumper', ['A6', 'C9'], 'J4 MOSI → R20'),
        ('bridge', ['B11', 'C11'], ''), ('bridge', ['D11', 'E11'], ''),
        ('bus', [f'E{r}' for r in range(2, 12)], 'GND'),
        ('bridge', ['E5', 'F5', 'G5', 'H5', 'I5'], ''), ('bridge', ['I5', 'J5'], ''),
        ('bridge', ['E7', 'F7', 'G7'], ''), ('bridge', ['H7', 'I7'], ''),
        ('bridge', ['H6', 'I6'], ''), ('bridge', ['H11', 'I11'], ''),
        ('bridge', ['H10', 'I10'], ''), ('bridge', ['F10', 'E10'], ''), ('bridge', ['F9', 'E9'], ''),
        ('bridge', ['G8', 'G9', 'G10'], ''),
    ],
    wires=[  # hole, net, colour, gauge, rings, destination
        ('A4', '3V3', 'white', 26, 0, 'P1 3V3'), ('J5', 'GND', 'blue', 26, 0, 'P1 GND'),
        ('A10', 'INT1', 'red', 30, 0, 'X2 ADXL345 INT1', ['X2.INT1']), ('A9', 'AMP_SD_S3', 'brown', 30, 1, 'middle tube → P2 A11 (before R10)'),
        ('A7', 'DC', 'red', 30, 0, 'P1 DC'), ('C10', 'MOSI', 'green', 30, 0, 'P1 MOSI (after R20)'),
        ('A5', 'CS1', 'purple', 30, 0, 'X1 screen 1 CS', ['X1.CS']),
        ('B11', 'VBAT/2', 'brown', 30, 0, 'left tube → X14', ['X14.VBAT/2']), ('B10', 'PIR', 'red', 30, 1, 'middle tube → P2 A4 (before R17)'),
        ('B9', 'SDA', 'green', 30, 2, 'X2 ADXL345 SDA', ['X2.SDA']), ('B8', 'SCL', 'yellow', 30, 2, 'X2 ADXL345 SCL', ['X2.SCL']),
        ('B7', 'BL_EN', 'brown', 30, 0, 'P1 BL_EN'), ('B6', 'RST', 'orange', 30, 0, 'P1 RST'),
        ('B5', 'CS2', 'purple', 30, 0, 'middle tube → X4 screen 2 CS', ['X4.CS']), ('B4', 'MIC_BCLK', 'yellow', 30, 1, 'X3 mic SCK', ['X3.SCK']),
        ('C7', 'SCK1', 'yellow', 30, 0, 'X1 screen 1 SCL', ['X1.SCL']), ('D7', 'SCK2', 'yellow', 30, 0, 'middle tube → X4 screen 2 SCL', ['X4.SCL']),
        ('I9', 'MIC_WS', 'purple', 30, 1, 'X3 mic WS', ['X3.WS']), ('I8', 'SD_CMD', 'purple', 30, 3, 'left tube → X15 CMD', ['X15.CMD']),
        ('I7', 'USB_DET', 'orange', 30, 0, 'left tube → X14', ['X14.USB_DET']), ('I4', 'MIC_SD', 'green', 30, 1, 'X3 mic SD', ['X3.SD']),
        ('J9', 'SD_EN', 'brown', 30, 3, 'left tube → X14', ['X14.SD_EN']), ('J8', 'SD_D0', 'green', 30, 3, 'left tube → X15 D0', ['X15.D0']),
        ('J6', 'DIN', 'green', 30, 1, 'middle tube → X5 amplifier DIN', ['X5.DIN']),
        ('G11', 'SD_CLK', 'yellow', 30, 3, 'left tube → X15 CLK', ['X15.CLK']), ('G6', 'LRC', 'purple', 30, 1, 'middle tube → X5 amplifier LRC', ['X5.LRC']),
        ('G4', 'BCLK', 'yellow', 30, 1, 'middle tube → X5 amplifier BCLK', ['X5.BCLK']),
        ('G8', 'VSENSE_B', 'brown', 30, 1, 'left tube → X14 (R23 at the power-path board end)', ['X14.VSENSE_B']),
    ],
    notes=[
        'Assemble in this order: female headers (component side, square: plug them onto the S3 to solder), parts, bridges, GND bus (tinned wire along column E), insulated jumpers, then the wires. Everything is done on the bench, carrier out of TARS.',
        'Cut: 1.2 mm below row 1 and 2.7 mm above row 13, so the bottom edge is flush with the S3 USB edge (row 4 = first pin row, 8.8 mm above that edge; check on the S3).',
        'Single-sided board: only the solder-side pads hold the headers. Glue each header to the board (cyanoacrylate or epoxy) once soldered, and hold the carrier to plug or pull the S3.',
        'Before soldering the right header, remove the V contact (J4, USB-C VBUS): pushed out of the plastic from below, or cut flush. The PC 5 V never reaches the carrier (J4 sits between GND J5 and MIC_SD I4).',
        'Standing resistors (2.54 pitch), body under the S3: height ≤ 10 mm (11 mm free between carrier and S3). Headers soldered first, then the standing parts bent towards the centre: R11–R14, R12, R20, C6 and C8 brush the header plastic (~0.1 mm).',
        'Each wire is soldered to the tail of its pin or to its pad, solder side, then first runs flat inwards (columns C–H) before going up or down: nothing within 5 mm of the left and right edges in bands 4.5–7 and 27.9–30.4 (lid tabs). Service loop 6–8 cm.',
        'IO37 (I10) is the VSYS sense (Q4, R24; R23 sits in the harness at the power-path board end). EN (A11), IO43 / IO44 (J11, J10) stay free: EN is the reset, not BL_EN.',
        'Ohmmeter check, S3 removed: each wire ↔ its pin; GND (bus E) isolated from 3V3 (> 1 kΩ with C1 charged) and from every signal, in particular BCLK (H4) and LRC (H6) on either side of the row 5 GND bridge, and VBAT/2 (B11) ↔ EN (A11).',
    ])

P1 = dict(
    key='p1', title='P1 · left middle distribution', size=(24, 32), grid=(9, 12), strips=True, lpad=40,
    sub='stripboard, 24 × 32 mm, 9 × 12 holes, horizontal strips · standing under screen 1, z 139.9–171.9',
    comp='component side: towards the front, the wires enter through the holes',
    copper='copper side: towards the lid, wires and leads are soldered there',
    keep=[], keep_note='left and right edges: lid tabs and stops (≈ 1.5 mm), no hole used in column A / I on rows 1 and 12',
    parts=[
        ('R4', 'R', '10 k', {'1': ('E8', 'BL_EN'), '2': ('E11', 'GND')}, 'BL_EN → GND, lying (7.62 pitch)'),
        ('C2', 'C', '10 µF 16 V', {'+': ('G9', '3V3'), '-': ('G10', 'GND')}, '16 V tantalum, + at G9 (3V3); or X5R / X7R ceramic ≥ 6.3 V, 2.54 pitch'),
        ('C3', 'Cc', '100 nF', {'1': ('H9', '3V3'), '2': ('H10', 'GND')}, 'decoupling, ceramic (as a fallback: 5.08-pitch film at H9–H11)'),
    ],
    links=[('link', ['I10', 'I11'], 'GND 10–11')],
    cuts=[],
    wires=[
        ('A10', 'GND', 'blue', 30, 0, 'X1 screen 1 GND', ['X1.GND']), ('B10', 'GND', 'blue', 26, 0, 'S3 G (J5)'),
        ('C10', 'GND', 'blue', 26, 0, 'left tube → TPS63020 GND (X13)', ['X13.GND log']),
        ('B11', 'GND', 'blue', 30, 3, 'left tube → X15 microSD GND (twisted with CLK)', ['X15.GND']),
        ('C11', 'GND', 'blue', 30, 0, 'middle tube → P2 GND'), ('D11', 'GND', 'blue', 30, 0, 'X3 mic GND (→ ADXL345)', ['X3.GND']),
        ('A9', '3V3', 'white', 30, 0, 'X1 screen 1 VCC', ['X1.VCC']), ('B9', '3V3', 'white', 26, 0, 'S3 3V (A4)'),
        ('C9', '3V3', 'white', 26, 0, 'left tube → TPS63020 VOUT (X13)', ['X13.3V3']), ('D9', '3V3', 'white', 30, 0, 'X3 mic VDD (→ ADXL345)', ['X3.VDD']),
        ('F9', '3V3', 'white', 30, 0, 'middle tube → P2 3V3'),
        ('A8', 'BL_EN', 'brown', 30, 0, 'S3 IO7 (B7)'), ('B8', 'BL_EN', 'brown', 30, 0, 'X1 screen 1 BLK', ['X1.BLK']),
        ('C8', 'BL_EN', 'brown', 30, 0, 'middle tube → X4 screen 2 BLK', ['X4.BLK']),
        ('A7', 'DC', 'red', 30, 0, 'S3 IO13 (A7)'), ('B7', 'DC', 'red', 30, 0, 'X1 screen 1 DC', ['X1.DC']),
        ('C7', 'DC', 'red', 30, 0, 'middle tube → X4 screen 2 DC', ['X4.DC']),
        ('A6', 'RST', 'orange', 30, 0, 'S3 IO8 (B6)'), ('B6', 'RST', 'orange', 30, 0, 'X1 screen 1 RES', ['X1.RES']),
        ('C6', 'RST', 'orange', 30, 0, 'middle tube → X4 screen 2 RES', ['X4.RES']),
        ('A5', 'MOSI', 'green', 30, 0, 'S3 IO11 (C10, after R20)'), ('B5', 'MOSI', 'green', 30, 0, 'X1 screen 1 SDA', ['X1.SDA']),
        ('C5', 'MOSI', 'green', 30, 0, 'middle tube → X4 screen 2 SDA', ['X4.SDA']),
    ],
    strip_names={10: 'GND', 9: 'GND', 8: '3V3', 7: 'BL_EN', 6: 'DC', 5: 'RST', 4: 'MOSI'},
    notes=[
        'Strips 1–4 and 12 free (spare: Q2 / Q3 if the screens BLK draws the LED current). No cut.',
        'Wires pushed through from the component side, soldered on the copper side; 26 AWG goes into the 1 mm holes without forcing. Columns A and I: 30 AWG only, bent inwards right out of the hole (the front stops cover 1.5 mm of each edge).',
        'Part height ≤ 9 mm on the component side (10.4 mm up to the front wall).',
        'Bare link I10–I11 on the component side: strips 10 and 11 form a single GND (11 solder holes for 6 GND wires and 3 leads).',
    ])

P2 = dict(
    key='p2', title='P2 · right middle distribution', size=(24, 32), grid=(9, 12), strips=True, lpad=100, gap=150,
    sub='stripboard, 24 × 32 mm, 9 × 12 holes, horizontal strips · standing under screen 2, z 139.9–171.9',
    comp='component side: towards the front, the wires enter through the holes',
    copper='copper side: towards the lid, wires and leads are soldered there',
    keep=[], keep_note='left and right edges: lid tabs and stops (≈ 1.5 mm)',
    parts=[
        ('R10', 'Rv', '1 k', {'1': ('B11', 'AMP_SD_S3'), '2': ('D11', 'AMP_SD')}, 'in series, standing, straddles the C11 cut'),
        ('R18', 'Rv', '10 k', {'1': ('E11', 'AMP_SD'), '2': ('E10', 'GND')}, 'AMP_SD → GND, standing'),
        ('C10', 'C', '10 µF 16 V', {'+': ('F9', '3V3'), '-': ('F10', 'GND')}, '16 V tantalum, + at F9 (3V3); or X5R / X7R ceramic ≥ 6.3 V'),
        ('C11', 'Cc', '100 nF', {'1': ('G9', '3V3'), '2': ('G10', 'GND')}, 'decoupling, ceramic'),
        ('R21', 'R', '100 Ω', {'1': ('H9', '3V3'), '2': ('H6', 'PIR_VDD')}, 'AM312 filter, lying (7.62 pitch)'),
        ('C12', 'C', '10 µF 16 V', {'+': ('F6', 'PIR_VDD'), '-': ('F5', 'GND')}, 'AM312 filter, 16 V tantalum (+ at F6); or 47 µF electrolytic Ø5 × 7 at most'),
        ('R17', 'Rv', '1 k', {'1': ('B4', 'PIR'), '2': ('D4', 'PIR_OUT')}, 'in series, standing, straddles the C4 cut'),
    ],
    links=[('jumper', ['I10', 'I5'], 'GND 10 ↔ 5')],
    cuts=['C11', 'C4'],
    wires=[
        ('A11', 'AMP_SD_S3', 'brown', 30, 1, 'middle tube → S3 IO4 (A9)'), ('F11', 'AMP_SD', 'brown', 30, 1, 'X5 amplifier SD', ['X5.SD']),
        ('A10', 'GND', 'blue', 30, 0, 'middle tube → P1 GND'), ('B10', 'GND', 'blue', 30, 0, 'X4 screen 2 GND', ['X4.GND']),
        ('C10', 'GND', 'blue', 30, 0, 'right tube → X8 DS3231 / X9 BME280 GND', ['X9.GND', 'X8.GND']), ('D10', 'GND', 'blue', 30, 0, 'X7 AM312 GND', ['X7.GND']),
        ('A9', '3V3', 'white', 30, 0, 'middle tube → P1 3V3'), ('B9', '3V3', 'white', 30, 0, 'X4 screen 2 VCC', ['X4.VCC']),
        ('C9', '3V3', 'white', 30, 0, 'right tube → X8 / X9 VCC', ['X9.VCC', 'X8.VCC']),
        ('A8', 'SDA', 'green', 30, 2, 'middle tube → ADXL345 SDA', ['X2.SDA']), ('C8', 'SDA', 'green', 30, 2, 'right tube → X9 / X8 SDA', ['X9.SDA', 'X8.SDA']),
        ('A7', 'SCL', 'yellow', 30, 2, 'middle tube → ADXL345 SCL', ['X2.SCL']), ('C7', 'SCL', 'yellow', 30, 2, 'right tube → X9 / X8 SCL', ['X9.SCL', 'X8.SCL']),
        ('D6', 'PIR_VDD', 'white', 30, 0, 'X7 AM312 VIN', ['X7.VIN']),
        ('A4', 'PIR', 'red', 30, 1, 'middle tube → S3 IO3 (B10)'), ('F4', 'PIR_OUT', 'red', 30, 1, 'X7 AM312 OUT', ['X7.OUT']),
    ],
    strip_names={10: 'AMP_SD_S3 | AMP_SD', 9: 'GND', 8: '3V3', 7: 'SDA', 6: 'SCL', 5: 'PIR_VDD', 4: 'GND', 3: 'PIR | PIR_OUT'},
    notes=[
        'Cuts at C11 and C4 (3 mm drill turned by hand on the copper side): R10 and R17 are in series in their strip.',
        'Insulated jumper I10 → I5 on the copper side (the lid tabs only touch rows 1 and 12): strips 10 and 5 are both GND (C12 needs a GND next to PIR_VDD).',
        'Strips 1–3 and 12 free (spare).',
        'The S3 wire arrives before the series resistor (A11 AMP_SD_S3, A4 PIR), the module one after it (F11 AMP_SD, F4 PIR_OUT): don\'t swap them, otherwise R10 / R17 are shorted.',
        'Part height ≤ 9 mm on the component side (10.4 mm up to the front wall); columns A and I: wires bent inwards right out of the hole (front stops).',
        'The SPI, CS2, BL_EN and I2S wires of screen 2 / the amplifier don\'t go through P2: tube → connector directly.',
    ])

POWER_BOARD = dict(
    key='power', title='P4 · power-path board', size=(26.6, 20), grid=(10, 8), strips=False,
    sub='single-sided pad perfboard, 26.6 × 20 mm, 10 × 8 holes · flat in the left leg, z 170.8, parts on top',
    comp='top view, component side: TARS front at the bottom, TARS left on the left',
    copper='solder side (underneath): bridges, GND bus and all the wires, which leave towards the front',
    keep=[('J3', 'attache de toron'), ('J4', 'attache de toron'), ('J5', 'attache de toron'), ('J6', 'attache de toron')],
    keep_note='column J, rows 3–6: the harness clip (z 179) passes 4 mm above: lying parts only',
    parts=[
        ('D1', 'D', '1N5822', {'K': ('A7', 'VPATH'), 'A': ('F7', 'VUSB')}, 'lying, band on the A7 side (axis 3.6 mm from the back edge); holes drilled to 1.3 mm, leads bent with flat pliers'),
        ('Q1', 'Q', 'AO3401A', {'S': ('A5', 'VPATH'), 'G': ('E5', 'VUSB'), 'D': ('B4', 'OUT+'), '_at': 'C5', '_d': 'N', '_via': {'D': ['B6']}}, 'glued legs up on C5–D5, D towards the back: G to the east (→ E5), S to the west (→ A5), D goes round by the west to B4'),
        ('R15', 'R', '68 k', {'1': ('F5', 'VUSB'), '2': ('F2', 'USB_DET')}, 'VUSB → USB_DET'),
        ('R16', 'R', '100 k', {'1': ('E2', 'USB_DET'), '2': ('B2', 'GND')}, 'USB_DET → GND'),
        ('R1', 'R', '4.7 k', {'1': ('G7', 'VUSB'), '2': ('G4', 'GND')}, 'Q1 gate → GND'),
        ('R3', 'R', '1 M', {'1': ('I4', 'VBAT/2'), '2': ('I1', 'GND')}, 'VBAT/2 → GND'),
        ('R22', 'R', '100 k', {'1': ('H8', '3V3'), '2': ('H5', 'SD_EN')}, 'grille de Q5 → 3V3'),
        ('Q5', 'Q', 'AO3401A', {'S': ('H8', '3V3'), 'G': ('H5', 'SD_EN'), 'D': ('I6', 'SD_3V3'), '_at': 'I7', '_d': 'E'}, 'glued legs up on I7, D to the right: S towards the back (→ H8), G towards the front (→ H5), D comes back down at I6'),
    ],
    links=[
        ('bridge', ['A8', 'A7', 'A6', 'A5'], ''),
        ('bridge', ['F8', 'F7', 'F6', 'F5'], ''), ('bridge', ['F5', 'E5'], ''), ('bridge', ['F7', 'G7'], ''),
        ('bridge', ['C3', 'D3'], ''),
        ('bridge', ['E2', 'F2'], ''),
        ('bridge', ['B2', 'B1'], ''), ('bridge', ['G4', 'G3', 'G2', 'G1'], ''),
        ('bus', [f'{chr(65 + c)}1' for c in range(10)], 'GND'),
        ('bridge', ['J5', 'J4'], ''), ('bridge', ['I4', 'J4'], ''), ('bridge', ['J4', 'J3'], ''),
        ('bridge', ['D3', 'D4'], ''),
    ],
    wires=[
        ('F8', 'VUSB', 'red', 26, 'purple', 'TP4056 IN+ (VUSB)'), ('B4', 'OUT+', 'red', 26, 'white', 'TP4056 OUT+'),
        ('A8', 'VPATH', 'red', 26, 'yellow', 'X10 → switch SW1 (VPATH)', ['X10.VPATH']),
        ('D3', 'VSYS', 'red', 26, 'orange', 'X10 ← switch SW1 (VSYS)', ['X10.VSYS']), ('C3', 'VSYS', 'red', 26, 'orange', 'TPS63020 VIN'),
        ('C3', 'VSYS', 'red', 26, 'orange', 'X13 → amplifier VIN (twisted pair)', ['X13.VSYS']),
        ('C1', 'GND', 'black', 26, 'white', 'TP4056 OUT−'), ('D1', 'GND', 'black', 26, 'orange', 'TPS63020 GND'),
        ('E1', 'GND', 'black', 26, 'orange', 'X13 → amplifier GND (twisted pair)', ['X13.GND amp']),
        ('J5', 'VBAT/2', 'brown', 30, 0, 'TP4056 B+ pad (R2 1 MΩ in line at the pad end)', [], {'inline': ('R2', '1 MΩ', 'B+', 'far')}), ('J3', 'VBAT/2', 'brown', 30, 0, 'X14 → left tube → S3 IO1', ['X14.VBAT/2']),
        ('E2', 'USB_DET', 'orange', 30, 0, 'X14 → left tube → S3 IO21', ['X14.USB_DET']),
        ('H8', '3V3', 'white', 30, 0, 'TPS63020 VOUT'), ('I6', 'SD_3V3', 'white', 30, 3, 'X15 → microSD reader VCC', ['X15.3V3']),
        ('H5', 'SD_EN', 'brown', 30, 3, 'X14 → left tube → S3 IO36', ['X14.SD_EN']),
        ('D4', 'VSYS', 'brown', 30, 1, 'R23 1 MΩ in line (heat-shrink, at this end) → X14 → left tube → carrier G8 (VSENSE_B)',
         ['X14.VSENSE_B'], {'inline': ('R23', '1 MΩ', 'VSENSE_B')}),
    ],
    notes=[
        'Single-sided board, copper underneath: no copper under Q1 / Q5 nor under the part bodies.',
        'Lying parts (1/4 W, 7.62 pitch), D1 lying (Ø5.3): height ≤ 6 mm. Q1 and Q5 (SOT-23) glued legs up in the drawn orientation (seen from the top, flipped: G / S / D on the sketch), linked with insulated 30 AWG wire-wrap wire (Kynar), stripped 2 mm at each end (one touch of the iron each); glue on top once tested.',
        'The underside carries the GND bus (tinned wire along row 1: the ground star), the bridges and all the wires, which leave towards the front (row 1) then go up or down in the front corridor.',
        'Holes left empty between the power nets and ground / the GPIOs: don\'t fill them with solder.',
        'Check to GND, without the modules: VUSB ≈ 9.4 kΩ (R1 ∥ R15 + R16), USB_DET ≈ 44 kΩ, VBAT/2 ≈ 1 MΩ, B+ ≈ 2 MΩ, VPATH / VSYS / OUT+ > 1 MΩ; OUT+ ↔ VSYS and OUT+ ↔ VPATH open.',
    ])

BOARDS = [CARRIER, P1, P2, POWER_BOARD]


# ----------------------------------------------------------------------------------------------------------------
def inline(rest):
    """(ref, value, net after it[, 'far']) of a resistor soldered in line in the wire, near its board end (or its far
    end with 'far'), or None"""
    return rest[5].get('inline') if len(rest) > 5 else None


def check(b):
    cols, rows = b['grid']
    parent = {}

    def f(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def u(a, c):
        parent[f(a)] = f(c)

    errs = []
    cuts = {h(x) for x in b.get('cuts', [])}
    if b['strips']:
        for r in range(rows):
            seg = None
            for c in range(cols):
                if (c, r) in cuts:
                    seg = None
                    continue
                if seg is not None:
                    u(seg, (c, r))
                seg = (c, r)
    for kind, holes, _ in b['links']:
        hs = [h(x) for x in holes]
        for a, c in zip(hs, hs[1:]):
            if kind == 'bridge' and abs(a[0] - c[0]) + abs(a[1] - c[1]) != 1:
                errs.append(f'bridge {hn(*a)}-{hn(*c)} not between neighbours')
            u(a, c)
    tags = {}   # hole -> set of nets
    leads = {}  # hole -> refs with a lead in it (component side)
    for ref, kind, val, pins, note in b['parts']:
        for pin, v in pins.items():
            if pin.startswith('_') or v[1] is None:
                continue
            hole, net = h(v[0]), v[1]
            tags.setdefault(hole, set()).add(net)
            if kind != 'Q':
                leads.setdefault(hole, []).append(ref + ':' + pin)
    seen_pin = {}
    for hole, net, *rest in b['wires']:
        tags.setdefault(h(hole), set()).add(net)
        far = inline(rest)[2] if inline(rest) else net   # a resistor in line in the harness changes the net
        for t in (rest[4] if len(rest) > 4 else []):
            ref, pin = t.split('.', 1)
            pn = dict(CONNS.get(ref, ('', []))[1])
            if pin not in pn:
                errs.append(f'wire {hole}: no contact {t}')
            elif pn[pin] != far:
                errs.append(f'wire {hole} ({net}) crimped into {t}, which is {pn[pin]}')
            elif t in seen_pin:
                errs.append(f'{t} gets two wires of this board ({seen_pin[t]}, {hole})')
            seen_pin[t] = hole
    for hole, refs in leads.items():
        if len(refs) > 1:
            errs.append(f'{hn(*hole)} holds two leads {refs}')
    for x in tags:
        f(x)
    groups = {}
    for x, nets in tags.items():
        groups.setdefault(f(x), set()).update(nets)
    for g, nets in groups.items():
        if len(nets) > 1:
            errs.append(f'short: {sorted(nets)} in one group (around {hn(*g)})')
    where = {}
    for x, nets in tags.items():
        for n in nets:
            where.setdefault(n, set()).add(f(x))
    for n, gs in where.items():
        if len(gs) > 1:
            errs.append(f'net {n} split in {len(gs)} groups')
    # leads under axial bodies (and capacitors spanning more than one pitch)
    for ref, kind, val, pins, note in b['parts']:
        if kind in ('R', 'D', 'Cc'):
            (a, b2) = [h(v[0]) for k, v in pins.items() if not k.startswith('_')]
            if a[0] == b2[0] or a[1] == b2[1]:
                n = max(abs(a[0] - b2[0]), abs(a[1] - b2[1]))
                for k in range(1, n):
                    x = (a[0] + (b2[0] - a[0]) * k // n, a[1] + (b2[1] - a[1]) * k // n)
                    if x in leads:
                        errs.append(f'{ref} body over the lead {leads[x]} in {hn(*x)}')
                    if b['strips'] and any(w[0] == hn(*x) for w in b['wires']):
                        errs.append(f'{ref} body over a wire entering {hn(*x)}')  # wires enter from the component side
    # hazards on pad boards: a power net next to any other net
    if not b['strips']:
        hole_net = {}
        for x in set(parent):
            g = f(x)
            if g in groups and len(groups[g]) == 1:
                hole_net[x] = next(iter(groups[g]))
        for (c, r), n in hole_net.items():
            for dc, dr in ((1, 0), (0, 1)):
                m = hole_net.get((c + dc, r + dr))
                if m and m != n:
                    pair = {n, m}
                    if pair & POWER:
                        errs.append(f'hazard: {n} at {hn(c, r)} next to {m} at {hn(c + dc, r + dr)}')
    return errs, groups


PIN_SCH = {'C': {'+': '1', '-': '2'}, 'D': {'K': '1', 'A': '2'}}  # board pin name -> schematic pin number


def sch_nets(path='tools/kicad_sch_gen.py'):
    """(ref, pin) -> net of the schematic, read from the generator's place() calls (without running it)."""
    src = open(path, encoding='utf-8').read()
    nets = {}
    for ref, d in re.findall(r'place\("[^"]+", "(\w+)", "[^"]*", [^{}]*?(\{[^{}]*\})', src):
        for pin, net in ast.literal_eval(d).items():
            nets[(ref, pin)] = net
    for ref, a, b2 in re.findall(r'\("(R\d+)", "(\w+)", "(\w+)", \d+, "\d+"\)', src):  # the 33 Ω loop
        nets[(ref, '1')], nets[(ref, '2')] = a, b2
    return nets


ALIAS = {'3V3': '+3V3', 'VBAT/2': 'VBAT_2', 'OUT+': 'OUTP', 'B+': 'BAT+'}  # board name -> schematic name


def crosscheck(boards):
    """Every board part found in the schematic sits on the same nets, and every board / wire net exists there."""
    sch = sch_nets()
    refs = {r for r, _ in sch}
    names = set(open('tools/kicad_sch_gen.py', encoding='utf-8').read().split('"')) | set(sch.values())
    errs = []
    for b in boards:
        for ref, kind, val, pins, note in b['parts']:
            if ref not in refs:
                if kind != 'HDR':
                    errs.append(f'{b["key"]}: {ref} is not in the schematic')
                continue
            for pin, v in pins.items():
                if pin.startswith('_'):
                    continue
                sp = PIN_SCH.get(kind, {}).get(pin, pin)
                sn = sch.get((ref, sp))
                if sn is None:
                    errs.append(f'{b["key"]}: {ref} pin {pin} has no net in the schematic')
                    continue
                if ALIAS.get(v[1], v[1]) != sn:
                    errs.append(f'{b["key"]}: {ref} pin {pin} on {v[1]}, schematic says {sn}')
        for w in b['wires']:
            for n in [w[1]] + ([inline(w[2:])[2]] if inline(w[2:]) else []):
                if ALIAS.get(n, n) not in names:
                    errs.append(f'{b["key"]}: wire {w[0]} net {n} is not a schematic net')
            if inline(w[2:]) and inline(w[2:])[0] not in refs:
                errs.append(f'{b["key"]}: wire {w[0]}: in-line {inline(w[2:])[0]} is not in the schematic')
    return errs


# ----------------------------------------------------------------------------------------------------------------
def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;')


def render(b):
    cols, rows = b['grid']
    W, H = b['size']
    mx, my = (W - (cols - 1) * P) / 2, b.get('my0', (H - (rows - 1) * P) / 2)
    S = 15 if max(W, H) < 30 else 12.5
    gap = b.get('gap', 90)
    ox1, oy = 60 + b.get('lpad', 0), 112
    ox2 = ox1 + W * S + gap
    out = []
    e = out.append

    def pos(c, r, mirror=False):
        x = mx + c * P
        y = my + r * P
        X = (ox2 + (W - x) * S) if mirror else (ox1 + x * S)
        return X, oy + (H - y) * S

    def hp(name, mirror=False):
        return pos(*h(name), mirror)

    cut = {h(x) for x in b.get('cuts', [])}
    used_hole = set()
    for _, kind, _, pins, _ in b['parts']:
        for k, v in pins.items():
            if not k.startswith('_') and v[1] is not None:
                used_hole.add(h(v[0]))
    for w in b['wires']:
        used_hole.add(h(w[0]))
    for _, holes, _ in b['links']:
        used_hole.update(h(x) for x in holes)

    total_w = ox2 + W * S + 40
    e(f'<text x="{ox1}" y="34" font-size="22" font-weight="600" fill="{INK}" font-family="IBM Plex Sans Condensed, Arial Narrow, sans-serif">{esc(b["title"])}</text>')
    e(f'<text x="{ox1}" y="56" font-size="12.5" fill="{MUTED}">{esc(b["sub"])}</text>')
    for k, (ox, mirror, label, sub) in enumerate([(ox1, False, 'component side', b['comp']), (ox2, True, 'solder side (mirrored)', b['copper'])]):
        e(f'<text x="{ox}" y="{oy - 30}" font-size="13" font-weight="600" fill="{INK}">{label}</text>')
        # board
        fill = '#efe3c6' if not mirror else '#e2cfa3'
        e(f'<rect x="{ox}" y="{oy}" width="{W * S}" height="{H * S}" rx="4" fill="{fill}" stroke="#9c8a62" stroke-width="1.2"/>')
        # grid labels
        for c in range(cols):
            X, _ = pos(c, rows - 1, mirror)
            e(f'<text x="{X}" y="{oy - 8}" font-size="10.5" text-anchor="middle" fill="{MUTED}" font-family="IBM Plex Mono, monospace">{chr(65 + c)}</text>')
        for r in range(rows):
            _, Y = pos(0, r)
            xl = ox - 8 - b.get('rowpad', 0) if not mirror else ox + W * S + 8
            e(f'<text x="{xl}" y="{Y + 3.5}" font-size="10.5" text-anchor="{"end" if not mirror else "start"}" fill="{MUTED}" font-family="IBM Plex Mono, monospace">{r + 1}</text>')
        # keep-out marks
        for hole, why in b.get('keep', []):
            X, Y = hp(hole, mirror)
            e(f'<rect x="{X - 0.5 * P * S}" y="{Y - 0.5 * P * S}" width="{P * S}" height="{P * S}" fill="#d9d2f0" opacity=".55"/>')
        if mirror and b['strips']:
            for r in range(rows):
                segs, cur = [], []
                for c in range(cols):
                    if (c, r) in cut:
                        if cur:
                            segs.append(cur)
                        cur = []
                    else:
                        cur.append(c)
                if cur:
                    segs.append(cur)
                for sg in segs:
                    X1, Y = pos(sg[0], r, True)
                    X2, _ = pos(sg[-1], r, True)
                    xa, xb = min(X1, X2) - 0.45 * P * S, max(X1, X2) + 0.45 * P * S
                    e(f'<rect x="{xa}" y="{Y - 0.38 * P * S}" width="{xb - xa}" height="{0.76 * P * S}" rx="2" fill="#c98a4b"/>')
                if r in b.get('strip_names', {}):
                    X, Y = pos(cols - 1, r, True)
                    e(f'<text x="{X - 0.62 * P * S}" y="{Y + 4}" font-size="10.5" text-anchor="end" fill="{INK}" font-weight="600">{b["strip_names"][r]}</text>')
            for c, r in cut:
                X, Y = pos(c, r, True)
                e(f'<circle cx="{X}" cy="{Y}" r="{0.5 * P * S}" fill="#e2cfa3" stroke="{INK}" stroke-width="1"/>')
                e(f'<path d="M{X - 6} {Y - 6} L{X + 6} {Y + 6} M{X + 6} {Y - 6} L{X - 6} {Y + 6}" stroke="#c0392b" stroke-width="2"/>')
        if not mirror and b['strips']:
            for r, n in b.get('strip_names', {}).items():
                _, Y = pos(0, r)
                e(f'<text x="{ox - 26}" y="{Y + 3.5}" font-size="10.5" text-anchor="end" fill="{INK}" font-weight="600">{n}</text>')
        # holes / pads
        for c in range(cols):
            for r in range(rows):
                X, Y = pos(c, r, mirror)
                if mirror and not b['strips']:
                    e(f'<circle cx="{X}" cy="{Y}" r="{0.36 * P * S}" fill="#c98a4b"/>')
                if (c, r) in cut:
                    continue
                e(f'<circle cx="{X}" cy="{Y}" r="{0.2 * P * S}" fill="{"#6f5f3e" if (c, r) in used_hole else "#b9a47a"}"/>')
        if mirror:
            for kind, holes, label in b['links']:
                pts = [hp(x, True) for x in holes]
                d = ' '.join(f'{x},{y}' for x, y in pts)
                if kind == 'bridge':
                    e(f'<polyline points="{d}" fill="none" stroke="#a9b0b4" stroke-width="{0.42 * P * S}" stroke-linecap="round" stroke-linejoin="round"/>')
                elif kind == 'bus':
                    e(f'<polyline points="{d}" fill="none" stroke="#8e979c" stroke-width="3.2" stroke-linecap="round"/>')
                    e(f'<polyline points="{d}" fill="none" stroke="#d5dadc" stroke-width="1.4" stroke-linecap="round"/>')
                elif kind == 'jumper':
                    e(f'<polyline points="{d}" fill="none" stroke="#3a4248" stroke-width="3.4" stroke-linecap="round"/>')
                    e(f'<polyline points="{d}" fill="none" stroke="#f0f0ea" stroke-width="1.8" stroke-linecap="round" stroke-dasharray="4 3"/>')
                    (x1, y1), (x2, y2) = pts[0], pts[-1]
                    e(f'<text x="{(x1 + x2) / 2}" y="{(y1 + y2) / 2 - 6}" font-size="10" text-anchor="middle" fill="{INK}" paint-order="stroke" stroke="{SHEET}" stroke-width="3">{esc(label.split()[0])}</text>')
                for x, y in pts:
                    e(f'<circle cx="{x}" cy="{y}" r="{0.24 * P * S}" fill="#cfd5d8" stroke="#7d868b" stroke-width=".8"/>')
            # solder joints of part leads
            for ref, kind, val, pins, note in b['parts']:
                for k, v in pins.items():
                    if k.startswith('_') or v[1] is None:
                        continue
                    x, y = hp(v[0], True)
                    e(f'<circle cx="{x}" cy="{y}" r="{0.22 * P * S}" fill="#dfe3e5" stroke="#7d868b" stroke-width=".8"/>')
        else:
            for kind, holes, label in b['links']:
                if kind == 'link':
                    pts = [hp(x) for x in holes]
                    d = ' '.join(f'{x},{y}' for x, y in pts)
                    e(f'<polyline points="{d}" fill="none" stroke="#3a4248" stroke-width="3.4" stroke-linecap="round"/>')
                    e(f'<polyline points="{d}" fill="none" stroke="#e8ecee" stroke-width="1.6" stroke-linecap="round"/>')
            draw_parts(b, e, hp, S)
        # wires (pad boards: soldered on the copper side only; strip boards: they enter from the component side)
        seen = {}
        for i, (hole, net, colr, g, rings, to, *_) in enumerate(b['wires'], 1):
            if not mirror and not b['strips']:
                continue
            x, y = hp(hole, mirror)
            rad = 0.34 * P * S if g == 26 else 0.27 * P * S
            k = seen[hole] = seen.get(hole, -1) + 1   # second wire on the same pad: drawn beside it
            x, y = x + k * 0.5 * P * S, y - k * 0.5 * P * S
            e(f'<circle cx="{x}" cy="{y}" r="{rad + 1.3}" fill="#3a4248"/>')
            e(f'<circle cx="{x}" cy="{y}" r="{rad}" fill="{KIT[colr]}"/>')
            if isinstance(rings, str):   # coloured band: one wide mark, outlined
                e(f'<rect x="{x - rad - 5}" y="{y - rad - 1}" width="9" height="6" fill="{KIT[rings]}" stroke="{INK}" stroke-width="1"/>')
            else:
                for k in range(rings):
                    e(f'<line x1="{x - rad - 2}" y1="{y - rad + 3 + k * 3.2}" x2="{x - rad + 2}" y2="{y - rad + 3 + k * 3.2}" stroke="{INK}" stroke-width="1.6"/>')
            tc = '#ffffff' if colr in ('black', 'blue', 'green', 'brown', 'purple', 'red') else INK
            e(f'<text x="{x}" y="{y + 3.4}" font-size="9" text-anchor="middle" fill="{tc}" font-weight="600" font-family="IBM Plex Mono, monospace">{i}</text>')
    # connectors (harness side), the wires of this board in their contacts
    ty = oy + H * S + 40
    used = {}
    for i, w in enumerate(b['wires'], 1):
        for t in (w[6] if len(w) > 6 else []):
            ref, pin = t.split('.', 1)
            used.setdefault(ref, {})[pin] = (i, w[2])
    if used:
        cw, gap_c, x, y = 46, 34, ox1, ty + 6
        e(f'<text x="{ox1}" y="{y}" font-size="12" font-weight="600" fill="{MUTED}" letter-spacing=".06em">CONNECTORS (HARNESS SIDE, PIN 1 ON THE LEFT; NO. = WIRE OF THIS BOARD)</text>')
        y += 30
        maxx = max(ox2 + W * S, ox1 + 780)
        for ref in sorted(used, key=lambda r: int(r[1:])):
            title, pins = CONNS[ref]
            wd = max(sum(12 if p == '|' else cw for p, _ in pins), 6.4 * (len(ref) + 1 + len(title)))
            if x > ox1 and x + wd > maxx:
                x, y = ox1, y + 92
            e(f'<text x="{x}" y="{y}" font-size="11.5" fill="{INK}"><tspan font-weight="700">{ref}</tspan> {esc(title)}</text>')
            cx = x
            for k, (pin, net) in enumerate(pins):
                if pin == '|':
                    cx += 12
                    continue
                e(f'<rect x="{cx}" y="{y + 8}" width="{cw - 2}" height="34" rx="3" fill="{"#d5d8da" if net == "key" else SHEET}" stroke="#7d868b" stroke-width="1"/>')
                if k == 0:
                    e(f'<path d="M{cx} {y + 8} l7 0 l-7 7 z" fill="{INK}"/>')
                if net == 'key':
                    e(f'<text x="{cx + cw / 2 - 1}" y="{y + 29}" font-size="9.5" text-anchor="middle" fill="{MUTED}">plugged</text>')
                elif pin in used[ref]:
                    n, colr = used[ref][pin]
                    tc = '#ffffff' if colr in ('black', 'blue', 'green', 'brown', 'purple', 'red') else INK
                    e(f'<circle cx="{cx + cw / 2 - 1}" cy="{y + 25}" r="10" fill="#3a4248"/><circle cx="{cx + cw / 2 - 1}" cy="{y + 25}" r="8.7" fill="{KIT[colr]}"/>')
                    e(f'<text x="{cx + cw / 2 - 1}" y="{y + 28.5}" font-size="9.5" text-anchor="middle" fill="{tc}" font-weight="600" font-family="IBM Plex Mono, monospace">{n}</text>')
                elif net:
                    e(f'<text x="{cx + cw / 2 - 1}" y="{y + 29}" font-size="8.5" text-anchor="middle" fill="{MUTED}">{esc(net)}</text>')
                else:
                    e(f'<text x="{cx + cw / 2 - 1}" y="{y + 29}" font-size="9.5" text-anchor="middle" fill="{MUTED}">empty</text>')
                e(f'<text x="{cx + cw / 2 - 1}" y="{y + 56}" font-size="9.5" text-anchor="middle" fill="{INK}" font-family="IBM Plex Mono, monospace">{esc(pin)}</text>')
                cx += cw
            x += wd + gap_c
        ty = y + 92
    # tables
    lines = []
    lines.append(('h', 'Composants'))
    for ref, kind, val, pins, note in b['parts']:
        if kind == 'HDR':
            hs = sorted({v[0] for v in pins.values()}, key=lambda s: (s[0], int(s[1:])))
            lines.append(('p', f'{ref} {val}', f'{hs[0][0]}–{hs[-1][0]}, rows {min(int(s[1:]) for s in hs)}–{max(int(s[1:]) for s in hs)}', note))
            continue
        pinstr = ' · '.join(f'{k} {v[0]} ({v[1]})' for k, v in pins.items() if not k.startswith('_'))
        lines.append(('p', f'{ref} {val}', pinstr, note))
    lines.append(('h', 'Solder-side links' if not b['strips'] else 'Links'))
    for kind, holes, label in b['links']:
        nm = {'bridge': 'bridge', 'bus': 'bare bus', 'jumper': 'insulated jumper', 'link': 'component-side link'}[kind]
        lines.append(('p', nm, '–'.join(holes) if kind != 'bus' else f'{holes[0]} … {holes[-1]}', label))
    if b.get('cuts'):
        lines.append(('p', 'cuts', ', '.join(b['cuts']), 'strip broken at this hole'))
    lines.append(('h', 'Wires (drawing no. · hole · signal · wire · other end: ● soldered, D Dupont, XH JST-XH, F / M · to)'))
    for i, (hole, net, colr, g, rings, to, *tg) in enumerate(b['wires'], 1):
        rg = rings_text(rings)
        pins = ' + '.join(f'{t.split(".", 1)[0]} br. {pin_no(*t.split(".", 1))}' for t in (tg[0] if tg else []))
        t0 = tg[0][0].split('.', 1)[0] if tg and tg[0] else None
        far = ('XH' if t0 in XH else 'D', gender(t0, b['key'])) if t0 else ('S', '')
        lines.append(('w', f'{i}', f'{hole}  {net}', f'{NAME[colr]} {g} AWG{rg}', to + (f'  [{pins}]' if pins else ''), colr, far))
    lines.append(('h', 'Notes'))
    if b.get('keep_note'):
        lines.append(('n', b['keep_note']))
    for n in b['notes']:
        lines.append(('n', n))
    y = ty
    body = []
    for ln in lines:
        if ln[0] == 'h':
            y += 10
            body.append(f'<text x="{ox1}" y="{y}" font-size="12" font-weight="600" fill="{MUTED}" letter-spacing=".06em">{esc(ln[1].upper())}</text>')
            y += 18
        elif ln[0] == 'p':
            body.append(f'<text x="{ox1}" y="{y}" font-size="12" fill="{INK}"><tspan font-weight="600">{esc(ln[1])}</tspan><tspan x="{ox1 + 150}" font-family="IBM Plex Mono, monospace" font-size="11">{esc(ln[2])}</tspan></text>')
            y += 15
            if ln[3]:
                body.append(f'<text x="{ox1 + 150}" y="{y}" font-size="11" fill="{MUTED}">{esc(ln[3])}</text>')
                y += 16
        elif ln[0] == 'w':
            body.append(f'<circle cx="{ox1 + 8}" cy="{y - 4}" r="6.5" fill="{KIT[ln[5]]}" stroke="#3a4248" stroke-width="1.3"/>')
            body.append(f'<text x="{ox1 + 22}" y="{y}" font-size="11.5" fill="{INK}" font-family="IBM Plex Mono, monospace">{esc(ln[1]):>2}  {esc(ln[2])}</text>')
            body.append(f'<text x="{ox1 + 190}" y="{y}" font-size="11.5" fill="{MUTED}">{esc(ln[3])}</text>')
            body.append(end_symbol(ox1 + 392, y - 4, *ln[6]))
            body.append(f'<text x="{ox1 + 410}" y="{y}" font-size="11.5" fill="{INK}">{esc(ln[4])}</text>')
            y += 17
        else:
            for part in wrap(ln[1], 112):
                body.append(f'<text x="{ox1}" y="{y}" font-size="11.5" fill="{INK}">{esc(part)}</text>')
                y += 15
            y += 3
    out.extend(body)
    total_w = max(total_w, ox1 + 860)
    total_h = y + 20
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_w:.0f} {total_h:.0f}" width="{total_w:.0f}" height="{total_h:.0f}" '
            f'font-family="IBM Plex Sans, Segoe UI, sans-serif">\n<rect width="{total_w:.0f}" height="{total_h:.0f}" fill="{SHEET}"/>\n'
            + '\n'.join(out) + '\n</svg>\n')


def end_symbol(x, y, kind, g=''):
    """wire end code shared with the harness guide: grey dot = soldered, blue D = Dupont, orange XH = JST-XH (F / M)"""
    if kind == 'S':
        return f'<circle cx="{x}" cy="{y}" r="5" fill="#8e979c" stroke="{INK}" stroke-width="1"/>'
    fill, lab = ('#2a62d6', 'D') if kind == 'D' else ('#f07800', 'XH')
    w = 15 if kind == 'D' else 22
    return (f'<rect x="{x - w / 2}" y="{y - 6.5}" width="{w}" height="13" rx="2" fill="{fill}"/>'
            f'<text x="{x}" y="{y + 3.5}" font-size="9" text-anchor="middle" fill="#ffffff" font-weight="700">{lab}{g}</text>')


def wrap(s, n):
    words, lines, cur = s.split(), [], ''
    for w in words:
        if len(cur) + len(w) + 1 > n:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + ' ' + w).strip()
    if cur:
        lines.append(cur)
    return lines


def draw_parts(b, e, hp, S):
    for ref, kind, val, pins, note in b['parts']:
        pv = {k: v for k, v in pins.items() if not k.startswith('_')}
        if kind == 'HDR':
            hs = [hp(v[0]) for v in pv.values()]
            xs, ys = [p[0] for p in hs], [p[1] for p in hs]
            pad = 0.5 * P * S
            e(f'<rect x="{min(xs) - pad}" y="{min(ys) - pad}" width="{max(xs) - min(xs) + 2 * pad}" height="{max(ys) - min(ys) + 2 * pad}" rx="2" fill="#2b2f33" opacity=".85"/>')
            for name, (hole, net) in pv.items():
                x, y = hp(hole)
                e(f'<circle cx="{x}" cy="{y}" r="{0.17 * P * S}" fill="#d9b44a"/>')
                lab = name.rstrip('0123456789') if name.startswith('G') else name.replace('IO', '')
                c, _ = h(hole)
                dx = -0.62 * P * S if c in (0, 8) else 0.62 * P * S
                anchor = 'end' if c in (0, 8) else 'start'
                if c in (0, 9):
                    tx = x - 0.62 * P * S - 2 if c == 0 else x + 0.62 * P * S + 2
                    anchor = 'end' if c == 0 else 'start'
                    e(f'<text x="{tx - (0 if c else 0)}" y="{y + 3.5}" font-size="9.5" text-anchor="{anchor}" fill="{INK}" font-family="IBM Plex Mono, monospace">{lab}</text>')
                else:
                    e(f'<text x="{x}" y="{y - 0.3 * P * S}" font-size="8" text-anchor="middle" fill="#e8e2c8" font-family="IBM Plex Mono, monospace">{lab}</text>')
            continue
        pts = [hp(v[0]) for v in pv.values()]
        if kind in ('R', 'D'):
            (x1, y1), (x2, y2) = pts
            L = math.hypot(x2 - x1, y2 - y1)
            ux, uy = (x2 - x1) / L, (y2 - y1) / L
            bl = min((9.5 if kind == 'D' else 6.3) * S, L - 0.8 * P * S)
            bw = (5.3 if kind == 'D' else 2.4) * S
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            ang = math.degrees(math.atan2(uy, ux))
            e(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#7d868b" stroke-width="2"/>')
            fill = '#2d3136' if kind == 'D' else '#d8c08e'
            e(f'<rect x="{cx - bl / 2}" y="{cy - bw / 2}" width="{bl}" height="{bw}" rx="{bw / 2.5}" fill="{fill}" stroke="#5e676d" stroke-width="1" transform="rotate({ang} {cx} {cy})"/>')
            if kind == 'D':
                kx, ky = pv['K'][0] and hp(pv['K'][0])
                sx = cx + (kx - cx) / max(1e-6, math.hypot(kx - cx, ky - cy)) * (bl / 2 - 6)
                sy = cy + (ky - cy) / max(1e-6, math.hypot(kx - cx, ky - cy)) * (bl / 2 - 6)
                e(f'<rect x="{sx - 3}" y="{sy - bw / 2}" width="6" height="{bw}" fill="#c9ced1" transform="rotate({ang} {sx} {sy})"/>')
            tcol = '#ffffff' if kind == 'D' else INK
            e(f'<text x="{cx}" y="{cy + 4}" font-size="10.5" text-anchor="middle" fill="{tcol}" font-weight="600" transform="rotate({ang if abs(ang) <= 90 else ang - 180} {cx} {cy + 0})">{ref} {val}</text>')
        elif kind == 'Rv':
            (x1, y1), (x2, y2) = pts
            e(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#7d868b" stroke-width="2"/>')
            e(f'<circle cx="{x1}" cy="{y1}" r="{1.3 * S}" fill="#d8c08e" stroke="#5e676d" stroke-width="1"/>')
            e(f'<text x="{x1}" y="{y1 + 3.5}" font-size="9" text-anchor="middle" fill="{INK}" font-weight="600">{ref}</text>')
        elif kind == 'C':
            (x1, y1), (x2, y2) = pts[0], pts[1]
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            if 'CMS' in val:  # SMD chip lying flat (7343), its band on the + end
                rad = 2.15 * S
                ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
                e(f'<rect x="{cx - 3.65 * S}" y="{cy - rad}" width="{7.3 * S}" height="{2 * rad}" rx="2" fill="#e0a43a" stroke="#8a5e15" stroke-width="1" transform="rotate({ang} {cx} {cy})"/>')
                bx = cx + (x1 - cx) * 0.8
                e(f'<rect x="{bx - 1.2 * S}" y="{cy - rad}" width="{1.2 * S}" height="{2 * rad}" fill="#8a5e15" transform="rotate({ang} {cx} {cy})"/>')
            else:
                rad = (3.15 if '220' in val or '100–' in val else 2.5) * S
                e(f'<circle cx="{cx}" cy="{cy}" r="{rad}" fill="#3d6aa8" fill-opacity=".85" stroke="#28466f" stroke-width="1"/>')
            px, py = hp(pv['+'][0])
            e(f'<text x="{px}" y="{py + 4}" font-size="12" text-anchor="middle" fill="#ffffff" font-weight="700">+</text>')
            e(f'<text x="{cx}" y="{cy - rad - 3}" font-size="10" text-anchor="middle" fill="{INK}" font-weight="600" paint-order="stroke" stroke="{SHEET}" stroke-width="3">{ref}</text>')
        elif kind == 'Cc':
            (x1, y1), (x2, y2) = pts
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
            e(f'<rect x="{cx - 2.4 * S}" y="{cy - 1.2 * S}" width="{4.8 * S}" height="{2.4 * S}" rx="{1.1 * S}" fill="#e0a43a" stroke="#8a5e15" stroke-width="1" transform="rotate({ang} {cx} {cy})"/>')
            e(f'<text x="{cx}" y="{cy + 3.5}" font-size="9" text-anchor="middle" fill="{INK}" font-weight="600">{ref}</text>')
        elif kind == 'T':
            # TO-92 standing, its three leads in a row; the flat face is on the side named by '_flat' (N, E, S, W)
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            cx, cy = sum(xs) / 3, sum(ys) / 3
            horiz = max(xs) - min(xs) > max(ys) - min(ys)
            fx, fy = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}[pins['_flat']]
            r = 2.4 * S
            if horiz:
                d = f'M{cx - r} {cy} A{r} {r} 0 0 {1 if fy < 0 else 0} {cx + r} {cy} Z'
            else:
                d = f'M{cx} {cy - r} A{r} {r} 0 0 {1 if fx > 0 else 0} {cx} {cy + r} Z'
            e(f'<path d="{d}" fill="#23272b" fill-opacity=".85" stroke="#111" stroke-width="1"/>')
            for k, v in pv.items():
                x, y = hp(v[0])
                e(f'<text x="{x}" y="{y + 3.5}" font-size="9" text-anchor="middle" fill="#ffffff" font-weight="700">{k}</text>')
            e(f'<text x="{cx - fx * (r + 8)}" y="{cy - fy * (r + 8) + 3.5}" font-size="9" text-anchor="middle" fill="{INK}" font-weight="600" paint-order="stroke" stroke="{SHEET}" stroke-width="3">{ref}</text>')
        elif kind == 'Q':
            # SOT-23 glued pins up, seen from above: its D pin faces '_d'; flipped, G is 90° clockwise of D, S 90°
            # counter-clockwise (screen coordinates), both on the far side of the body
            ax, ay = hp(pins['_at'])
            dx, dy = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}[pins['_d']]
            gx, gy = -dy, dx
            bw, bh = (3 * S, 1.5 * S) if dx == 0 else (1.5 * S, 3 * S)
            e(f'<rect x="{ax - bw / 2}" y="{ay - bh / 2}" width="{bw}" height="{bh}" rx="2" fill="#23272b"/>')
            stub = {'D': (ax + dx * 1.15 * S, ay + dy * 1.15 * S),
                    'G': (ax + gx * 0.95 * S - dx * 1.15 * S, ay + gy * 0.95 * S - dy * 1.15 * S),
                    'S': (ax - gx * 0.95 * S - dx * 1.15 * S, ay - gy * 0.95 * S - dy * 1.15 * S)}
            for k, v in pv.items():
                x, y = hp(v[0])
                d = ' '.join(f'{px},{py}' for px, py in [stub[k]] + [hp(w) for w in pins.get('_via', {}).get(k, [])] + [(x, y)])
                e(f'<polyline points="{d}" fill="none" stroke="#3a4248" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
                e(f'<polyline points="{d}" fill="none" stroke="#7fb3e6" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>')
            for k, (sx, sy) in stub.items():
                e(f'<rect x="{sx - 2.5}" y="{sy - 2.5}" width="5" height="5" fill="#c9ced1" stroke="#5e676d" stroke-width=".8"/>')
                e(f'<text x="{sx + (dx * 9 if k == "D" else 0)}" y="{sy + 3.5 + (dy * 9 if k == "D" else -dy * 9 if dx == 0 else 0) + (0 if dx == 0 else -9)}" font-size="10" text-anchor="middle" fill="{INK}" font-weight="700" paint-order="stroke" stroke="{SHEET}" stroke-width="3">{k}</text>')
            e(f'<text x="{ax}" y="{ay + 3.2}" font-size="8" text-anchor="middle" fill="#ffffff" font-weight="600">{ref}</text>')


def main():
    bad = False
    errs = crosscheck(BOARDS)
    if errs:
        bad = True
        print(f'== schematic: {len(errs)} problem(s)')
        for x in errs:
            print('  ', x)
    else:
        print('== schematic: OK, every board part on the same nets as in kicad_sch_gen.py')
    for b in BOARDS:
        errs, groups = check(b)
        if errs:
            bad = True
            print(f'== {b["key"]}: {len(errs)} problem(s)')
            for x in errs:
                print('  ', x)
        else:
            nets = sorted({n for g in groups.values() for n in g})
            print(f'== {b["key"]}: OK, {len(nets)} nets, {len(b["wires"])} wires')
    if bad:
        sys.exit(1)
    for b in BOARDS:
        path = f'renders/tars4_board_{b["key"]}.svg'
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(render(b))
        print('wrote', path)


if __name__ == '__main__':
    main()
