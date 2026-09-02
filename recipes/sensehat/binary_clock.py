#!/usr/bin/env python3
"""Show the time as four digits on the 8x8 LED matrix.

What it does
    Draws HH on the top half and MM on the bottom, using a 4x4 numeral font.
    Hours in red, minutes in cyan.

Hardware
    Raspberry Pi with a Sense HAT.

Wiring
    None.

Run on a Pi
    python3 recipes/sensehat/binary_clock.py

Run on your Mac
    tools/dev python3 recipes/sensehat/binary_clock.py

Copy into a project
    The font and renderer live in pihome.display, so the digits stay correct
    everywhere. At 4x4 the numeral 8 is necessarily a solid block - that is
    the font's design, not a bug.

requires: sense-hat  (dev: sense-emu)
"""
import time

from sense_hat import SenseHat

from pihome.display import clock_pixels

# --- tunables -------------------------------------------------------------
ROTATION = 180
REFRESH_SECONDS = 10
HOUR_COLOUR = (255, 0, 0)
MINUTE_COLOUR = (0, 255, 255)
# --------------------------------------------------------------------------

sense = SenseHat()
sense.set_rotation(ROTATION)
sense.low_light = True


if __name__ == "__main__":
    try:
        while True:
            now = time.localtime()
            sense.set_pixels(clock_pixels(now.tm_hour, now.tm_min,
                                          HOUR_COLOUR, MINUTE_COLOUR))
            print("{:02d}:{:02d}".format(now.tm_hour, now.tm_min))
            time.sleep(REFRESH_SECONDS)
    except KeyboardInterrupt:
        pass
    finally:
        sense.clear()
