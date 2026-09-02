#!/usr/bin/env python3
"""Show temperature, pressure and humidity as three bars.

What it does
    Draws three vertical bars on the LED matrix - red for temperature, green
    for pressure, blue for humidity - each scaled to a sensible range. The
    only view in this repo that shows all three environmental sensors at once.

Hardware
    Raspberry Pi with a Sense HAT.

Wiring
    None.

Run on a Pi
    python3 recipes/sensehat/bar_graph.py

Run on your Mac
    tools/dev python3 recipes/sensehat/bar_graph.py

Copy into a project
    The scaling and drawing live in pihome.display (pure Python, no numpy).
    Adjust the *_RANGE constants to your climate or the bars will sit pegged
    at the top or bottom and tell you nothing.

requires: sense-hat  (dev: sense-emu)
"""
import time

from sense_hat import SenseHat

from pihome.display import BLUE, GREEN, RED, reading_bars

# --- tunables -------------------------------------------------------------
ROTATION = 0
INTERVAL_SECONDS = 1
TEMPERATURE_RANGE = (0, 40)      # degrees C
PRESSURE_RANGE = (950, 1050)     # hPa
HUMIDITY_RANGE = (0, 100)        # %
# --------------------------------------------------------------------------

sense = SenseHat()
sense.set_rotation(ROTATION)
sense.low_light = True


if __name__ == "__main__":
    try:
        while True:
            sense.set_pixels(reading_bars([
                (sense.temperature, TEMPERATURE_RANGE[0], TEMPERATURE_RANGE[1], RED),
                (sense.pressure, PRESSURE_RANGE[0], PRESSURE_RANGE[1], GREEN),
                (sense.humidity, HUMIDITY_RANGE[0], HUMIDITY_RANGE[1], BLUE),
            ]))
            time.sleep(INTERVAL_SECONDS)
    except KeyboardInterrupt:
        pass
    finally:
        sense.clear()
