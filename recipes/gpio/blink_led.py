#!/usr/bin/env python3
"""Blink an LED or relay on a GPIO pin.

What it does
    Turns one output on and off forever, until you press Ctrl-C.

Hardware
    An LED (with a series resistor) or a relay board channel on a BCM pin.

Wiring
    BCM 26 -> LED anode -> 330R resistor -> ground.

Run on a Pi
    python3 recipes/gpio/blink_led.py

Run on your Mac
    tools/dev python3 recipes/gpio/blink_led.py

Copy into a project
    Keep blink(); drop the __main__ block. If the thing you are blinking is a
    status indicator, drive it from your main loop rather than blocking here.

requires: gpiozero
"""
from signal import pause

from gpiozero import LED

# --- tunables -------------------------------------------------------------
PIN = 26                # BCM numbering
ON_SECONDS = 0.5
OFF_SECONDS = 0.5
# --------------------------------------------------------------------------


def blink(pin=PIN, on_seconds=ON_SECONDS, off_seconds=OFF_SECONDS):
    """Start blinking. Returns the LED so the caller can stop it."""
    led = LED(pin)
    led.blink(on_time=on_seconds, off_time=off_seconds)
    return led


if __name__ == "__main__":
    led = blink()
    print("blinking BCM {} (Ctrl-C to stop)".format(PIN))
    try:
        pause()
    except KeyboardInterrupt:
        pass
    finally:
        led.off()          # never leave an output energised
