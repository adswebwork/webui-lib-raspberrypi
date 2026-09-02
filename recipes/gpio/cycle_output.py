#!/usr/bin/env python3
"""Cycle an output on and off a fixed number of times.

What it does
    Switches a light, fan or relay on for a while, then off, repeating a set
    number of times. Useful as a wiring test before you trust a circuit.

Hardware
    A relay channel or LED on a BCM pin.

Wiring
    BCM 26 -> relay IN.

Run on a Pi
    python3 recipes/gpio/cycle_output.py

Run on your Mac
    tools/dev python3 recipes/gpio/cycle_output.py

Copy into a project
    Keep cycle(). Raise CYCLES or set it to None for an endless loop.

requires: gpiozero
"""
import time

from gpiozero import OutputDevice

# --- tunables -------------------------------------------------------------
PIN = 26                 # BCM numbering
ON_SECONDS = 10
OFF_SECONDS = 10
CYCLES = 3               # None to run until interrupted
# --------------------------------------------------------------------------


def cycle(device, cycles=CYCLES, on_seconds=ON_SECONDS, off_seconds=OFF_SECONDS):
    """Run the on/off cycle. Yields the completed count after each pass."""
    completed = 0
    while cycles is None or completed < cycles:
        device.on()
        time.sleep(on_seconds)
        device.off()
        time.sleep(off_seconds)
        completed += 1
        yield completed


if __name__ == "__main__":
    output = OutputDevice(PIN, initial_value=False)
    try:
        for count in cycle(output):
            print("cycle {} complete".format(count))
    except KeyboardInterrupt:
        pass
    finally:
        output.off()
