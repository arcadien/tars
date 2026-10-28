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
