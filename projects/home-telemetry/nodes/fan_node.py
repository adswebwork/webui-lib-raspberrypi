#!/usr/bin/env python3
"""Fan node: switch a fan when another Pi reports it is too warm.

Subscribes to temperature from anywhere in the fleet. Formerly
_globalConfig/sys3.py.

Note this node authenticates with sys2's certificate - long-standing
behaviour, recorded in devices.json rather than hidden in a call.

    python3 nodes/fan_node.py
"""
import os
import time

from gpiozero import OutputDevice

from pihome import config, identity, iot, log

CONFIG = config.load(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  os.pardir, "config.json"))
SETTINGS = CONFIG["nodes"]["fan_node"]
THRESHOLDS = CONFIG["thresholds"]

# The one device this fan answers to. Not "+": see main().
SOURCE = SETTINGS["source_device"]

logger = log.get_logger("fan_node")

# Claimed in main(), not at import. Constructing it here would mean merely
# importing this module takes the pin, which breaks tests and stops two nodes
# from being loaded in one process.
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

    ideal = THRESHOLDS["ideal_f"]
    hysteresis = THRESHOLDS["hysteresis_f"]

    if not fan.value and temperature > ideal:
        fan.on()
        logger.info("%s F from %s -> fan ON", temperature, reading.device)
        iot.publish_event(_client, "actuate", "fan on", source=reading.device)
    elif fan.value and temperature < ideal - hysteresis:
        fan.off()
        logger.info("%s F from %s -> fan OFF", temperature, reading.device)
        iot.publish_event(_client, "actuate", "fan off", source=reading.device)


def main():
    global _client, fan
    identity.assume(SETTINGS["device"])
    fan = OutputDevice(SETTINGS["output_pin"], initial_value=False)
    _client = iot.connect()
    iot.publish_event(_client, "online", "fan node up")

    # One named publisher, not every device on the bus. The whole point of
    # putting the device in the topic is being able to say which Pi this fan
    # answers to; subscribing to `+` would throw that away and let any node
    # that happens to report a temperature drive mains voltage.
    iot.subscribe_readings(_client, on_reading, device=SOURCE,
                           metric="temperature")
    # The pre-schema topic too, until every publisher has changed over. It
    # carries no device, so readings on it are attributed to the same source.
    iot.subscribe_legacy(_client, on_reading, device_hint=SOURCE)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        fan.off()
        iot.publish_event(_client, "offline", "fan node down")
        _client.disconnect()


if __name__ == "__main__":
    main()
