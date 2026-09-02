"""Kennel temperature. Started as recipes/sensehat/read_temperature.py.

Diverged from the recipe: the band is the animal's safe range from
config.json, not a comfort setting, and it reports a state rather than a
colour so the caller decides what to do about it.
"""
from pihome import hw, sensors

_sense = None


def sensor(rotation=90):
    global _sense
    if _sense is None:
        _sense = hw.SenseHat()
        _sense.set_rotation(rotation)
        _sense.low_light = True
    return _sense


def read_temperature():
    """Ambient temperature in Fahrenheit, self-heating compensated."""
    return sensors.sense_hat_temperature_f(sensor())


def state(temp_f, low_f, high_f):
    """'too_cold', 'too_hot' or 'ok'. Pure function - testable off-hardware."""
    return sensors.band(temp_f, low_f, high_f,
                        below="too_cold", inside="ok", above="too_hot")
