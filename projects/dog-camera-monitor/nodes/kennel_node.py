#!/usr/bin/env python3
"""Kennel node: report the temperature where the dog actually is.

Runs on the Pi 3 with the Sense HAT, inside the kennel.

    PYTHONPATH=/home/pi/raspberrypi python3 nodes/kennel_node.py
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pihome import config, identity, iot, log       # noqa: E402
from pihome.display import BLUE, RED, WHITE, shape  # noqa: E402
from pihome.reading import Reading                  # noqa: E402

from lib import climate                             # noqa: E402

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = config.load(os.path.join(HERE, "config.json"))
SETTINGS = CONFIG["nodes"]["kennel_node"]
THRESHOLDS = CONFIG["thresholds"]
MESSAGES = CONFIG["messages"]

logger = log.get_logger("kennel_node")

_STATE_COLOUR = {"too_hot": RED, "too_cold": BLUE, "ok": WHITE}


def main():
    identity.assume(SETTINGS["device"])
    sense = climate.sensor(SETTINGS["rotation"])
    client = iot.connect()
    iot.publish_event(client, "online", "kennel node up")

    last_state = None
    try:
        while True:
            temperature = climate.read_temperature()
            state = climate.state(temperature,
                                  THRESHOLDS["temp_low_f"],
                                  THRESHOLDS["temp_high_f"])

            iot.publish(client, Reading("temperature", temperature, "F",
                                        tags={"location": "kennel"}))
            sense.set_pixels(shape("heart", _STATE_COLOUR[state]))
            logger.info("%s F (%s)", temperature, state)

            # Only announce a change, so an alert means something happened.
            if state != last_state and state != "ok":
                iot.publish_event(client, "alarm", MESSAGES[state], level="warn")
                last_state = state
            elif state == "ok":
                last_state = state

            time.sleep(SETTINGS["publish_interval_s"])
    except KeyboardInterrupt:
        pass
    finally:
        sense.clear()
        iot.publish_event(client, "offline", "kennel node down")
        client.disconnect()


if __name__ == "__main__":
    main()
