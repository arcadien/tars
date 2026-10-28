"""PLAT-MECH acceptance criteria checked on the model (requirements/platform.md): mechanical/scad/tars4.scad is
evaluated once by OpenSCAD without any export (part="none"), its echoed values and WARNINGs are read back."""
import os
import re
import shutil
import subprocess

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAD = os.path.join(ROOT, 'mechanical', 'scad', 'tars4.scad')
VALUES = ('tube_od', 'tube_glue_clr', 'tube_run_clr')


@pytest.fixture(scope='session')
def model(tmp_path_factory):
    d = tmp_path_factory.mktemp('model')
    probe = d / 'probe.scad'
    probe.write_text(f'include <{SCAD.replace(os.sep, "/")}>\necho({", ".join(f"{v}={v}" for v in VALUES)});\n',
                     encoding='utf-8')
    run = subprocess.run([shutil.which('openscad') or 'openscad', '-D', 'part="none"', '-o', str(d / 'm.echo'),
                          str(probe)], capture_output=True, text=True, timeout=300)
    echo = (d / 'm.echo').read_text(encoding='utf-8') + run.stdout + run.stderr
    line = next(ln for ln in echo.splitlines() if ln.startswith(f'ECHO: {VALUES[0]} ='))
    values = {k: float(v) for k, v in re.findall(r'(\w+) = ([-\d.]+)', line)}
    return values, [ln for ln in echo.splitlines() if 'WARNING' in ln or 'ERROR' in ln]


def source():
    return open(SCAD, encoding='utf-8').read()


@pytest.mark.req('PLAT-MECH-CHARGEPORT-001')
def test_plat_mech_chargeport_001_charge_port_geometry_asserts_hold(model):
    # Given the model and its charge-port geometry asserts (axis, mouth depth, height, clearances)
    asserts = re.findall(r'echo\("WARNING: charge port', source())
    assert len(asserts) >= 6, 'charge port asserts removed from tars4.scad'
    # When it is evaluated
    _, warnings = model
    # Then it prints no WARNING / ERROR at all (make check clean)
    assert warnings == []

