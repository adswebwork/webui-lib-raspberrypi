#!/usr/bin/env python3
"""Alternate two lights, at a changing pace.

What it does
    Flips between two outputs - a traffic light, a warning beacon, or an
    attract sequence. Speeds up through several phases.

Hardware
    Two LEDs or relay channels on BCM pins.

Wiring
    BCM 20 -> red LED, BCM 21 -> green LED, both via a resistor to ground.

Run on a Pi
    python3 recipes/gpio/alternate_lights.py

Run on your Mac
    tools/dev python3 recipes/gpio/alternate_lights.py

Copy into a project
    Keep alternate(). Each PHASES entry is (repeats, seconds_per_side).

requires: gpiozero
"""
import time

from gpiozero import LED

# --- tunables -------------------------------------------------------------
PIN_A = 20               # BCM
PIN_B = 21               # BCM
PHASES = [(5, 1.0), (10, 0.5), (20, 0.2)]   # (repeats, seconds each side)
# --------------------------------------------------------------------------


def alternate(a, b, repeats, interval):
    """Flip between two outputs `repeats` times."""
    for _ in range(repeats):
        a.on()
        b.off()
        time.sleep(interval)
        a.off()
        b.on()
        time.sleep(interval)


if __name__ == "__main__":
    a, b = LED(PIN_A), LED(PIN_B)
    try:
        for repeats, interval in PHASES:
            print("{} repeats at {}s".format(repeats, interval))
            alternate(a, b, repeats, interval)
    except KeyboardInterrupt:
        pass
    finally:
        a.off()
        b.off()
