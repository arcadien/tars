"""Acceptance tests of the requirements, read from the KiCad project itself (not from tools/kicad_sch_gen.py).

The schematic is exported once per run as a KiCad XML netlist (kicad-cli, or the KiCad AppImage named by $KICAD) and
read with the standard library. Nets are found through their pins: most of them have generated names such as
"Net-(BT1-+)" that change when parts are renumbered; only the labelled nets (+3V3, GND, /USB_DET...) are named.
"""
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCH = os.path.join(ROOT, 'hardware', 'kicad', 'tars4.kicad_sch')
sys.path.insert(0, os.path.join(ROOT, 'tools'))   # boards.py / harness.py wire lists


def pytest_configure(config):
    config.addinivalue_line('markers', 'req(id): requirement whose acceptance criterion the test checks')


class Netlist:
    def __init__(self, path):
        root = ET.parse(path).getroot()
        self.parts = {c.get('ref'): c.find('libsource').get('part') for c in root.iter('comp')}
        self.values = {c.get('ref'): c.findtext('value') for c in root.iter('comp')}
        self.nets = {n.get('name'): {(x.get('ref'), x.get('pin')) for x in n.iter('node')} for n in root.iter('net')}
        self.net_of = {pin: name for name, pins in self.nets.items() for pin in pins}

    def net(self, ref, pin):
        """name of the net on pin `pin` of `ref`"""
        return self.net_of[(ref, pin)]

    def pins(self, ref, pin):
        """every (ref, pin) on the same net as pin `pin` of `ref`"""
        return self.nets[self.net(ref, pin)]

    def part_nets(self, ref):
        """{pin: net} of every connected pin of `ref`"""
        return {p: name for (r, p), name in self.net_of.items() if r == ref}

    def refs(self, part):
        """references of the parts drawn with library symbol `part` (e.g. 'TP4056_DW01', 'Polyfuse')"""
        return sorted(r for r, p in self.parts.items() if p == part)


@pytest.fixture(scope='session')
def sch(tmp_path_factory):
    if os.environ.get('TARS_NETLIST'):   # a given netlist (e.g. a deliberately broken one, to see a test fail)
        return Netlist(os.environ['TARS_NETLIST'])
    out = str(tmp_path_factory.mktemp('netlist') / 'tars4.xml')
    cli = [os.environ['KICAD'], 'kicad-cli'] if os.environ.get('KICAD') else [shutil.which('kicad-cli') or 'kicad-cli']
    subprocess.run([*cli, 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', out, SCH], check=True,
                   capture_output=True)
    return Netlist(out)
