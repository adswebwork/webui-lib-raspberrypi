#!/usr/bin/env python3
"""Scroll a message across the LED matrix.

What it does
    Displays scrolling text, then clears the display.

Hardware
    Raspberry Pi with a Sense HAT.

Wiring
    None.

Run on a Pi
    python3 recipes/sensehat/show_message.py

Run on your Mac
    tools/dev python3 recipes/sensehat/show_message.py

Copy into a project
    Keep show(). Always clear() in a finally - a message interrupted partway
    leaves the matrix lit, which on a battery node matters.

requires: sense-hat  (dev: sense-emu)
"""
from sense_hat import SenseHat

# --- tunables -------------------------------------------------------------
MESSAGE = "Hello"
ROTATION = 90
SCROLL_SPEED = 0.08      # seconds per column; lower is faster
COLOUR = (255, 255, 255)
LOW_LIGHT = True
# --------------------------------------------------------------------------

sense = SenseHat()
sense.set_rotation(ROTATION)
sense.low_light = LOW_LIGHT


def show(text, colour=COLOUR, speed=SCROLL_SPEED):
    sense.show_message(str(text), scroll_speed=speed, text_colour=colour)


if __name__ == "__main__":
    try:
        show(MESSAGE)
    except KeyboardInterrupt:
        pass
    finally:
        sense.clear()
