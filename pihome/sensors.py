"""Turning what a sensor reports into the number we publish.

Calibration belongs here, not in each project. The Sense HAT's self-heating
offset is a property of the board and its mounting - the same 20 degrees
whether the Pi is watching a house, a kennel or a dog house - so three
projects holding three copies of it meant recalibrating in three places and
finding out later that only two of them were done.

The recipe keeps its own copy on purpose: recipes/sensehat/read_temperature.py
is standalone Pi code meant to be copied out of this repo, so it carries the
constant inline with the note explaining it. Projects import from here.
"""
# The Sense HAT's temperature sensor sits directly above the Pi's CPU and reads
# high. Calibrated by eye against a room thermometer. Re-check it if the case,
# the mounting or the Pi model changes - and change it here, once.
SENSE_HAT_SELF_HEATING_OFFSET_F = 20


def celsius_to_fahrenheit(celsius):
    return celsius * 1.8 + 32


def sense_hat_temperature_f(sense, offset_f=SENSE_HAT_SELF_HEATING_OFFSET_F):
    """Ambient temperature in Fahrenheit, self-heating compensated.

    Rounded to a whole degree. The sensor sits above a CPU and is corrected by
    a hand-calibrated offset, so a decimal place would be claiming precision
    that is not there.
    """
    return round(celsius_to_fahrenheit(sense.get_temperature()) - offset_f)


def band(value, low, high, below="below", inside="ok", above="above"):
    """Which side of a range a reading falls on.

    Pure function, no hardware: the three projects each had their own copy of
    this comparison with different labels, which is the only thing that
    actually differed between them.
    """
    if value >= high:
        return above
    if value <= low:
        return below
    return inside
