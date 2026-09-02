#!/usr/bin/env python3
"""Sense HAT node: publish temperature to the fleet.

Runs on the Pi 3 with the Sense HAT. Formerly _globalConfig/sys1.py.

    python3 nodes/sensehat_node.py
"""
import os
import time

from pihome import config, hw, identity, iot, log, sensors
from pihome.reading import Reading

CONFIG = config.load(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  os.pardir, "config.json"))
SETTINGS = CONFIG["nodes"]["sensehat_node"]
THRESHOLDS = CONFIG["thresholds"]

logger = log.get_logger("sensehat_node")

# Claimed on first use, not at import - same reason as fan_node's pin. Building
# it here meant that merely importing this module took the hardware, which off
# a Pi spawns the sense_emu GUI and on a Pi fails outright where no HAT is
# fitted. Matches lib/climate.py in the other projects.
_sense = None


def sensor():
    global _sense
    if _sense is None:
        _sense = hw.SenseHat()
        _sense.set_rotation(SETTINGS.get("rotation", 90))
        _sense.low_light = True
    return _sense


def read_temperature():
    """Ambient temperature in Fahrenheit, self-heating compensated."""
    return sensors.sense_hat_temperature_f(sensor())


def main():
    identity.assume(SETTINGS["device"])
    sense = sensor()
    client = iot.connect()
    iot.publish_event(client, "online", "sense hat node up")

    try:
        while True:
            temperature = read_temperature()
            iot.publish(client, Reading("temperature", temperature, "F",
                                        tags={"sensor": "sense-hat"}))
            iot.publish(client, Reading("humidity", round(sense.humidity, 1), "%"))
            iot.publish(client, Reading("pressure", round(sense.pressure, 1), "hPa"))
            logger.info("%s F", temperature)
            time.sleep(SETTINGS["publish_interval_s"])
    except KeyboardInterrupt:
        pass
    finally:
        sense.clear()
        iot.publish_event(client, "offline", "sense hat node down")
        client.disconnect()


if __name__ == "__main__":
    main()
