"""Wiring guide of TARS4: every wire with both ends, in build order.

usage: python3 -I tools/harness.py [--no-pdf]   (writes hardware/tars4_harness.html and, with Firefox, hardware/tars4_harness.pdf)

The board wires come from tools/boards.py (hole, net, colour, connector contacts); the wires that touch no board
(power block leads, module pigtails, cells, charge port, switch, speaker, contact-to-contact jumpers) are listed
below. Every wire gets a number W1… in build order and its two ends are typed with the code of the board drawings:
soldered (grey dot), Dupont (blue D) or JST-XH (orange XH), female F / male M. Each build step gets a diagram (TARS
columns from left to right, tubes between them), its wire table and its bench test.
"""
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from boards import BOARDS, CONNS, KIT, NAME, XH, CCOL, P, gender, pin_no, rings_text  # noqa: E402
import json  # noqa: E402
import tempfile  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEO_CACHE = os.path.join(ROOT, 'tools', 'harness_geometry.json')
HTML = os.path.join(ROOT, 'hardware', 'tars4_harness.html')
PDF = os.path.join(ROOT, 'hardware', 'tars4_harness.pdf')
PIGTAIL = 6      # module pigtails (INMP441, AM312, microSD reader), cm
TOL = 3         # cut length = estimate + TOL, cm

BCOL = {'s3': 1, 'p1': 1, 'p2': 2, 'power': 0}
BNAME = {'s3': 'P3', 'p1': 'P1', 'p2': 'P2', 'power': 'P4'}   # P = hand-wired board, X = connector, else a module
BSUB = {'s3': 'S3 carrier', 'p1': 'left middle distribution', 'p2': 'right middle distribution', 'power': 'power path'}
FRAME = {'P': ('#2f8f5b', 'board'), 'M': ('#8e44c4', 'module'), 'D': ('#2a62d6', 'Dupont'), 'XH': ('#f07800', 'JST-XH')}
BSTEP = {'power': 1, 's3': 3, 'p1': 4, 'p2': 6}
TUBE = {0: 'left tube', 1: 'middle tube', 2: 'right tube'}
COLNAME = ['left leg', 'left middle', 'right middle', 'right leg']
# board-to-board wires: listed on both drawings, one wire
PAIRS = [('s3', 'A4', 'p1', 'B9'), ('s3', 'J5', 'p1', 'B10'), ('s3', 'A7', 'p1', 'A7'), ('s3', 'C10', 'p1', 'A5'),
         ('s3', 'B7', 'p1', 'A8'), ('s3', 'B6', 'p1', 'A6'), ('s3', 'A9', 'p2', 'A11'), ('s3', 'B10', 'p2', 'A4'),
         ('p1', 'C11', 'p2', 'A10'), ('p1', 'F9', 'p2', 'A9')]


def S(block, port, col, step, sub='', frame='M'):
    return dict(kind='S', block=block, port=port, col=col, step=step, sub=sub, frame=frame)


def C(t, g):
    ref, pin = t.split('.', 1)
    step = {'X1': 4, 'X2': 4, 'X3': 4, 'X4': 6, 'X5': 6, 'X6': 6, 'X7': 6, 'X8': 7, 'X9': 7, 'X15': 5,
            'X10': 1 if g == 'F' else 2, 'X12': 1 if g == 'M' else 2, 'X16': 1 if g == 'M' else 2,
            'X13': 1 if g == 'F' else 5, 'X14': 1 if g == 'F' else 5}[ref]
    kind = 'XH' if ref in XH else 'D'
    return dict(kind=kind, block=f'{ref} {g}', sub=f'{"female" if g == "F" else "male"} side · {CONNS[ref][0].split(" · ")[0]}', frame=kind,
                port=f'{pin_no(ref, pin)} {pin}', col=CCOL[ref],
                step=step, ref=ref, pin=pin, g=g)


# wires touching no board: (colour, AWG, rings, signal, end A, end B, step, note)
EXTRA = [
    ('red', 26, 'purple', 'VUSB', S('TP4056', 'IN+', 0, 1), C('X10.VUSB', 'F'), 1, ''),
    ('black', 26, 'purple', 'GND', S('TP4056', 'IN−', 0, 1), C('X10.GND', 'F'), 1, ''),
    ('white', 26, 0, '3V3', S('TPS63020', 'VOUT', 0, 1), C('X13.3V3', 'F'), 1, 'along the logic GND wire'),
    ('blue', 26, 0, 'GND', S('TPS63020', 'GND', 0, 1), C('X13.GND log', 'F'), 1, 'logic GND, along the 3V3'),
    ('red', 26, 0, 'B+', S('TP4056', 'B+', 0, 1), C('X12.B+', 'M'), 1, 'cell junction: two wires soldered on the B+ pad'),
    ('black', 26, 0, 'B−', S('TP4056', 'B−', 0, 1), C('X12.B−', 'M'), 1, 'cell junction: two wires soldered on the B− pad'),
    ('red', 26, 0, 'B+', S('TP4056', 'B+', 0, 1), C('X16.B+', 'M'), 1, 'to X16, parked above the power-path board'),
    ('black', 26, 0, 'B−', S('TP4056', 'B−', 0, 1), C('X16.B−', 'M'), 1, ''),
    ('red', 26, 'purple', 'VUSB', S('J1 micro-USB', 'VBUS', 0, 2), C('X10.VUSB', 'M'), 2, 'twisted with the GND'),
    ('black', 26, 'purple', 'GND', S('J1 micro-USB', 'GND', 0, 2), C('X10.GND', 'M'), 2, ''),
    ('red', 26, 'yellow', 'VPATH', S('SW1 switch', 'end lug', 0, 2), C('X10.VPATH', 'M'), 2, ''),
    ('red', 26, 'orange', 'VSYS', S('SW1 switch', 'centre lug', 0, 2), C('X10.VSYS', 'M'), 2, ''),
    ('red', 26, 0, 'B+', S('left cell', 'F1 (+ plate)', 0, 2), C('X12.B+', 'F'), 2, 'twisted with B−'),
    ('black', 26, 0, 'B−', S('left cell', '− plate', 0, 2), C('X12.B−', 'F'), 2, ''),
    ('red', 26, 0, 'B+', S('right cell', 'F2 (+ plate)', 3, 7), C('X16.B+', 'F'), 7,
     'X16 crimped at step 2, bare end threaded through the 3 tubes, soldered on F2 at step 7; twisted with B−'),
    ('black', 26, 0, 'B−', S('right cell', '− plate', 3, 7), C('X16.B−', 'F'), 7,
     'as B+; twisted with B+'),
    ('white', 30, 0, '3V3', C('X3.VDD', 'F'), C('X2.VCC', 'F'), 4, 'double contact in X3 (with the wire from P1)'),
    ('blue', 30, 0, 'GND', C('X3.GND', 'F'), C('X2.GND', 'F'), 4, 'double contact in X3 (with the wire from P1)'),
    ('yellow', 30, 1, 'MIC_BCLK', S('INMP441', 'SCK', 1, 4), C('X3.SCK', 'M'), 4, '5–6 cm pigtail'),
    ('purple', 30, 1, 'MIC_WS', S('INMP441', 'WS', 1, 4), C('X3.WS', 'M'), 4, ''),
    ('green', 30, 1, 'MIC_SD', S('INMP441', 'SD', 1, 4), C('X3.SD', 'M'), 4, ''),
    ('white', 30, 0, '3V3', S('INMP441', 'VDD', 1, 4), C('X3.VDD', 'M'), 4, ''),
    ('blue', 30, 0, 'GND', S('INMP441', 'GND', 1, 4), C('X3.GND', 'M'), 4, 'L/R bridged to GND on the board'),
    ('yellow', 30, 3, 'SD_CLK', S('microSD reader', 'CLK', 0, 5), C('X15.CLK', 'M'), 5, '5–6 cm pigtail'),
    ('purple', 30, 3, 'SD_CMD', S('microSD reader', 'CMD', 0, 5), C('X15.CMD', 'M'), 5, ''),
    ('green', 30, 3, 'SD_D0', S('microSD reader', 'D0', 0, 5), C('X15.D0', 'M'), 5, ''),
    ('white', 30, 3, 'SD_3V3', S('microSD reader', 'VCC', 0, 5), C('X15.3V3', 'M'), 5, ''),
    ('blue', 30, 3, 'GND', S('microSD reader', 'GND', 0, 5), C('X15.GND', 'M'), 5, ''),
    ('red', 26, 'orange', 'VSYS', C('X13.VSYS', 'M'), C('X5.VIN', 'F'), 6,
     'amplifier pair: threaded through the left tube at step 5, X5 end crimped here; twisted with its GND'),
    ('black', 26, 'orange', 'GND', C('X13.GND amp', 'M'), C('X5.GND', 'F'), 6, 'twisted with VSYS; the orange band tells it from the right cell B+ / B− pair in the tubes'),
    ('grey', 26, 0, 'SPK+', S('speaker', '+', 2, 6), C('X6.+', 'F'), 6, '+ marked with a pen at both ends'),
    ('grey', 26, 0, 'SPK−', S('speaker', '−', 2, 6), C('X6.−', 'F'), 6, ''),
    ('white', 30, 0, 'PIR_VDD', S('AM312', 'VIN', 2, 6), C('X7.VIN', 'M'), 6, '5–6 cm pigtail'),
    ('red', 30, 1, 'PIR_OUT', S('AM312', 'OUT', 2, 6), C('X7.OUT', 'M'), 6, ''),
    ('blue', 30, 0, 'GND', S('AM312', 'GND', 2, 6), C('X7.GND', 'M'), 6, ''),
]

STEPS = [
    (1, 'Power block, on the bench', 'left leg: TP4056, power-path board, TPS63020 soldered together',
     ['Power-path board: parts, bridges and GND bus per renders/tars4_board_power.svg (Q1 / Q5 with wire-wrap wire).',
      'TP4056: R_PROG replaced by 2.4 k, then tested alone: 3.7 V bench supply on B+ / B−, current < 10 µA. Polarities: C9 + on IN+, D3 band (cathode) on IN+ (reversed, it shorts the 5 V). TPS63020: EN tied to VIN, PS/SYNC to GND.',
      'Crowded pads (joints ≥ 0.65 mm from the board end): splice 1 cm before the pad the two VUSB wires of IN+ (to X10 and to the power-path board), the two B+ (to X12 and X16, with the B+ sense wire to the power-path board) and the two B−: a single conductor per pad, next to C9 / D3.',
      'Solder the wires below (4–5 cm loops between the three boards), then crimp the XH contacts and slide them into X10, X12, X13 and X14.',
      'X12 and X16 on the block side (M): while unplugged, capped with an empty female XH housing. Their pins carry B+ / B− as soon as a cell is plugged in, until step 7.'],
     ['3.7 V bench supply on X12 (block side, M): OUT+ ≈ B+; current without USB noted (D1 leakage adds to the TP4056 one: a few tens of µA possible; power_budget.md).',
      'X10 cavities 3–4 bridged (switch simulated): VSYS ≈ B+; 3.3 V on X13 cavity 3; VBAT/2 ≈ B+ / 2 on X14 cavity 1.',
      '5 V on X10 cavities 1–2: charge LED, USB_DET ≈ 3 V on X14 cavity 2, Q1 off.']),
    (2, 'Charge port, switch, cells', 'the foot and cell cables up to X10, X12 and X16',
     ['Solder F1 on the left + plate (F2 on the right one at step 7). Never solder on a cell.',
      'Right cell wires: long enough to cross the three tubes (length from the table, already + 3 cm, offered up on TARS before cutting). Crimp X16 (female) now; the right cell end stays bare.'],
     ['Left cell alone: X12 plugged in, switch on, VSYS ≈ B+.',
      'Charger on J1: charge LED; unplugged: VUSB < 0.5 V within ~1 s.']),
    (3, 'S3 carrier', 'the 27 controller wires, soldered on the carrier side',
     ['Plan renders/tars4_board_s3.svg: 2 × 8 headers (V contact removed, headers glued), standing parts, bridges, GND bus, jumpers.',
      'Solder the 27 wires on the carrier side only, long enough (6–8 cm service loop + route). The other end stays bare: it is finished at the step shown.'],
     ['Before any power-up: every still-free end capped with closed heat-shrink (shrunk, end pinched while hot).', 'S3 removed: each wire ↔ its pin with the ohmmeter, GND isolated from 3V3 and the signals.',
      'S3 plugged in, PC USB: test program flashed, the S3 boots.']),
    (4, 'P1 and the left middle', 'screen 1, mic, accelerometer',
     ['Plan renders/tars4_board_p1.svg. 1 × 8 right-angle header on the back of screen 1 (X1). ADXL345: straight header, INT2 removed and its cavity plugged (X2).',
      'INMP441: 5-wire pigtail (male contacts, X3); L/R bridged to GND on its board.',
      'X2 SDA and SCL: double contact, crimp together (without folding back) the S3 wire and the one leaving for P2 (bare end, soldered at step 6).'],
     ['Before any power-up: every still-free end capped with closed heat-shrink (shrunk, end pinched while hot).', 'S3 on USB, switch off: screen 1 displays, the mic gives I2S samples, the ADXL345 answers at 0x53 and INT1 toggles.']),
    (5, 'Left tube: power block ↔ left middle, microSD', 'everything crossing the left tube',
     ['Thread the left brass tube onto the listed wires BEFORE crimping the far end. The amplifier pair (step 6) and the right cell pair (step 2) also cross this tube: thread them at the same time.',
      'microSD reader: C4 10 µF tantalum lying flat (+ on VCC; only ~6.6 mm up to the TPS63020) and C5 100 nF on its VCC / GND pins; without pull-ups on the reader, R5–R9 10 k from CMD, D0, D1, D2 and D3 to VCC (SD_3V3). Then a 5-wire pigtail (male contacts, X15).'],
     ['Before any power-up: every still-free end capped with closed heat-shrink (shrunk, end pinched while hot).', 'Without USB, switch on: the S3 boots from the cells (3.3 V on the carrier).',
      'VBAT/2 and USB_DET read by the S3; the microSD is read; SD_EN high cuts its 3.3 V.']),
    (6, 'Middle tube and right middle', 'screen 2, amplifier, speaker, AM312, P2',
     ['Plan renders/tars4_board_p2.svg. Right-angle header on the back of screen 2 (X4). Amplifier: 1 × 4 (GAIN removed) + 1 × 3 headers (X5), 2-pin header instead of the screw terminal (X6), C7 + on VIN, band (−) to GND.',
      'AM312: 3-wire pigtail (male contacts, X7), breakout pins trimmed flush, breakout slipped into a heat-shrink sock (it passes 5 mm from the middle tube exit). Thread the middle tube before crimping.'],
     ['Before any power-up: every still-free end capped with closed heat-shrink (shrunk, end pinched while hot).', 'Screen 2 displays; sound in the speaker; AMP_SD low cuts the amplifier; PIR rises when a hand passes.']),
    (7, 'Right tube and right leg', 'DS3231, BME280, right cell',
     ['DS3231: right-angle header, 32K removed, coin-cell charging resistor removed. BME280: 1 × 4 header, LED removed.',
      'Thread the right tube. F2 on the right + plate, then solder the two right cell wires (step 2).',
      'X9: each contact takes two wires (P2 + the continuation to X8), crimped together without folding back.',
      'Right tube: twist SDA with GND and SCL with 3V3 (long I2C bus, next to SCK / BCLK).'],
     ['I2C scan: 0x53 (ADXL345), 0x57 (DS3231 EEPROM), 0x68 (DS3231), 0x76 or 0x77 (BME280).',
      'Before plugging in the right cell (X16): same voltage as the left one within 0.05 V.']),
]


def geometry():
    """positions read from tars4.scad (openscad echo), cached in tools/harness_geometry.json for machines without it"""
    keys = ('col_w D H wall gap lid_y d1_x d1_z0 carrier_back_y hub_y hub_z0 pp_z0 charger_z0 bk_z0 bk_y1 usbb_z0 shelf_z '
            'fuse_z0 sw_y usbb_y0 spk_z0 spk_front_y charger bk spk').split()
    q = '\\"'                       # an escaped quote inside the SCAD string
    items = [(k, k) for k in keys] + [('pivot_z', 'pivot_z[0]'), ('conn_names', '[for (c = CONN) c[1]]'),
                                      ('conn_box', '[for (c = CONN) [c[0], c[3], c[4]]]')]
    body = ', '.join(f'"{"," if n else ""}{q}{k}{q}:", {v}' for n, (k, v) in enumerate(items))
    scad = f'include <{os.path.join(ROOT, "mechanical", "scad", "tars4.scad")}>\necho(str("GEOJSON{{", {body}, "}}"));\n'
    if shutil.which('openscad'):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, 'g.scad'), 'w') as fh:
                fh.write(scad)
            subprocess.run(['openscad', '-D', 'part="none"', '-o', os.path.join(d, 'g.echo'), os.path.join(d, 'g.scad')],
                           capture_output=True, timeout=300)
            txt = open(os.path.join(d, 'g.echo')).read()
        j = txt[txt.index('GEOJSON') + 7:].split('\n')[0].rstrip('"').replace('\\"', '"')
        geo = json.loads(j)
        with open(GEO_CACHE, 'w', encoding='utf-8') as fh:
            json.dump(geo, fh, indent=1)
        return geo
    # without openscad, the cache is only trusted if no model file changed after it was written (else: old wire lengths)
    scad = os.path.join(ROOT, 'mechanical', 'scad', 'tars4.scad')
    if not os.path.exists(GEO_CACHE) or os.path.getmtime(GEO_CACHE) < os.path.getmtime(scad):
        sys.exit(f'harness.py: openscad not found and {os.path.relpath(GEO_CACHE, ROOT)} is missing or older than '
                 'tars4.scad: put openscad on the PATH')
    print(f'harness.py: openscad not found, positions from {os.path.relpath(GEO_CACHE, ROOT)}')
    return json.load(open(GEO_CACHE))


def where(e, g):
    """(column, x, y, z) of a wire end in mm, or None for a fixed-length module pigtail"""
    cw, D = g['col_w'], g['D']
    if 'board' in e:
        b = next(bb for bb in BOARDS if bb['key'] == e['board'])
        W, Hh = b['size']
        cols, rows = b['grid']
        mx, my = (W - (cols - 1) * P) / 2, b.get('my0', (Hh - (rows - 1) * P) / 2)
        c, r = ord(e['port'][0]) - 65, int(e['port'][1:]) - 1
        if e['board'] == 's3':
            return 1, g['d1_x'] - W / 2 + mx + c * P, g['carrier_back_y'], g['d1_z0'] + my + r * P
        if e['board'] == 'power':
            return 0, cw / 2 - W / 2 + mx + c * P, g['lid_y'] - 0.3 - Hh + my + r * P, g['pp_z0']
        return BCOL[e['board']], cw / 2 - W / 2 + mx + c * P, g['hub_y'], g['hub_z0'] + my + r * P
    if e['kind'] != 'S':
        k = g['conn_names'].index(e['ref'])
        col, a, b2 = g['conn_box'][k]
        return (col, *[(u + v) / 2 for u, v in zip(a, b2)])
    m, col = e['block'], e['col']
    if m == 'TP4056':
        return 0, cw / 2, g['lid_y'] - 0.3 - g['charger'][1] / 2, g['charger_z0'] + 1
    if m == 'TPS63020':
        return 0, cw / 2, g['bk_y1'] - g['bk'][1] / 2, g['bk_z0'] + 1
    if m.startswith('J1'):
        return 0, g['wall'] + 3, g['usbb_y0'] + 2, g['usbb_z0'] + 7
    if m.startswith('SW1'):
        return 0, cw / 2, g['sw_y'], 8
    if m.endswith(' cell'):
        return col, cw / 2, D / 2, g['fuse_z0'] + 1 if '+' in e['port'] else g['shelf_z'] - 1
    if m == 'speaker':
        return 2, cw / 2, g['spk_front_y'] + g['spk'][1], g['spk_z0'] + g['spk'][2] / 2
    return None


def slack(e):
    """service loop at an end, cm: P3 slides out with the S3 (6–8 cm), boards / modules / connectors come out of the back"""
    if e.get('board') == 's3':
        return 7
    if e['kind'] != 'S':
        return 4
    if e['block'] in ('TP4056', 'TPS63020'):
        return 2
    return 3


def length(w, g):
    """estimated wire length and cut length, cm"""
    a, b = where(w['A'], g), where(w['B'], g)
    if a is None or b is None:
        return PIGTAIL, PIGTAIL + 1
    cw, D, wall, gap, zp = g['col_w'], g['D'], g['wall'], g['gap'], g['pivot_z']
    if a[0] == b[0]:
        mm = sum(abs(u - v) for u, v in zip(a[1:], b[1:]))
    else:
        if a[0] > b[0]:
            a, b = b, a
        mm = (abs(cw - wall - a[1]) + abs(D / 2 - a[2]) + abs(zp - a[3])          # up to the tube, out of the right wall
              + (b[0] - a[0]) * (2 * wall + gap) + (b[0] - a[0] - 1) * (cw - 2 * wall)
              + abs(b[1] - wall) + abs(D / 2 - b[2]) + abs(zp - b[3]))
    est = 1.1 * mm / 10 + slack(w['A']) + slack(w['B']) + 3 * len(w['tubes'])
    est = int(-(-est // 1))
    return est, est + TOL


def collect():
    wires = []
    pair_of = {}
    for a, ha, b, hb in PAIRS:
        pair_of[(a, ha)] = (b, hb)
        pair_of[(b, hb)] = None
    for b in BOARDS:
        k = b['key']
        for i, w in enumerate(b['wires'], 1):
            hole, net, colr, g, rings, dest = w[:6]
            tg = w[6] if len(w) > 6 else []
            A = S(BNAME[k], f'{hole}', BCOL[k], BSTEP[k], BSUB[k], 'P')
            A.update(board=k, plan=i)
            if (k, hole) in pair_of:
                if pair_of[(k, hole)] is None:
                    continue
                kb, hb = pair_of[(k, hole)]
                j = [n for n, x in enumerate(next(bb for bb in BOARDS if bb['key'] == kb)['wires'], 1) if x[0] == hb][0]
                B = S(BNAME[kb], hb, BCOL[kb], BSTEP[kb], BSUB[kb], 'P')
                B.update(board=kb, plan=j)
            elif tg:
                B = C(tg[0], gender(tg[0].split('.')[0], k))
            else:
                mod, pin = dest.split(' ', 1)
                B = S(mod, pin, 0, 1)
            il = w[7].get('inline') if len(w) > 7 else None   # resistor soldered in line near the board end
            wires.append(dict(colr=colr, awg=g, rings=rings, net=f'{net} → {il[2]}' if il else net, A=A, B=B,
                              note=f'{il[0]} {il[1]} soldered in line ~2 cm from the board end, in heat-shrink' if il else ''))
            if len(tg) > 1:   # chained on to a second connector: a jumper from the first contact
                wires.append(dict(colr=colr, awg=g, rings=rings, net=net, A=C(tg[0], 'F'), B=C(tg[1], 'F'),
                                  note=f'double contact in {tg[0].split(".")[0]} (with the wire from P2)'))
    for colr, g, rings, net, A, B, step, note in EXTRA:
        wires.append(dict(colr=colr, awg=g, rings=rings, net=net, A=A, B=B, note=note, step=step))
    for w in wires:
        w.setdefault('step', max(w['A']['step'], w['B']['step']))
        w['start'] = min(w['A']['step'], w['B']['step'], w['step'])
        lo, hi = sorted((w['A']['col'], w['B']['col']))
        w['tubes'] = [TUBE[c] for c in range(lo, hi)]
    wires.sort(key=lambda w: (w['step'], w['start'], w['A']['col'], w['A']['block'], w['B']['block']))
    geo = geometry()
    for n, w in enumerate(wires, 1):
        w['n'] = n
        w['len'], w['cut'] = length(w, geo)
    return wires


def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;')


def sym(kind, g='', x=0, y=0):
    if kind == 'S':
        return f'<circle cx="{x}" cy="{y}" r="5.5" fill="#8e979c" stroke="var(--ink)" stroke-width="1"/>'
    fill, lab, w = ('#2a62d6', 'D', 17) if kind == 'D' else ('#f07800', 'XH', 25)
    return (f'<rect x="{x - w / 2}" y="{y - 7}" width="{w}" height="14" rx="2" fill="{fill}"/>'
            f'<text x="{x}" y="{y + 3.6}" font-size="9.5" text-anchor="middle" fill="#fff" font-weight="700" font-family="var(--f-mono)">{lab}{g}</text>')


def sym_html(e):
    if e['kind'] == 'S':
        return '<span class="e s">●</span>'
    return f'<span class="e {"d" if e["kind"] == "D" else "x"}">{"D" if e["kind"] == "D" else "XH"}{e["g"]}</span>'


def end_text(e):
    if e['kind'] == 'S':
        if 'board' in e:
            return f'<b>{e["block"]}</b> {e["sub"]} · hole {e["port"]} <small>(wire {e["plan"]} of the plan)</small>'
        return f'{e["block"]} · {e["port"]}'
    title = CONNS[e['ref']][0].split(' · ')[0]
    return f'<b>{e["ref"]}</b> {title} · case {e["port"]}'


def wire_swatch(w):
    r = w['rings']
    rings = (f'<i class="band" style="background:{KIT[r]}"></i>' if isinstance(r, str)
             else ''.join('<i></i>' for _ in range(r)))
    return f'<span class="sw{" big" if w["awg"] == 26 else ""}" style="background:{KIT[w["colr"]]}">{rings}</span>'


def pt_size(svg, portrait):
    """printed size (pt) of the 12 px diagram text on an A4 page, 8 mm margins and a caption line"""
    W, H = (float(v) for v in svg.split('viewBox="0 0 ')[1].split('"')[0].split())
    pw, ph = (194, 262) if portrait else (281, 172)
    return 12 * min(pw / W, ph / H) / 0.3528


def diagrams(step, wires):
    """the step's diagram(s): when its text would print under 6.5 pt, the wires that cross a tube and the local ones
    go on two pages; each page in the orientation (A4 landscape or portrait) that prints it larger"""
    done = [w for w in wires if w['step'] == step]
    started = [w for w in wires if w['start'] == step and w['step'] > step]
    parts = [('', done, started)]
    one = diagram(step, done, started)
    if max(pt_size(one, False), pt_size(one, True)) < 6.5:
        sets = sorted({tuple(w['tubes']) for w in done + started}, key=lambda t: (len(t), t))
        cross = [(f'wires through {" + ".join(t)}' if t else 'local wires', [w for w in done if tuple(w['tubes']) == t],
                  [w for w in started if tuple(w['tubes']) == t]) for t in sets]
        best = lambda d, st: max(pt_size(diagram(step, d, st), False), pt_size(diagram(step, d, st), True))
        merged = []
        for what, d, st in cross:   # put small groups together while the text stays at 7 pt or more
            if merged and best(merged[-1][1] + d, merged[-1][2] + st) >= 7:
                merged[-1] = (merged[-1][0] + ', ' + what.replace('wires ', ''), merged[-1][1] + d, merged[-1][2] + st)
            else:
                merged.append((what, d, st))
        if len(merged) > 1:
            parts = merged
    out = []
    for k, (what, d, st) in enumerate(parts, 1):
        svg = one if len(parts) == 1 else diagram(step, d, st)
        portrait = pt_size(svg, True) > pt_size(svg, False) * 1.08
        cap = f'diagram {k}/{len(parts)}: {what}' if len(parts) > 1 else 'diagram'
        out.append((cap, svg, portrait))
    return out


def diagram(step, done, started):
    """blocks in TARS's columns (left leg on the left), one row per wire end, wires drawn between them"""
    blocks = {}   # name -> dict(col, ports: [(port label, end, wire, side)])
    for w in done:
        for e, o in ((w['A'], w['B']), (w['B'], w['A'])):
            blocks.setdefault(e['block'], dict(col=e['col'], ports=[], sub=e['sub'], frame=e['frame']))['ports'].append((e, o, w, False))
    for w in started:
        e = w['A'] if w['A']['step'] == step else w['B']
        o = w['B'] if e is w['A'] else w['A']
        blocks.setdefault(e['block'], dict(col=e['col'], ports=[], sub=e['sub'], frame=e['frame']))['ports'].append((e, o, w, True))
    # two lanes per TARS column: what gets soldered (boards, modules), then the connector sides
    def lane_of(col, kind):
        return col * 2 + (0 if kind == 'S' else 1)
    for name, b in blocks.items():
        b['lane'] = lane_of(b['col'], b['ports'][0][0]['kind'])
    lanes = sorted({b['lane'] for b in blocks.values()})
    BW, RH, TOP = 255, 19, 64
    LX, x = {}, 120
    for i, ln_ in enumerate(lanes):
        if i:
            x += BW + (32 if ln_ // 2 == lanes[i - 1] // 2 else 96)
        LX[ln_] = x
    order = sorted(blocks, key=lambda n: (blocks[n]['lane'], blocks[n]['frame'] != 'P',
                                          int(n[1:].split()[0]) if n[0] == 'X' and n[1].isdigit() else 0, n))
    rank = {n: k for k, n in enumerate(order)}
    y_of, lane_y, out = {}, {l: TOP for l in lanes}, []
    for name in order:
        b = blocks[name]
        lane = b['lane']

        def side(p):
            pl = lane_of(p[1]['col'], p[1]['kind'])
            return 1 if pl > lane else -1 if pl < lane else (-1 if lane % 2 == 0 else 1)
        b['ports'].sort(key=lambda p: (side(p), lane_of(p[1]['col'], p[1]['kind']), rank.get(p[1]['block'], 999), p[2]['n']))
        x, y = LX[lane], lane_y[lane]
        h = 46 + RH * len(b['ports'])
        fc, ft = FRAME[b['frame']]
        out.append(f'<rect x="{x}" y="{y}" width="{BW}" height="{h}" rx="5" fill="var(--block)" stroke="{fc}" stroke-width="2.6"/>')
        out.append(f'<rect x="{x + BW - 62}" y="{y + 6}" width="56" height="16" rx="3" fill="{fc}"/>')
        out.append(f'<text x="{x + BW - 34}" y="{y + 18}" class="tg" text-anchor="middle">{ft}</text>')
        out.append(f'<text x="{x + 10}" y="{y + 19}" class="bt">{esc(name)}</text>')
        out.append(f'<text x="{x + 10}" y="{y + 35}" class="pt m">{esc(b["sub"])}</text>')
        for k, p in enumerate(b['ports']):
            e, o, w, stub = p
            py = y + 52 + k * RH
            right = side(p) > 0
            y_of[(w['n'], id(e))] = (x + BW if right else x, py, right)
            x0 = x + (12 if right else 70)
            out.append(f'<text x="{x0}" y="{py + 4}" class="pt">{esc(e["port"])}</text>')
            out.append(f'<text x="{x0 + 70}" y="{py + 4}" class="pt m">{esc(w["net"])}</text>')
            if stub:
                out.append(f'<text x="{x0 + 128}" y="{py + 4}" class="ps">→ st. {w["step"]}</text>')
            out.append(f'<text x="{x + BW - 30 if right else x + 30}" y="{py + 4}" class="pw" text-anchor="{"end" if right else "start"}">W{w["n"]}</text>')
        lane_y[lane] = y + h + 22
    H = max(lane_y.values()) + 10
    W = LX[lanes[-1]] + BW
    bg = []
    cols = sorted({l // 2 for l in lanes})
    for c in cols:
        bg.append(f'<text x="{LX[min(l for l in lanes if l // 2 == c)]}" y="48" class="cl">{COLNAME[c]}</text>')
    for c1, c2 in zip(cols, cols[1:]):
        xa = LX[max(l for l in lanes if l // 2 == c1)] + BW
        xb = LX[min(l for l in lanes if l // 2 == c2)]
        xm = (xa + xb) / 2
        bg.append(f'<rect x="{xm - 22}" y="28" width="44" height="{H - 40}" rx="8" fill="var(--tube)"/>')
        bg.append(f'<text x="{xm}" y="20" class="tl" text-anchor="middle">{esc(" + ".join(TUBE[c] for c in range(c1, c2)))}</text>')
    ln, sy = [], []
    for w in done:
        a = y_of[(w['n'], id(w['A']))]
        b = y_of[(w['n'], id(w['B']))]
        (x1, y1, r1), (x2, y2, r2) = a, b
        if r1 == r2:   # loop on the same side of a lane
            d1 = d2 = min(150, 40 + abs(y2 - y1) * .25) * (1 if r1 else -1)
        else:
            k = max(60, abs(x2 - x1) * .45)
            d1, d2 = (k if r1 else -k), (k if r2 else -k)
        path = f'M{x1} {y1} C{x1 + d1} {y1} {x2 + d2} {y2} {x2} {y2}'
        wd = 4.2 if w['awg'] == 26 else 2.6
        ln.append(f'<path d="{path}" fill="none" stroke="var(--casing)" stroke-width="{wd + 1.6}"/>')
        ln.append(f'<path d="{path}" fill="none" stroke="{KIT[w["colr"]]}" stroke-width="{wd}"/>')
        for e, (x, y, r) in ((w['A'], a), (w['B'], b)):
            sy.append(sym(e['kind'], e.get('g', ''), x + (-15 if r else 15), y))
    for w in started:
        e = w['A'] if w['A']['step'] == step else w['B']
        x, y, r = y_of[(w['n'], id(e))]
        x2 = x + (22 if r else -22)
        wd = 4.2 if w['awg'] == 26 else 2.6
        ln.append(f'<path d="M{x} {y} L{x2} {y}" stroke="var(--casing)" stroke-width="{wd + 1.6}"/>')
        ln.append(f'<path d="M{x} {y} L{x2} {y}" stroke="{KIT[w["colr"]]}" stroke-width="{wd}"/>')
        ln.append(f'<path d="M{x2} {y - 5} l{6 if r else -6} 5 l{-6 if r else 6} 5" fill="none" stroke="var(--ink)" stroke-width="1.6"/>')
        sy.append(sym(e['kind'], e.get('g', ''), x + (-15 if r else 15), y))
    W += 150
    return (f'<svg viewBox="0 0 {W} {H}" width="{W}" role="img" aria-label="Step {step}: wires and their ends">'
            + ''.join(bg) + ''.join(ln) + ''.join(out) + ''.join(sy) + '</svg>')


def table(ws, show_step=False):
    rows = []
    for w in ws:
        rg = rings_text(w['rings'])
        tubes = ' + '.join(w['tubes']) or '—'
        extra = f'<br><small>{esc(w["note"])}</small>' if w['note'] else ''
        st = f'<td class="n">{w["start"]}{"→" + str(w["step"]) if w["start"] != w["step"] else ""}</td>' if show_step else ''
        rows.append(f'<tr><td class="n">W{w["n"]}</td>{st}<td>{wire_swatch(w)} {NAME[w["colr"]]} {w["awg"]} AWG{rg}</td>'
                    f'<td class="m">{esc(w["net"])}</td><td>{sym_html(w["A"])} {end_text(w["A"])}</td>'
                    f'<td>{sym_html(w["B"])} {end_text(w["B"])}{extra}</td><td>{tubes}</td><td class="n">{w["len"]}<small> → {w["cut"]}</small></td></tr>')
    st = '<th>step</th>' if show_step else ''
    return (f'<div class="tbl"><table><tr><th>wire</th>{st}<th>colour</th><th>signal</th><th>end A</th><th>end B</th>'
            f'<th>tubes</th><th>length cm<br><small>estimated → to cut</small></th></tr>{"".join(rows)}</table></div>')


def page(wires):
    steps = []
    for n, title, sub, prep, tests in STEPS:
        done = [w for w in wires if w['step'] == n]
        started = [w for w in wires if w['start'] == n and w['step'] > n]
        crimp = sorted({(e['ref'], e['g']) for w in done for e in (w['A'], w['B']) if e['kind'] != 'S'},
                       key=lambda r: (int(r[0][1:]), r[1]))
        crimp_txt = ', '.join(f'{r} {g}' for r, g in crimp) or 'none'
        st = ''
        if started:
            st = (f'<h4>Wires started here, finished later ({len(started)})</h4>'
                  f'<p class="small">One end only now; the other stays bare until the step shown.</p>{table(started, True)}')
        steps.append(f'''
  <section class="step" id="e{n}">
    <h2><span class="num">{n}</span> {esc(title)}</h2>
    <p class="sub">{esc(sub)} · {len(done)} wires finished · housings to fill: {crimp_txt}</p>
    <div class="cols">
      <div><h4>Before</h4><ol>{"".join(f"<li>{esc(p)}</li>" for p in prep)}</ol></div>
      <div><h4>Bench test</h4><ul class="tests">{"".join(f"<li>{esc(t)}</li>" for t in tests)}</ul></div>
    </div>
    {"".join(f'<div class="sheet{" portrait" if pr else ""}"><p class="cap">Step {n} · {esc(title)}: {cap}</p>{svg}</div>' for cap, svg, pr in diagrams(n, wires))}
    <h4>Wires finished at this step ({len(done)})</h4>
    {table(done)}
    {st}
  </section>''')
    conn_cards = []
    for ref in sorted(CONNS, key=lambda r: int(r[1:])):
        title, pins = CONNS[ref]
        cells = ''.join('<span class="gap"></span>' if p == '|' else
                        f'<span class="cell{" key" if net == "key" else ""}"><b>{esc(p)}</b><small>{"plugged" if net == "key" else esc(net or "empty")}</small></span>'
                        for p, net in pins)
        kind = 'x' if ref in XH else 'd'
        conn_cards.append(f'<div class="card"><p><span class="e {kind}">{ref}</span> {esc(title)}</p><div class="pins">{cells}</div></div>')
    n26 = sum(1 for w in wires if w['awg'] == 26)
    geo_pz = json.load(open(GEO_CACHE))['pivot_z']
    tot = {}
    for w in wires:
        tot[(w['awg'], w['colr'])] = tot.get((w['awg'], w['colr']), 0) + w['cut']
    rows = ''.join(f'<tr><td>{wire_swatch(dict(awg=g, colr=c, rings=0))} {NAME[c]}</td><td class="n">{g} AWG</td>'
                   f'<td class="n">{sum(1 for w in wires if (w["awg"], w["colr"]) == (g, c))}</td><td class="n">{v / 100:.2f} m</td></tr>'
                   for (g, c), v in sorted(tot.items(), key=lambda kv: (-kv[0][0], -kv[1])))
    t30 = sum(v for (g, _), v in tot.items() if g == 30) / 100
    t26 = sum(v for (g, _), v in tot.items() if g == 26) / 100
    totals = (f'<div class="tbl"><table><tr><th>colour</th><th>gauge</th><th>wires</th><th>to cut</th></tr>{rows}'
              f'<tr><td><b>total 30 AWG</b></td><td></td><td></td><td class="n">{t30:.2f} m</td></tr>'
              f'<tr><td><b>total 26 AWG</b></td><td></td><td></td><td class="n">{t26:.2f} m</td></tr></table></div>')
    return f'''<title>TARS4 wiring guide</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Sans+Condensed:wght@600&display=swap">
<style>
/* Generated by tools/harness.py: edit the script, not this file. */
:root {{
  --paper: #f3f4f1; --sheet: #fbfbf9; --ink: #1d2226; --muted: #5e676d; --rule: #c9cec9; --block: #eef1ec;
  --edge: #7b858a; --tube: #e6dcc6; --casing: #4c555b;
  --f-display: "IBM Plex Sans Condensed", "Arial Narrow", sans-serif;
  --f-body: "IBM Plex Sans", system-ui, sans-serif;
  --f-mono: "IBM Plex Mono", ui-monospace, Consolas, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --paper: #15191c; --sheet: #1b2024; --ink: #e5e8e6; --muted: #98a2a7; --rule: #3a4248; --block: #232a2f;
  --edge: #8a959b; --tube: #3d3729; --casing: #aab4ba; color-scheme: dark }} }}
:root[data-theme="dark"] {{
  --paper: #15191c; --sheet: #1b2024; --ink: #e5e8e6; --muted: #98a2a7; --rule: #3a4248; --block: #232a2f;
  --edge: #8a959b; --tube: #3d3729; --casing: #aab4ba; color-scheme: dark }}
body {{ background: var(--paper); color: var(--ink); font: 15px/1.5 var(--f-body); margin: 0;
  padding: 24px max(16px, env(safe-area-inset-right, 0px)) 48px max(16px, env(safe-area-inset-left, 0px)); }}
.wrap {{ max-width: 1500px; margin: 0 auto; display: grid; grid-template-columns: minmax(0, 1fr); gap: 28px; }}
h1 {{ font: 600 30px/1.1 var(--f-display); margin: 0; }}
h2 {{ font: 600 22px/1.2 var(--f-display); margin: 0 0 4px; display: flex; gap: 12px; align-items: center; }}
h3 {{ font: 600 13px var(--f-mono); text-transform: uppercase; letter-spacing: .08em; color: var(--muted); margin: 0 0 10px; }}
h4 {{ font: 600 14px var(--f-body); margin: 18px 0 6px; }}
p {{ margin: 0; }}
.lead {{ color: var(--muted); max-width: 80ch; margin-top: 6px; }}
.num {{ display: inline-grid; place-items: center; width: 34px; height: 34px; border-radius: 50%; background: var(--ink); color: var(--paper); font: 600 18px var(--f-mono); }}
.sub, .small {{ color: var(--muted); font-size: 13.5px; }}
.step {{ min-width: 0; background: var(--sheet); border: 1px solid var(--rule); border-radius: 6px; padding: 18px 20px; }}
.cols {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 420px), 1fr)); gap: 8px 32px; }}
ol, ul {{ margin: 0; padding-left: 20px; font-size: 14px; }}
.tests li::marker {{ content: "☐  "; }}
.sheet {{ overflow-x: auto; margin-top: 14px; border: 1px solid var(--rule); border-radius: 4px; background: var(--paper); }}
.sheet svg {{ display: block; height: auto; max-width: none; }}
.tbl {{ overflow-x: auto; }}
table {{ width: 100%; border-collapse: collapse; font-size: 13.5px; font-variant-numeric: tabular-nums; }}
th, td {{ text-align: left; padding: 5px 7px; border-bottom: 1px solid var(--rule); vertical-align: top; }}
th {{ font: 600 12px var(--f-mono); color: var(--muted); }}
td.n {{ font: 600 13.5px var(--f-mono); white-space: nowrap; }}
td.m {{ font-family: var(--f-mono); font-size: 13px; }}
td small {{ color: var(--muted); }}
.e {{ display: inline-block; min-width: 22px; padding: 0 4px; border-radius: 3px; font: 700 11px/17px var(--f-mono); color: #fff; text-align: center; vertical-align: 1px; }}
.e.s {{ background: none; color: #8e979c; font-size: 17px; min-width: 14px; padding: 0; }}
.e.d {{ background: #2a62d6; }}
.e.x {{ background: #f07800; }}
.sw {{ display: inline-flex; gap: 2px; align-items: center; justify-content: center; width: 30px; height: 8px; border-radius: 2px; box-shadow: 0 0 0 1px var(--casing); vertical-align: 2px; }}
.sw.big {{ height: 12px; }}
.sw i {{ width: 2px; height: 100%; background: var(--ink); }}
.sw i.band {{ width: 6px; box-shadow: 0 0 0 1px var(--ink); }}
.legend {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 330px), 1fr)); gap: 10px 28px; }}
.legend div {{ display: grid; grid-template-columns: 54px 1fr; gap: 10px; align-items: start; font-size: 14px; }}
.legend .e {{ justify-self: start; }}
.cards {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 330px), 1fr)); gap: 12px; }}
.card {{ background: var(--sheet); border: 1px solid var(--rule); border-radius: 5px; padding: 10px 12px; font-size: 13.5px; }}
.pins {{ display: flex; flex-wrap: wrap; gap: 3px; margin-top: 6px; }}
.cell {{ display: grid; min-width: 44px; padding: 2px 4px; border: 1px solid var(--edge); border-radius: 3px; text-align: center; font-family: var(--f-mono); font-size: 11px; }}
.cell small {{ color: var(--muted); font-size: 10px; }}
.cell.key {{ background: var(--rule); }}
.gap {{ width: 10px; }}
.cap {{ display: none; font: 600 13px var(--f-mono); color: var(--muted); margin: 0 0 2mm; }}
.fr {{ display: inline-grid; place-items: center; width: 34px; height: 22px; border: 2.6px solid; border-radius: 4px; font: 700 12px var(--f-mono); background: var(--block); }}
@media print {{
  :root, :root[data-theme="dark"], :root:not([data-theme="light"]) {{
    --paper: #fff; --sheet: #fff; --ink: #1d2226; --muted: #5e676d; --rule: #c9cec9; --block: #f3f5f2;
    --edge: #7b858a; --tube: #ece4d2; --casing: #4c555b; color-scheme: light; }}
  body {{ padding: 0; font-size: 10pt; background: #fff; }}
  .wrap {{ display: block; max-width: none; }}
  .wrap > * {{ margin-bottom: 5mm; }}
  .cols {{ grid-template-columns: 1fr 1fr; gap: 2mm 8mm; }}
  .cols ol, .cols ul {{ font-size: 9pt; }}
  nav {{ display: none; }}
  .step {{ break-before: page; border: 0; padding: 0; border-radius: 0; }}
  .sheet {{ overflow: visible; margin-top: 3mm; background: #fff; }}
  .sheet {{ break-before: page; border: 0; margin: 0; }}
  .sheet + h4 {{ break-before: page; }}
  .sheet .cap {{ display: block; }}
  .sheet.portrait svg {{ max-height: 172mm; }}
  .sheet svg {{ width: 100% !important; height: auto; max-height: 172mm; }}
  .tbl {{ overflow: visible; }}
  table {{ font-size: 8pt; }}
  th, td {{ padding: 2px 4px; }}
  tr, .card {{ break-inside: avoid; }}
  h2, h4 {{ break-after: avoid; }}
  #conn {{ break-before: page; }}
  #long table {{ width: auto; }}
  .cards {{ grid-template-columns: repeat(3, 1fr); }}
}}
nav ol {{ display: flex; flex-wrap: wrap; gap: 6px 18px; list-style: none; padding: 0; }}
nav a {{ color: var(--ink); }}
svg .bt {{ font: 600 14px var(--f-display); fill: var(--ink); }}
svg .pt {{ font: 12px var(--f-mono); fill: var(--ink); }}
svg .tg {{ font: 700 10px var(--f-mono); fill: #fff; }}
svg .pt.m {{ fill: var(--muted); font-size: 11px; }}
svg .tl {{ font: 600 12px var(--f-mono); fill: var(--muted); }}
svg .cl {{ font: 600 12px var(--f-mono); fill: var(--muted); text-transform: uppercase; letter-spacing: .06em; }}
svg .pw {{ font: 700 11px var(--f-mono); fill: var(--ink); }}
svg .ps {{ font: 600 11px var(--f-mono); fill: #c0392b; }}
</style>
<div class="wrap">
  <header>
    <h1>TARS4 — wiring guide</h1>
    <p class="lead">The {len(wires)} TARS wires ({n26} in 26 AWG, the rest in 30 AWG), in build order. Each step is tested
    on the bench before the next; everything is done outside TARS, fitting comes at the end. The board plans
    (renders/tars4_board_*.svg) give hole by hole, this guide gives both ends of every wire.</p>
  </header>
  <section>
    <h3>Wire end code (the same on the board plans)</h3>
    <div class="legend">
      <div><span class="e s">●</span><span><b>Soldered</b>: on a board hole (plan shown) or on a module pad / lead. Tin the wire, solder, heat-shrink over the joint if it is exposed.</span></div>
      <div><span class="e d">DF</span><span><b>Dupont, female contact</b> crimped (SN-28B, 30 AWG folded in two; two wires in one contact: together, without folding), slid into housing Xn at the cavity shown (cavity 1 = pin 1, paint dot).</span></div>
      <div><span class="e d">DM</span><span><b>Dupont, male contact</b>: the module side of an inline pair (pigtails of X3, X7, X15).</span></div>
      <div><span class="e x">XHF</span><span><b>JST-XH female</b> crimped, on the power block side (X10, X13, X14) or the cell side (X12).</span></div>
      <div><span class="e x">XHM</span><span><b>JST-XH male</b> crimped, the other side of the pair.</span></div>
      <div><span class="sw" style="background:#f07800"><i></i><i></i></span><span><b>Wire colour</b>, thick = 26 AWG, strokes = black heat-shrink rings at both ends (1 = I2S / PIR, 2 = I2C, 3 = microSD).</span></div>
      <div><span class="sw big" style="background:#d7262b"><i class="band" style="background:#f07800"></i></span><span><b>Power pairs</b>: red / black = battery and 5 V, white / blue = regulated 3V3. Rails sharing red / black carry a <b>coloured band</b> (10 mm of coloured heat-shrink, shrunk 2–3 cm from each end, the same on the + and on its GND): none = cell B+ / B−, <b>white</b> = TP4056 OUT+ / OUT−, <b>yellow</b> = VPATH, <b>orange</b> = VSYS, <b>purple</b> = VUSB. Slip the band on before soldering or crimping.</span></div>
    </div>
  </section>
  <section>
    <h3>Diagram blocks (frame colour)</h3>
    <div class="legend frames">
      <div><span class="fr" style="border-color:#2f8f5b">P</span><span><b>Hand-wired board</b>: P1, P2 (stripboards), P3 S3 carrier, P4 power path (pad perfboards); plans renders/tars4_board_*.svg.</span></div>
      <div><span class="fr" style="border-color:#8e44c4">M</span><span><b>Module or part</b> under its name: TP4056, TPS63020, INMP441, AM312, microSD reader, switch, cells, speaker…</span></div>
      <div><span class="fr" style="border-color:#2a62d6">X</span><span><b>Dupont connector</b>, one side (female or male); cavities are numbered from pin 1.</span></div>
      <div><span class="fr" style="border-color:#f07800">X</span><span><b>JST-XH connector</b>, one side (female or male).</span></div>
    </div>
  </section>
  <nav><h3>Steps</h3><ol>{"".join(f'<li><a href="#e{n}">{n}. {esc(t)}</a></li>' for n, t, *_ in STEPS)}<li><a href="#long">Lengths</a></li><li><a href="#tous">Full list</a></li><li><a href="#conn">Connectors</a></li></ol></nav>
  <p class="small">In the diagrams, TARS is seen from the front (left leg on the left), one column per TARS column, the tubes between them. A block = a board, a module or one side of a connector; each line = one wire end. A wire started at one step and finished later leaves the block with an arrow "→ st. n".</p>
  {"".join(steps)}
  <section class="step" id="long"><h2>Wire lengths</h2>
    <p class="sub">Taken from the 3D model (tars4.scad): route from one end to the other along the column, through the pivot (z {geo_pz:.0f}) when the wire changes column, +10 % for bends, + service loop at each end (7 cm at the P3 carrier, 4 cm at connectors, 2–3 cm at boards and modules), + 3 cm per tube (leg rotation). Length to cut = estimated + {TOL} cm; module pigtails are {PIGTAIL} cm. Cut at assembly time, after offering the wire up in TARS if possible.</p>
    {totals}
  </section>
  <section class="step" id="tous"><h2>Full wire list</h2><p class="sub">step where it is started → finished</p>{table(wires, True)}</section>
  <section id="conn"><h3>Connectors (harness side, cavity 1 on the left)</h3><div class="cards">{"".join(conn_cards)}</div></section>
</div>
'''


def main():
    wires = collect()
    # every contact of a connector side gets at most two wires (double contacts are documented)
    seen = {}
    for w in wires:
        for e in (w['A'], w['B']):
            if e['kind'] != 'S':
                seen.setdefault((e['ref'], e['g'], e['pin']), []).append(w['n'])
    bad = [f'{k}: {v}' for k, v in seen.items() if len(v) > 2]
    if bad:
        print('more than two wires in a contact:', *bad, sep='\n  ')
        sys.exit(1)
    with open(HTML, 'w', encoding='utf-8') as fh:
        fh.write(page(wires))
    print(f'tars4_harness.html: {len(wires)} wires, {len(STEPS)} steps, '
          f'{sum(1 for v in seen.values() if len(v) == 2)} double contacts')
    if '--no-pdf' not in sys.argv and shutil.which('firefox'):
        make_pdf()


def pin_dates(path):
    """fixed creation / modification dates (same length, offsets unchanged): an unchanged guide gives the same bytes"""
    b = open(path, 'rb').read()
    b = re.sub(rb'/(CreationDate|ModDate) ?\(D:\d{14}', lambda m: m.group(0)[:-14] + b'20000101000000', b)
    open(path, 'wb').write(b)


def make_pdf():
    """printable copy through headless Firefox: the document in A4 landscape, then every portrait diagram printed on
    its own A4 portrait page and put in place of its landscape page (gs splits, pdfunite joins)"""
    tool = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'html2pdf.py')
    pdf = lambda src, dst, *opt: subprocess.run([sys.executable, '-I', tool, src, dst, *opt], check=True, timeout=180,
                                                stdout=subprocess.DEVNULL)
    src = open(HTML, encoding='utf-8').read()
    head = src[:src.index('<div class="wrap">')]
    sheets = [s.split('</svg></div>')[0] + '</svg></div>' for s in src.split('<div class="sheet portrait">')[1:]]
    with tempfile.TemporaryDirectory() as d:
        main_html = os.path.join(d, 'main.html')   # portrait diagrams left out: only their caption, a page to replace
        with open(main_html, 'w', encoding='utf-8') as fh:
            parts = src.split('<div class="sheet portrait">')
            fh.write(parts[0] + ''.join('<div class="sheet portrait">' + q.split('<svg ')[0] + '</div>' + q.split('</svg></div>', 1)[1]
                                        for q in parts[1:]))
        pdf(main_html, os.path.join(d, 'main.pdf'))
        if not sheets or not (shutil.which('gs') and shutil.which('pdfunite') and shutil.which('pdftotext')):
            shutil.copy(os.path.join(d, 'main.pdf'), PDF)
            pin_dates(PDF)
            print('wrote tars4_harness.pdf (landscape only)')
            return
        n = int(subprocess.run(['gs', '-q', '-dNODISPLAY', '-dNOSAFER', '-c',
                                f'({os.path.join(d, "main.pdf")}) (r) file runpdfbegin pdfpagecount = quit'],
                               capture_output=True, text=True).stdout.split()[-1])
        subprocess.run(['gs', '-q', '-dNOPAUSE', '-dBATCH', '-sDEVICE=pdfwrite', f'-sOutputFile={d}/p%03d.pdf',
                        os.path.join(d, 'main.pdf')], check=True)
        pages = [os.path.join(d, f'p{i:03d}.pdf') for i in range(1, n + 1)]
        for k, sh in enumerate(sheets):
            cap = sh.split('<p class="cap">')[1].split('</p>')[0].replace('&amp;', '&')
            one = os.path.join(d, f'portrait{k}.html')
            with open(one, 'w', encoding='utf-8') as fh:
                fh.write(head + '<style>@media print { .sheet { break-before: auto !important; } .sheet svg { max-height: 262mm !important; } }</style>'
                         + '<div class="wrap"><div class="sheet">' + sh + '</div>')
            pdf(one, os.path.join(d, f'portrait{k}.pdf'), '--portrait')
            for i, pg in enumerate(pages):
                txt = subprocess.run(['pdftotext', '-layout', pg, '-'], capture_output=True, text=True).stdout
                if ' '.join(cap.split()[:4]) in ' '.join(txt.split()) and ' '.join(cap.split()) .split(' : ')[-1] in ' '.join(txt.split()):
                    pages[i] = os.path.join(d, f'portrait{k}.pdf')
                    break
        subprocess.run(['pdfunite', *pages, PDF], check=True)
    pin_dates(PDF)
    print(f'wrote tars4_harness.pdf ({len(sheets)} diagram(s) in portrait)')


if __name__ == '__main__':
    main()
