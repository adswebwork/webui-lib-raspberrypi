#!/usr/bin/env python3
"""Listen for readings from the whole fleet, or one device.

What it does
    Subscribes and prints each reading as it arrives, with the device it came
    from. Because the device is in the topic, you can narrow to one Pi without
    filtering in Python.

Hardware
    Any Pi with credentials provisioned. Runs equally well on a laptop.

Wiring
    None.

Run on a Pi
    python3 recipes/iot/subscribe_readings.py

Run on your Mac
    tools/dev python3 recipes/iot/subscribe_readings.py

Copy into a project
    Keep the handler shape. A malformed payload from one node is logged and
    dropped rather than killing the subscriber - which matters when the thing
    subscribing is the node that switches your heating.

requires: AWSIoTPythonSDK
"""
import time

from pihome import iot

# --- tunables -------------------------------------------------------------
DEVICE = "+"             # "+" = every device, or e.g. "sensehat-01"
METRIC = "#"             # "#" = every metric, or e.g. "temperature"
LISTEN_AS = None         # which credentials to connect with; None = this machine
# --------------------------------------------------------------------------


def on_reading(reading):
    print("{}  {:12s} {:>8} {:4s}  from {}".format(
        reading.ts, reading.metric, reading.value, reading.unit, reading.device))


if __name__ == "__main__":
    client = iot.connect(LISTEN_AS)
    try:
        iot.subscribe_readings(client, on_reading, device=DEVICE, metric=METRIC)
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        client.disconnect()
