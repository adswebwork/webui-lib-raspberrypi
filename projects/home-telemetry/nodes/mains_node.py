#!/usr/bin/env python3
"""Mains node: four relay channels and a motion sensor.

Runs on the Pi wired to the relay board. Formerly _globalConfig/sys2.py.

Pins here are BOARD (physical header positions), because that is how the relay
board is wired and documented. See docs/pinmap.md.

    python3 nodes/mains_node.py
"""
import os
import time

import RPi.GPIO as GPIO

from pihome import config, identity, iot, log
from pihome.reading import Reading

CONFIG = config.load(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  os.pardir, "config.json"))
SETTINGS = CONFIG["nodes"]["mains_node"]

logger = log.get_logger("mains_node")

# BOARD numbering - physical header positions, not BCM lines.
MOTION = 32
RELAYS = {"relay1": 31, "relay2": 33, "relay3": 35, "relay4": 37}
LEDS = {"led1": 40, "led2": 38}
# NOTE: a third LED was wired to 35, which relay3 already claims. Confirm
# against the board before driving it - see docs/pinmap.md.

_client = None


def setup():
    GPIO.setmode(GPIO.BOARD)
    for pin in list(RELAYS.values()) + list(LEDS.values()):
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)
    GPIO.setup(MOTION, GPIO.IN)


def all_off():
    """Drop every channel. Safe to call twice."""
    for pin in list(RELAYS.values()) + list(LEDS.values()):
        GPIO.output(pin, GPIO.LOW)


def main():
    global _client
    identity.assume(SETTINGS["device"])
    setup()
    _client = iot.connect()
    iot.publish_event(_client, "online", "mains node up")

    last_motion = False
    try:
        while True:
            motion = GPIO.input(MOTION) == GPIO.HIGH
            if motion != last_motion:
                logger.info("motion %s", "detected" if motion else "cleared")
                iot.publish(_client, Reading("motion", motion, "bool"))
                last_motion = motion
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        all_off()
        GPIO.cleanup()
        iot.publish_event(_client, "offline", "mains node down")
        _client.disconnect()


if __name__ == "__main__":
    main()
