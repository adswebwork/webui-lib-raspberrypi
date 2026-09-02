#!/usr/bin/env python3
"""Force every controlled pin to a safe state.

What it does
    Sets a list of outputs low and releases them. Run it when a script has
    crashed and left something energised, or as the last step of a service.

Hardware
    Whatever your project drives.

Wiring
    Edit CHANNELS to match your board.

Run on a Pi
    python3 recipes/gpio/safe_shutdown.py

Run on your Mac
    Not meaningful - RPi.GPIO has no mock backend.

Copy into a project
    Import this rather than duplicating it, and wire it to your service's
    ExecStop so a restart always begins from a known state.

requires: RPi.GPIO
"""
import RPi.GPIO as GPIO

# --- tunables -------------------------------------------------------------
CHANNELS = [32, 36, 38, 40, 35, 37]      # BOARD numbering
# --------------------------------------------------------------------------


def shutdown(channels=CHANNELS):
    """Drive every listed pin low, then release the GPIO subsystem."""
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)          # these pins may already be configured
    for pin in channels:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)
    GPIO.cleanup()


if __name__ == "__main__":
    shutdown()
    print("all channels low, GPIO released")
