#!/usr/bin/env python3
"""React to the Sense HAT joystick.

What it does
    Shows a letter for whichever way the little joystick is pushed - U, D, L,
    R, or M for the middle press.

Hardware
    Raspberry Pi with a Sense HAT.

Wiring
    None.

Run on a Pi
    python3 recipes/sensehat/read_joystick.py

Run on your Mac
    tools/dev python3 recipes/sensehat/read_joystick.py
    (the emulator GUI has a joystick)

Copy into a project
    Keep the events loop. Filter on event.action == "pressed" or you will act
    on both press and release for every nudge.

requires: sense-hat  (dev: sense-emu)
"""
from sense_hat import SenseHat

# --- tunables -------------------------------------------------------------
ROTATION = 90
COLOUR = (255, 255, 255)
LETTERS = {"up": "U", "down": "D", "left": "L", "right": "R", "middle": "M"}
# --------------------------------------------------------------------------

sense = SenseHat()
sense.set_rotation(ROTATION)
sense.low_light = True


if __name__ == "__main__":
    print("push the joystick (Ctrl-C to stop)")
    try:
        while True:
            for event in sense.stick.get_events():
                # Every nudge produces both a press and a release.
                if event.action != "pressed":
                    continue
                letter = LETTERS.get(event.direction, "?")
                print("{} -> {}".format(event.direction, letter))
                sense.show_letter(letter, text_colour=COLOUR)
    except KeyboardInterrupt:
        pass
    finally:
        sense.clear()
