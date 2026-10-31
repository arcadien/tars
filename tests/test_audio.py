"""AUDIO acceptance criteria checked on the schematic (requirements/technical.md)."""
import pytest


@pytest.mark.req('TECH-AUDIO-SHUTDOWN-001')
def test_tech_audio_shutdown_001_amp_sd_from_gpio4_through_r10_pulled_down_by_r18(sch):
    # Given the amplifier and GPIO4 of the S3
    amp, = sch.refs('MAX98357A')
    io4 = sch.net(sch.refs('LOLIN_S3_Mini')[0], '4')
    sd = sch.net(amp, 'SD')
    # Then R10 runs from GPIO4 to the amplifier SD
    assert set(sch.between('R10')) == {io4, sd}
    # And R18 pulls SD to GND (shut down from reset, before the firmware drives GPIO4)
    assert set(sch.between('R18')) == {sd, 'GND'}
