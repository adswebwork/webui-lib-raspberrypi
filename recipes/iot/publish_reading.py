#!/usr/bin/env python3
"""Publish a sensor reading to AWS IoT Core.

What it does
    Connects, sends one temperature reading in the fleet's envelope format,
    and disconnects. The smallest complete publish.

Hardware
    Any Pi with credentials provisioned (see secrets/README.md).

Wiring
    None.

Run on a Pi
    python3 recipes/iot/publish_reading.py

Run on your Mac
    tools/dev python3 recipes/iot/publish_reading.py
    (set PIHOME_MOCK=1 to publish to a MockClient rather than AWS)

Copy into a project
    Do NOT copy the envelope - import Reading from pihome.reading. It is the
    contract the web UI reads, and a forked copy will drift from it. Copy the
    connect/publish shape only.

requires: AWSIoTPythonSDK
"""
import os

from pihome import iot
from pihome.reading import Reading

# --- tunables -------------------------------------------------------------
DEVICE = None            # None = whoever this machine is (see pihome.identity)
METRIC = "temperature"
UNIT = "F"
# --------------------------------------------------------------------------


if __name__ == "__main__":
    if os.environ.get("PIHOME_MOCK"):
        client = iot.MockClient()
        print("(mock client - nothing leaves this machine)")
    else:
        client = iot.connect(DEVICE)

    try:
        iot.publish(client, Reading(METRIC, 72.5, UNIT, tags={"source": "recipe"}))
        for topic, payload in getattr(client, "published", []):
            print(topic, "->", payload)
    finally:
        client.disconnect()
