#!/usr/bin/env python3
"""Say goodbye and blank the LED matrix.

What it does
    Scrolls a short message, then clears the display. Run it when a crashed
    script has left the matrix lit.

Hardware
    Raspberry Pi with a Sense HAT.

Wiring
    None.

Run on a Pi
    python3 recipes/sensehat/clear_display.py

Run on your Mac
    tools/dev python3 recipes/sensehat/clear_display.py

Copy into a project
    Wire this into your service's ExecStop so a restart never inherits a lit
    display.

requires: sense-hat  (dev: sense-emu)
"""
from sense_hat import SenseHat

# --- tunables -------------------------------------------------------------
MESSAGE = "Bye"
ROTATION = 270
SCROLL_SPEED = 0.05
COLOUR = (255, 104, 0)
# --------------------------------------------------------------------------


if __name__ == "__main__":
    sense = SenseHat()
    sense.set_rotation(ROTATION)
    try:
        sense.show_message(MESSAGE, SCROLL_SPEED, text_colour=COLOUR)
    finally:
        sense.clear()
