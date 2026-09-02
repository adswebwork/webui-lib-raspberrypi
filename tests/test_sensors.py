"""Sensor calibration and banding.

These were three copies in three projects. Now that there is one, it is worth
testing - the offset is the difference between a fan that runs and one that
does not.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pihome import sensors


class FakeSense:
    """Just the one method sense_hat_temperature_f uses."""

    def __init__(self, celsius):
        self._celsius = celsius

    def get_temperature(self):
        return self._celsius


def test_conversion_is_the_textbook_one():
    assert sensors.celsius_to_fahrenheit(0) == 32
    assert sensors.celsius_to_fahrenheit(100) == 212


def test_self_heating_offset_is_subtracted():
    """37.8C is 100F; the HAT reads high, so we publish 100 - 20."""
    assert sensors.sense_hat_temperature_f(FakeSense(37.7778)) == 80


def test_offset_is_overridable_without_editing_the_module():
    """Recalibrating one Pi must not mean forking the shared constant."""
    assert sensors.sense_hat_temperature_f(FakeSense(37.7778), offset_f=0) == 100


def test_result_is_a_whole_number():
    """A hand-calibrated offset on a sensor sitting above a CPU does not
    support a decimal place."""
    value = sensors.sense_hat_temperature_f(FakeSense(21.6667))
    assert isinstance(value, int)


@pytest.mark.parametrize("value, expected", [
    (40, "below"),      # at the low edge - inclusive
    (39, "below"),
    (60, "ok"),
    (80, "above"),      # at the high edge - inclusive
    (81, "above"),
])
def test_band_edges(value, expected):
    assert sensors.band(value, 40, 80) == expected


def test_band_labels_are_the_only_thing_projects_differed_on():
    assert sensors.band(90, 45, 85, below="too_cold", inside="ok",
                        above="too_hot") == "too_hot"
    assert sensors.band(90, 45, 75, below="cold", inside="ok",
                        above="hot") == "hot"
