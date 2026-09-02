#!/usr/bin/env python3
"""Alert node: run the fan when the kennel gets too warm.

Subscribes to the kennel's temperature. Runs on the Pi with the relay.

    PYTHONPATH=/home/pi/raspberrypi python3 nodes/alert_node.py
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gpiozero import OutputDevice              # noqa: E402

from pihome import config, identity, iot, log  # noqa: E402

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = config.load(os.path.join(HERE, "config.json"))
SETTINGS = CONFIG["nodes"]["alert_node"]
THRESHOLDS = CONFIG["thresholds"]
MESSAGES = CONFIG["messages"]

# The one device this fan answers to. Not "+": see main().
SOURCE = SETTINGS["source_device"]

logger = log.get_logger("alert_node")

# Claimed in main(), not at import - see fan_node for why.
fan = None
_client = None


def on_reading(reading):
    """Switch the fan, with hysteresis so the relay does not chatter."""
    if reading.metric != "temperature":
        return
    try:
        temperature = float(reading.value)
    except (TypeError, ValueError):
        logger.warning("ignoring non-numeric temperature: %r", reading.value)
        return

    high = THRESHOLDS["temp_high_f"]
    hysteresis = THRESHOLDS["hysteresis_f"]

    if not fan.value and temperature >= high:
        fan.on()
        logger.info("%s F from %s -> fan ON", temperature, reading.device)
        iot.publish_event(_client, "actuate", MESSAGES["too_hot"], level="warn")
    elif fan.value and temperature < high - hysteresis:
        fan.off()
        logger.info("%s F from %s -> fan OFF", temperature, reading.device)
        iot.publish_event(_client, "actuate", "fan off")


def main():
    global _client, fan
    identity.assume(SETTINGS["device"])
    fan = OutputDevice(SETTINGS["output_pin"], initial_value=False)
    _client = iot.connect()
    iot.publish_event(_client, "online", "alert node up")
    # One named publisher, not every device on the bus. Subscribing to `+`
    # would let any node that happens to report a temperature - including
    # the house fleet, which shares this site - drive the kennel fan.
    iot.subscribe_readings(_client, on_reading, device=SOURCE,
                           metric="temperature")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        fan.off()
        iot.publish_event(_client, "offline", "alert node down")
        _client.disconnect()


if __name__ == "__main__":
    main()
