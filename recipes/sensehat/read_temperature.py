#!/usr/bin/env python3
"""Read the ambient temperature from a Sense HAT, compensated for self-heating.

What it does
    Prints a Fahrenheit reading every few seconds and floods the LED matrix
    blue, white or red depending on whether it is below, inside, or above the
    comfortable band.

Hardware
    Raspberry Pi with a Sense HAT on the GPIO header.

Wiring
    None. The Sense HAT uses the whole 40-pin header.

Run on a Pi
    python3 recipes/sensehat/read_temperature.py

Run on your Mac
    tools/dev python3 recipes/sensehat/read_temperature.py
    (uses sense_emu - run `sense_emu_gui` and move the sliders)

Copy into a project
    Keep read_temperature() and band_colour(); drop the __main__ block.
    Publish with pihome.iot.publish(client, Reading("temperature", t, "F")) -
    do not hand-roll the JSON payload.

requires: sense-hat  (dev: sense-emu)
"""
import time

from sense_hat import SenseHat

# --- tunables -------------------------------------------------------------
INTERVAL_SECONDS = 3
IDEAL_F = 80
THRESHOLD_F = 3
ROTATION = 90

# The Sense HAT's sensor sits directly above the Pi's CPU and reads high. This
# is the plain C-to-F conversion with a self-heating offset subtracted,
# calibrated by eye against a room thermometer. Re-check it if you change the
# case, the mounting, or the Pi model.
SELF_HEATING_OFFSET_F = 20

BLUE, WHITE, RED = (0, 0, 255), (255, 255, 255), (255, 0, 0)
# --------------------------------------------------------------------------

sense = SenseHat()
sense.set_rotation(ROTATION)
sense.low_light = True


def read_temperature():
    """Ambient temperature in degrees Fahrenheit, self-heating compensated."""
    return round(sense.get_temperature() * 1.8 + 32 - SELF_HEATING_OFFSET_F)


def band_colour(temp_f, ideal=IDEAL_F, threshold=THRESHOLD_F):
    """Blue below the comfortable band, red above it, white inside.

    A pure function of a number, so it can be tested without hardware.
    """
    if temp_f >= ideal + threshold:
        return RED
    if temp_f <= ideal - threshold:
        return BLUE
    return WHITE


if __name__ == "__main__":
    try:
        while True:
            temp_f = read_temperature()
            print("{} F".format(temp_f))
            sense.clear(band_colour(temp_f))
            time.sleep(INTERVAL_SECONDS)
    except KeyboardInterrupt:
        pass
    finally:
        sense.clear()
