#!/usr/bin/env python3
"""Run a light along a row of LEDs, in either direction.

What it does
    Lights a chain of outputs one after another - a stairwell that lights from
    the top when you open the door, and from the bottom when you walk up.

Hardware
    Any number of LEDs or relay channels on BCM pins.

Wiring
    BCM 4, 17, 18, 27 -> one LED (+ resistor) each, in physical order.

Run on a Pi
    python3 recipes/gpio/led_chase.py

Run on your Mac
    tools/dev python3 recipes/gpio/led_chase.py

Copy into a project
    Keep chase(). Note the lights stay lit when it returns - call all_off()
    when you want them out. The archived original called GPIO.cleanup() at the
    end of every chase, which reset the pins and dropped the lights it had
    just turned on.

requires: gpiozero
"""
import time

from gpiozero import LED

# --- tunables -------------------------------------------------------------
PINS = [4, 17, 18, 27]   # BCM, in the order they are physically arranged
STEP_SECONDS = 0.3
# --------------------------------------------------------------------------


def chase(leds, ascending=True, lit=True, step=STEP_SECONDS):
    """Walk along `leds`, switching each one.

    ascending  - first pin to last, or last to first
    lit        - True lights them one by one, False extinguishes them
    """
    order = leds if ascending else list(reversed(leds))
    for led in order:
        led.on() if lit else led.off()
        time.sleep(step)


def all_off(leds):
    for led in leds:
        led.off()


if __name__ == "__main__":
    leds = [LED(pin) for pin in PINS]
    try:
        print("up, lighting")
        chase(leds, ascending=True, lit=True)
        time.sleep(1)
        print("up, extinguishing")
        chase(leds, ascending=True, lit=False)
        print("down, lighting")
        chase(leds, ascending=False, lit=True)
        time.sleep(1)
        print("down, extinguishing")
        chase(leds, ascending=False, lit=False)
    except KeyboardInterrupt:
        pass
    finally:
        all_off(leds)
