#!/usr/bin/env python3
"""Read a light level with no ADC, by timing a capacitor charge.

What it does
    Reports how bright it is, using the standard resistor-capacitor trick: a
    photoresistor charges a capacitor, and the time taken to cross the Pi's
    logic threshold varies with light. Fewer counts means brighter.

    The tight counting loop IS the measurement - it is not a busy-wait bug.
    Replacing it with sleep() breaks the reading.

Hardware
    A photoresistor (LDR) and a 1uF capacitor. No ADC needed.

Wiring
    3V3 -> LDR -> BCM 4 -> capacitor -> ground.

Run on a Pi
    python3 recipes/gpio/read_light_sensor.py

Run on your Mac
    Not meaningful - this measures real electrical timing. Mock pins will
    return instantly. Run it on a Pi.

Copy into a project
    Keep read_light(). Calibrate THRESHOLD by printing raw counts in your own
    room, in the dark and with the lights on - the numbers are specific to
    your capacitor and your LDR.

requires: RPi.GPIO
"""
import time

import RPi.GPIO as GPIO

# --- tunables -------------------------------------------------------------
PIN = 4                  # BCM numbering
DISCHARGE_SECONDS = 0.1
THRESHOLD = 2            # counts above this = dark. Calibrate for your parts.
# --------------------------------------------------------------------------


def read_light(pin=PIN):
    """Counts taken for the capacitor to charge. Higher means darker."""
    # Drain the capacitor first, so every reading starts from the same place.
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)
    time.sleep(DISCHARGE_SECONDS)

    # Now count how long it takes to charge back up through the LDR.
    GPIO.setup(pin, GPIO.IN)
    count = 0
    while GPIO.input(pin) == GPIO.LOW:
        count += 1
    return count


def is_dark(pin=PIN, threshold=THRESHOLD):
    return read_light(pin) > threshold


if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)
    try:
        while True:
            count = read_light()
            print("{:6d}  {}".format(count, "dark" if count > THRESHOLD else "light"))
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()
