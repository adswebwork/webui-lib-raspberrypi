#!/usr/bin/env python3
"""Sweep a rainbow across the LED matrix.

What it does
    Cycles hue across all 64 pixels. Pure eye candy, and a quick way to prove
    a Sense HAT's display works.

Hardware
    Raspberry Pi with a Sense HAT.

Wiring
    None.

Run on a Pi
    python3 recipes/sensehat/rainbow.py

Run on your Mac
    tools/dev python3 recipes/sensehat/rainbow.py

Copy into a project
    Useful as a boot animation. Keep low_light on - at full brightness the
    matrix draws real current and washes out anything near it.

requires: sense-hat  (dev: sense-emu)
"""
import time

from sense_hat import SenseHat

from pihome.display import rainbow_frame

# --- tunables -------------------------------------------------------------
ROTATION = 0
FRAME_SECONDS = 0.05
STEP = 0.01              # hue advanced per frame
# --------------------------------------------------------------------------

sense = SenseHat()
sense.set_rotation(ROTATION)
sense.low_light = True


if __name__ == "__main__":
    offset = 0.0
    try:
        while True:
            sense.set_pixels(rainbow_frame(offset))
            offset = (offset + STEP) % 1.0
            time.sleep(FRAME_SECONDS)
    except KeyboardInterrupt:
        pass
    finally:
        sense.clear()
