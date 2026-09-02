#!/usr/bin/env python3
"""Flash a light and sound a buzzer together.

What it does
    A combined visual and audible alert, repeated a set number of times. The
    thing you call when a sensor trips and somebody needs to notice.

Hardware
    An LED or relay channel, and an active buzzer.

Wiring
    BCM 26 -> light/relay IN. BCM 19 -> buzzer +.

Run on a Pi
    python3 recipes/gpio/alarm_sequence.py

Run on your Mac
    tools/dev python3 recipes/gpio/alarm_sequence.py

Copy into a project
    Keep alarm(). Call it from a sensor callback, and publish an Event
    alongside it so the alert shows up off-device too.

requires: gpiozero
"""
import time

from gpiozero import LED, Buzzer

# --- tunables -------------------------------------------------------------
LIGHT_PIN = 26           # BCM
BUZZER_PIN = 19          # BCM
REPEATS = 3
ON_SECONDS = 0.4
OFF_SECONDS = 0.6
# --------------------------------------------------------------------------


def alarm(light, buzzer, repeats=REPEATS, on=ON_SECONDS, off=OFF_SECONDS):
    """Flash and sound together, `repeats` times."""
    try:
        for _ in range(repeats):
            light.on()
            buzzer.on()
            time.sleep(on)
            light.off()
            buzzer.off()
            time.sleep(off)
    finally:
        # An alarm interrupted partway must never leave the buzzer sounding.
        light.off()
        buzzer.off()


if __name__ == "__main__":
    light, buzzer = LED(LIGHT_PIN), Buzzer(BUZZER_PIN)
    try:
        alarm(light, buzzer)
        print("alarm complete")
    except KeyboardInterrupt:
        pass
    finally:
        light.off()
        buzzer.off()
