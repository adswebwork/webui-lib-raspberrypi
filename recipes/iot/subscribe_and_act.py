#!/usr/bin/env python3
"""Switch an output based on a reading from another Pi.

What it does
    Subscribes to temperature from anywhere in the fleet and turns a fan on
    when it goes above a threshold. One Pi senses, another acts - the pattern
    the whole message bus exists for.

Hardware
    A relay or fan on a BCM pin, plus provisioned credentials.

Wiring
    BCM 26 -> relay IN.

Run on a Pi
    python3 recipes/iot/subscribe_and_act.py

Run on your Mac
    tools/dev python3 recipes/iot/subscribe_and_act.py

Copy into a project
    Keep the hysteresis. Switching on a bare > comparison makes a relay
    chatter when the reading hovers on the threshold, which wears the contacts
    and is audible from the next room.

requires: AWSIoTPythonSDK, gpiozero
"""
import time

from gpiozero import OutputDevice

from pihome import iot

# --- tunables -------------------------------------------------------------
OUTPUT_PIN = 26          # BCM
IDEAL_F = 80
HYSTERESIS_F = 2         # must fall this far below IDEAL_F before switching off
WATCH_DEVICE = "+"       # or a specific device, e.g. "sensehat-01"
# --------------------------------------------------------------------------

fan = OutputDevice(OUTPUT_PIN, initial_value=False)


def on_reading(reading, client=None):
    if reading.metric != "temperature":
        return
    try:
        temperature = float(reading.value)
    except (TypeError, ValueError):
        print("ignoring non-numeric temperature: {!r}".format(reading.value))
        return

    if not fan.value and temperature > IDEAL_F:
        fan.on()
        print("{} F from {} -> fan ON".format(temperature, reading.device))
    elif fan.value and temperature < IDEAL_F - HYSTERESIS_F:
        fan.off()
        print("{} F from {} -> fan OFF".format(temperature, reading.device))


if __name__ == "__main__":
    client = iot.connect()
    try:
        iot.subscribe_readings(client, on_reading, device=WATCH_DEVICE,
                               metric="temperature")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        fan.off()
        client.disconnect()
