"""TECH-POWER acceptance criteria checked on the schematic (requirements/technical.md)."""
import pytest

import boards    # tools/, on the path through conftest.py
import harness


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


@pytest.mark.req('TECH-POWER-GROUND-001')
def test_tech_power_ground_001_no_load_ground_on_b_minus(sch):
    # Given the raw cell negative B- (the charger's B- pin)
    u = sch.refs('TP4056_DW01')[0]
    # When listing every pin on it
    pins = sch.pins(u, 'B-')
    # Then only the cell negatives and the protection's B- are there (loads return to GND, after the protection)
    assert pins == {(c, '2') for c in sch.refs('Battery_Cell')} | {(u, 'B-')}


@pytest.mark.req('TECH-POWER-REG-001')
def test_tech_power_reg_001_one_buck_boost_feeds_every_3v3_load(sch):
    # Given the single buck-boost regulator, the amplifier (fed from VSYS by design) and VSYS (switch SW1 output)
    reg, = sch.refs('TPS63020_3V3')
    amp, = sch.refs('MAX98357A')
    vsys = sch.net('SW1', '2')
    # Then the regulator sources +3V3 from VSYS
    assert sch.net(reg, 'VOUT') == '+3V3' and sch.net(reg, 'VIN') == vsys

    # fed by +3V3 = on +3V3, or behind at most one switch / filter part whose other pin is on it (microSD Q5, PIR RC);
    # reading of "every 3V3 load pin is on the +3V3 net" agreed on 2026-10-28
    def fed_by_3v3(net):
        return net == '+3V3' or any(sch.parts[r] in ('R', 'Q_PMOS') and '+3V3' in sch.part_nets(r).values()
                                    for r, _ in sch.nets[net])
    # When listing the supply pins of every 3.3 V load: all modules but the charger, the regulator and the
    # amplifier, plus the microSD reader
    loads = [r for r in sch.parts if r.startswith('U') and r not in (reg, amp, *sch.refs('TP4056_DW01'))]
    loads += sch.refs('microSD_3V3')
    for r in loads:
        supply = {p: n for p, n in sch.part_nets(r).items() if p in ('VCC', 'VDD', '3V', 'VIN')}
        assert supply, f'{r}: no supply pin found'
        # Then each one is fed by the +3V3 rail
        for p, n in supply.items():
            assert fed_by_3v3(n), f'{r}.{p} on {n}'
    # And no other module draws from VSYS (no linear regulator on the system rail)
    assert {r for r, _ in sch.nets[vsys] if r.startswith('U')} <= {reg, amp}


@pytest.mark.req('TECH-POWER-DIST-001')
def test_tech_power_dist_001_separate_vsys_pairs_for_regulator_and_amplifier(sch):
    # Given the regulator and the amplifier, both loads of VSYS in the schematic
    reg, = sch.refs('TPS63020_3V3')
    amp, = sch.refs('MAX98357A')
    vsys = sch.net('SW1', '2')
    assert sch.net(reg, 'VIN') == vsys and sch.net(amp, 'VIN') == vsys
    # When reading the power board's wire list (its GND bus is the star point)
    power = next(b for b in boards.BOARDS if b['key'] == 'power')
    star = next(holes for kind, holes, net in power['links'] if kind == 'bus' and net == 'GND')

    def wire(net, dest):
        ws = [w for w in power['wires'] if w[1] == net and dest in w[5]]
        assert len(ws) == 1, f'{net} → {dest}: {len(ws)} wires'
        return ws[0]
    # Then the regulator and the amplifier each get their own VSYS wire and their own GND wire from the star
    wire('VSYS', 'TPS63020 VIN')
    assert wire('VSYS', 'amplifier VIN')[6] == ['X13.VSYS']
    assert wire('GND', 'TPS63020 GND')[0] in star
    amp_gnd = wire('GND', 'amplifier GND')
    assert amp_gnd[0] in star and amp_gnd[6] == ['X13.GND amp']
    # And the 3V3 pair (3V3 + logic GND) leaves from the regulator's own pads
    starts = {e[5]['pin']: (e[4]['block'], e[4]['port']) for e in harness.EXTRA if e[5].get('ref') == 'X13'}
    assert starts['3V3'] == ('TPS63020', 'VOUT') and starts['GND log'] == ('TPS63020', 'GND')
