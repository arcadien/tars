"""TECH-POWER acceptance criteria checked on the schematic (requirements/technical.md)."""
import pytest


@pytest.mark.req('TECH-POWER-CELL-001')
def test_tech_power_cell_001_one_charger_both_cells_on_bat_plus_and_b_minus(sch):
    # Given the schematic
    # When the charger / protection modules and the two cell branches are looked up
    chargers = sch.refs('TP4056_DW01')
    cells = sch.refs('Battery_Cell')
    # Then there is exactly one charger / protection module and two cells
    assert len(chargers) == 1 and len(cells) == 2
    u = chargers[0]
    # And both cell negatives are on the module's B- net
    assert all(sch.net(c, '2') == sch.net(u, 'B-') for c in cells)
    # And each cell positive reaches the module's B+ net through its branch (fuse)
    for c in cells:
        branch = {r for r, _ in sch.pins(c, '1')} - {c}
        assert any(sch.net(r, p) == sch.net(u, 'B+') for r in branch for p in ('1', '2'))


@pytest.mark.req('TECH-POWER-PROTECT-002')
def test_tech_power_protect_002_one_polyfuse_between_each_cell_plus_and_bat_plus(sch):
    # Given the schematic and the charger's B+ net (BAT+)
    bat_plus = sch.net(sch.refs('TP4056_DW01')[0], 'B+')
    fuses = set()
    for c in sch.refs('Battery_Cell'):
        # When following each cell's + terminal
        others = sch.pins(c, '1') - {(c, '1')}
        # Then it meets exactly one part, a polyfuse
        assert len(others) == 1, f'{c} +: {sorted(others)}'
        (f, pin), = others
        assert sch.parts[f] == 'Polyfuse'
        # And that fuse's other pin is on BAT+
        assert sch.net(f, '2' if pin == '1' else '1') == bat_plus
        fuses.add(f)
    # And each cell has its own fuse
    assert len(fuses) == 2
