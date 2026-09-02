"""Sense HAT display for the dog house.

Was smarthouse/automation/senseHatRoutines.py. The bar rendering moved to
pihome.display, which is pure Python and testable off-hardware.
"""
from pihome import hw, sensors
from pihome.display import BLUE, RED, WHITE, reading_bars, shape

_sense = None


def sensor():
    global _sense
    if _sense is None:
        _sense = hw.SenseHat()
        _sense.low_light = True
    return _sense


def read_temperature():
    """Ambient temperature in Fahrenheit, self-heating compensated."""
    return sensors.sense_hat_temperature_f(sensor())


def state(temp_f, low_f, high_f):
    """'cold', 'hot' or 'ok'. Pure function - testable off-hardware."""
    return sensors.band(temp_f, low_f, high_f,
                        below="cold", inside="ok", above="hot")


def show_state(temp_f, low_f, high_f):
    """Paint a heart coloured for the current state."""
    colour = {"hot": RED, "cold": BLUE, "ok": WHITE}[state(temp_f, low_f, high_f)]
    sensor().set_pixels(shape("heart", colour))


def show_climate():
    """Temperature, pressure and humidity as three bars."""
    sense = sensor()
    sense.set_pixels(reading_bars([
        (sense.temperature, 0, 40, RED),
        (sense.pressure, 950, 1050, (0, 255, 0)),
        (sense.humidity, 0, 100, BLUE),
    ]))
