#!/usr/bin/env python3
"""React to a PIR motion sensor.

What it does
    Prints a line whenever motion starts and stops. Event-driven, so it costs
    no CPU while nothing is happening.

Hardware
    A PIR module (HC-SR501 or similar) on a BCM pin.

Wiring
    PIR VCC -> 5V, GND -> ground, OUT -> BCM 4.

Run on a Pi
    python3 recipes/gpio/read_pir.py

Run on your Mac
    tools/dev python3 recipes/gpio/read_pir.py
    (mock pins; drive it with Device.pin_factory.pin(4).drive_high())

Copy into a project
    Keep watch() and pass your own callbacks. Give the sensor 30-60s to settle
    after power-up or you will get spurious triggers.

requires: gpiozero
"""
from signal import pause

from gpiozero import MotionSensor

# --- tunables -------------------------------------------------------------
PIN = 4                  # BCM numbering
QUEUE_LEN = 1            # samples averaged; raise to debounce a twitchy sensor
# --------------------------------------------------------------------------


def watch(on_motion=None, on_still=None, pin=PIN):
    """Attach callbacks to a PIR. Returns the sensor - keep a reference to it."""
    sensor = MotionSensor(pin, queue_len=QUEUE_LEN)
    if on_motion:
        sensor.when_motion = on_motion
    if on_still:
        sensor.when_no_motion = on_still
    return sensor


if __name__ == "__main__":
    sensor = watch(
        on_motion=lambda: print("motion"),
        on_still=lambda: print("still"),
    )
    print("watching BCM {} (Ctrl-C to stop)".format(PIN))
    try:
        pause()
    except KeyboardInterrupt:
        pass
