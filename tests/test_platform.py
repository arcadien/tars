"""PLAT acceptance criteria checked on the schematic (requirements/platform.md)."""
import pytest


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
