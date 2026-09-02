#!/usr/bin/env python3
"""Switch every relay channel in turn, then switch them all off.

What it does
    A wiring smoke test. Energises each channel one at a time so you can hear
    the clicks and confirm the channel map matches the physical board, then
    drops everything to a known-safe state.

Hardware
    A multi-channel relay board on the 40-pin header.

Wiring
    BOARD numbering, because that is how these boards are usually documented.
    See docs/pinmap.md for the BOARD-to-BCM conversion.

Run on a Pi
    python3 recipes/gpio/exercise_relays.py

Run on your Mac
    Not meaningful - RPi.GPIO has no mock backend.

Copy into a project
    Keep all_off() and call it from your shutdown path. Leaving a relay
    energised because a script crashed is how a heater stays on all night.

requires: RPi.GPIO
"""
import time

import RPi.GPIO as GPIO

# --- tunables -------------------------------------------------------------
# BOARD pin numbers. These are header positions, not BCM lines.
CHANNELS = {
    "food": 32,
    "water": 36,
    "heat": 38,
    "cool": 40,
    "light": 35,
}
HOLD_SECONDS = 0.5
SETTLE_SECONDS = 3
# --------------------------------------------------------------------------


def setup(channels=CHANNELS):
    GPIO.setmode(GPIO.BOARD)
    for pin in channels.values():
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)


def all_off(channels=CHANNELS):
    """Drop every channel. Safe to call at any time, including twice."""
    for pin in channels.values():
        GPIO.output(pin, GPIO.LOW)


def exercise(channels=CHANNELS, hold=HOLD_SECONDS):
    """Energise each channel in turn, announcing it, then release."""
    for name, pin in channels.items():
        print("  {} (BOARD {}) on".format(name, pin))
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(hold)
    time.sleep(SETTLE_SECONDS)
    all_off(channels)
    print("  all off")


if __name__ == "__main__":
    setup()
    try:
        exercise()
    except KeyboardInterrupt:
        pass
    finally:
        all_off()
        GPIO.cleanup()
