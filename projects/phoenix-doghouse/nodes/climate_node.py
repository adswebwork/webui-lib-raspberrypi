#!/usr/bin/env python3
"""Climate node: watch the kennel temperature and drive heat or cool.

Was smarthouse/automation/system1_register.py.

    PYTHONPATH=/home/pi/raspberrypi python3 nodes/climate_node.py
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pihome import config, identity, iot, log  # noqa: E402
from pihome.reading import Reading             # noqa: E402

from lib import display                        # noqa: E402

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = config.load(os.path.join(HERE, "config.json"))
SETTINGS = CONFIG["nodes"]["climate_node"]
THRESHOLDS = CONFIG["thresholds"]
MESSAGES = CONFIG["messages"]

logger = log.get_logger("climate_node")


def main():
    identity.assume(SETTINGS["device"])
    client = iot.connect()
    iot.publish_event(client, "online", "climate node up")

    last_state = None
    try:
        while True:
            temperature = display.read_temperature()
            state = display.state(temperature, THRESHOLDS["temp_low_f"],
                                  THRESHOLDS["temp_high_f"])
            display.show_state(temperature, THRESHOLDS["temp_low_f"],
                               THRESHOLDS["temp_high_f"])

            iot.publish(client, Reading("temperature", temperature, "F",
                                        tags={"location": "kennel"}))
            logger.info("%s F (%s)", temperature, state)

            if state != last_state:
                if state in MESSAGES:
                    iot.publish_event(client, "alarm", MESSAGES[state], level="warn")
                last_state = state

            time.sleep(SETTINGS["interval_s"])
    except KeyboardInterrupt:
        pass
    finally:
        display.sensor().clear()
        iot.publish_event(client, "offline", "climate node down")
        client.disconnect()


if __name__ == "__main__":
    main()
