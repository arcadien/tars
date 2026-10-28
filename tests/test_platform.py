"""PLAT acceptance criteria checked on the schematic (requirements/platform.md)."""
import pytest

import harness   # tools/, on the path through conftest.py


def vusb(sch):
    """VUSB: the charger's IN+ net"""
    return sch.net(sch.refs('TP4056_DW01')[0], 'IN+')


def s3_pin(sch, gpio):
    """net on GPIO `gpio` of the S3 Mini"""
    return sch.net(sch.refs('LOLIN_S3_Mini')[0], str(gpio))


@pytest.mark.req('PLAT-POWER-HOTPLUG-001')
def test_plat_power_hotplug_001_tvs_and_capacitor_across_vusb(sch):
    # Given VUSB (the TP4056 IN+ pads)
    # When looking at D3 and C9
    # Then D3 is the SMAJ5.0A TVS, cathode on VUSB, anode on GND
    assert sch.value('D3') == 'SMAJ5.0A'
    assert sch.net('D3', '1') == vusb(sch) and sch.net('D3', '2') == 'GND'
    # And C9 is 22 µF, + on VUSB, - on GND
    assert sch.value('C9') == '22µ' and sch.between('C9') == (vusb(sch), 'GND')


@pytest.mark.req('PLAT-POWER-REG-002')
def test_plat_power_reg_002_tps63020_ps_sync_on_gnd(sch):
    # Given the TPS63020
    reg, = sch.refs('TPS63020_3V3')
    # Then its PS/SYNC pin is tied to GND (power-save mode, never forced PWM)
    assert sch.net(reg, 'PS') == 'GND'


@pytest.mark.req('PLAT-POWER-REG-003')
def test_plat_power_reg_003_220uF_tantalum_on_3v3_at_the_s3(sch):
    # Given C1
    # Then it is the 220 µF polarised capacitor, + on +3V3, - on GND
    assert sch.parts['C1'] == 'C_Polarized' and sch.value('C1') == '220µ'
    assert sch.between('C1') == ('+3V3', 'GND')
    # And the S3 Mini's 3V pin is on that same +3V3 net
    assert sch.net(sch.refs('LOLIN_S3_Mini')[0], '3V') == '+3V3'


@pytest.mark.req('PLAT-POWER-DIST-001')
def test_plat_power_dist_001_amplifier_on_its_own_vsys_pair_with_c7(sch):
    # Given the amplifier and VSYS (switch SW1 output)
    amp, = sch.refs('MAX98357A')
    vsys = sch.net('SW1', '2')
    # Then VIN is on VSYS and GND on system GND (never B-)
    assert sch.net(amp, 'VIN') == vsys and sch.net(amp, 'GND') == 'GND'
    # And C7 470 µF sits across them, + on VIN
    assert sch.value('C7') == '470µ' and sch.between('C7') == (vsys, 'GND')
    # And the harness brings them on their own pair: X13 VSYS / GND amp -> X5 VIN / GND
    ends = {(e[4].get('ref'), e[4].get('pin'), e[5].get('ref'), e[5].get('pin')) for e in harness.EXTRA}
    assert ('X13', 'VSYS', 'X5', 'VIN') in ends and ('X13', 'GND amp', 'X5', 'GND') in ends


@pytest.mark.req('PLAT-POWER-MONITOR-001')
def test_plat_power_monitor_001_vbat_divider_on_gpio1(sch):
    # Given the TP4056 B+ pad and GPIO1 of the S3 (VBAT/2)
    bplus = sch.net(sch.refs('TP4056_DW01')[0], 'B+')
    mid = s3_pin(sch, 1)
    # Then R2 1M runs from B+ to the midpoint and R3 1M from the midpoint to GND
    assert sch.value('R2') == '1M' and set(sch.between('R2')) == {bplus, mid}
    assert sch.value('R3') == '1M' and set(sch.between('R3')) == {mid, 'GND'}
    # And C6 is a 100 nF ceramic (non-polarised symbol) from GPIO1 to GND
    assert sch.parts['C6'] == 'C' and sch.value('C6') == '0.1µ' and set(sch.between('C6')) == {mid, 'GND'}


@pytest.mark.req('PLAT-POWER-DETECT-001')
def test_plat_power_detect_001_usb_det_divider_on_gpio21(sch):
    # Given VUSB and the USB_DET net
    det = sch.net('R16', '1')
    # Then GPIO21 is on USB_DET
    assert s3_pin(sch, 21) == det == '/USB_DET'
    # And R15 68k runs from VUSB, R16 100k and C8 100 nF to GND
    assert sch.value('R15') == '68k' and set(sch.between('R15')) == {vusb(sch), det}
    assert sch.value('R16') == '100k' and set(sch.between('R16')) == {det, 'GND'}
    assert sch.value('C8') == '0.1µ' and set(sch.between('C8')) == {det, 'GND'}


@pytest.mark.req('PLAT-POWER-VSENSE-001')
@pytest.mark.xfail(strict=True, reason='hardware change not in the schematic yet (requirement text); remove this mark '
                                       'once the NPN on GPIO37 is drawn')
def test_plat_power_vsense_001_npn_from_vsys_to_gpio37(sch):
    # Given GPIO37 of the S3
    io37 = s3_pin(sch, 37)
    # Then it is the collector of an NPN whose emitter is on GND
    npn = [r for r, p in sch.nets[io37] if sch.parts.get(r, '').startswith('Q_NPN')]
    assert len(npn) == 1
    q = npn[0]
    assert sch.net(q, 'C') == io37 and sch.net(q, 'E') == 'GND'
    # And its base sits between 1M from VSYS and 1M to GND
    base = [r for r, _ in sch.nets[sch.net(q, 'B')] if r.startswith('R') and sch.value(r) == '1M']
    assert {n for r in base for n in sch.between(r)} >= {sch.net('SW1', '2'), 'GND'}


@pytest.mark.req('PLAT-POWER-GATE-001')
def test_plat_power_gate_001_q5_switches_the_sd_card_supply(sch):
    # Given Q5 (AO3401A) and the microSD reader
    sd, = sch.refs('microSD_3V3')
    # Then Q5 switches +3V3 (source) to SD_3V3 (drain, the reader's VCC)
    assert sch.value('Q5') == 'AO3401A' and sch.parts['Q5'] == 'Q_PMOS'
    assert sch.net('Q5', 'S') == '+3V3' and sch.net('Q5', 'D') == sch.net(sd, 'VCC')
    # And its gate is on SD_EN (GPIO36), pulled up to +3V3 by R22 100k
    assert sch.net('Q5', 'G') == s3_pin(sch, 36)
    assert sch.value('R22') == '100k' and set(sch.between('R22')) == {'+3V3', s3_pin(sch, 36)}
