#!/usr/bin/env python3
"""Draw a shape on the LED matrix.

What it does
    Displays one of the built-in 8x8 bitmaps - heart, plus, equals, or the
    Raspberry Pi and Trinket logos.

Hardware
    Raspberry Pi with a Sense HAT.

Wiring
    None.

Run on a Pi
    python3 recipes/sensehat/show_shape.py

Run on your Mac
    tools/dev python3 recipes/sensehat/show_shape.py

Copy into a project
    Shapes live in pihome.display. shape() takes a colour, so one bitmap can
    signal several states - a red heart for too hot, blue for too cold.

requires: sense-hat  (dev: sense-emu)
"""
import time

from sense_hat import SenseHat

from pihome.display import BLUE, SHAPES, shape

# --- tunables -------------------------------------------------------------
SHAPE = "heart"
COLOUR = BLUE
ROTATION = 90
HOLD_SECONDS = 3
# --------------------------------------------------------------------------

sense = SenseHat()
sense.set_rotation(ROTATION)
sense.low_light = True


if __name__ == "__main__":
    print("available shapes:", ", ".join(SHAPES))
    try:
        sense.set_pixels(shape(SHAPE, COLOUR))
        time.sleep(HOLD_SECONDS)
    except KeyboardInterrupt:
        pass
    finally:
        sense.clear()
