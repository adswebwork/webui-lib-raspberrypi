#!/usr/bin/env python3
"""Switch an output when a sensor trips.

What it does
    Reads a light sensor and turns an output on when it goes dark - the
    smallest complete sense-and-act loop. Swap the sensor for a PIR and you
    have a motion-activated light.

Hardware
    A photoresistor + capacitor on one pin, a relay or buzzer on another.

Wiring
    3V3 -> LDR -> BCM 4 -> capacitor -> ground.
    BCM 26 -> relay IN.

Run on a Pi
    python3 recipes/gpio/sensor_triggers_output.py

Run on your Mac
    Not meaningful - see read_light_sensor.py.

Copy into a project
    Keep the loop shape and replace read_light() with whatever you are
    sensing. Publish the state change rather than only printing it:
    pihome.iot.publish(client, Reading("motion", True, "bool")).

requires: RPi.GPIO
"""
import time

import RPi.GPIO as GPIO

# --- tunables -------------------------------------------------------------
SENSOR_PIN = 4           # BCM
OUTPUT_PIN = 26          # BCM - a relay, buzzer, light or fan
THRESHOLD = 2            # counts above this = dark. Calibrate for your parts.
DISCHARGE_SECONDS = 0.1
INTERVAL_SECONDS = 2
# --------------------------------------------------------------------------


def read_light(pin=SENSOR_PIN):
    """Counts taken for the capacitor to charge. Higher means darker."""
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)
    time.sleep(DISCHARGE_SECONDS)
    GPIO.setup(pin, GPIO.IN)
    count = 0
    while GPIO.input(pin) == GPIO.LOW:
        count += 1
    return count


if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(OUTPUT_PIN, GPIO.OUT)
    GPIO.output(OUTPUT_PIN, GPIO.LOW)
    try:
        while True:
            level = read_light()
            dark = level > THRESHOLD
            GPIO.output(OUTPUT_PIN, GPIO.HIGH if dark else GPIO.LOW)
            print("{:6d}  output {}".format(level, "on" if dark else "off"))
            time.sleep(INTERVAL_SECONDS)
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()
