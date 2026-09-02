#!/usr/bin/env python3
"""Status node: blink the status LED so you can see the system is alive.

Was smarthouse/automation/system3_register.py.

    PYTHONPATH=/home/pi/raspberrypi python3 nodes/status_node.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import RPi.GPIO as GPIO                        # noqa: E402

from pihome import config, identity, iot, log  # noqa: E402

from lib import controls                       # noqa: E402

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = config.load(os.path.join(HERE, "config.json"))
SETTINGS = CONFIG["nodes"]["status_node"]

logger = log.get_logger("status_node")


def main():
    identity.assume(SETTINGS["device"])
    controls.setup()
    client = iot.connect()
    iot.publish_event(client, "online", "status node up")
    try:
        controls.blink_status(SETTINGS["blink_interval_s"])
    except KeyboardInterrupt:
        pass
    finally:
        controls.all_off()
        GPIO.cleanup()
        iot.publish_event(client, "offline", "status node down")
        client.disconnect()


if __name__ == "__main__":
    main()
