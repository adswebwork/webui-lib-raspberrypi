#!/usr/bin/env python3
"""Sustenance node: food and water dispensing.

Was smarthouse/automation/system2_register.py, which called testControl() to
cycle every relay. This does the same smoke test, then reports it.

    PYTHONPATH=/home/pi/raspberrypi python3 nodes/sustenance_node.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pihome import config, identity, iot, log  # noqa: E402
from pihome.reading import Reading             # noqa: E402

from lib import controls                       # noqa: E402

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = config.load(os.path.join(HERE, "config.json"))
SETTINGS = CONFIG["nodes"]["sustenance_node"]
ANIMAL = CONFIG["animal"]

logger = log.get_logger("sustenance_node")


def main():
    identity.assume(SETTINGS["device"])
    controls.setup()
    client = iot.connect()
    iot.publish_event(client, "online",
                      "sustenance node up for {}".format(ANIMAL["name"]))
    try:
        controls.exercise_all()
        iot.publish(client, Reading("food_level", ANIMAL["food"], "%"))
        iot.publish(client, Reading("water_level", ANIMAL["water"], "%"))
        logger.info("control check complete")
    except KeyboardInterrupt:
        pass
    finally:
        controls.all_off()
        iot.publish_event(client, "offline", "sustenance node down")
        client.disconnect()


if __name__ == "__main__":
    main()
