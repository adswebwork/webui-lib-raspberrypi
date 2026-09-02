#!/usr/bin/env python3
"""Turn one output on or off, once.

What it does
    Sets a single GPIO output high or low and exits. The building block for
    switching a relay, a light or a fan from another script.

Hardware
    A relay channel or LED on a BCM pin.

Wiring
    BCM 26 -> relay IN. Relay VCC/GND to the Pi's 5V/GND.

Run on a Pi
    python3 recipes/gpio/toggle_output.py

Run on your Mac
    tools/dev python3 recipes/gpio/toggle_output.py

Copy into a project
    Keep toggle(); it is safe to call repeatedly. Note that gpiozero device
    objects must outlive the call - if you construct one inside a function and
    return nothing, it is garbage-collected and the pin resets.

requires: gpiozero
"""
from gpiozero import OutputDevice

# --- tunables -------------------------------------------------------------
PIN = 26                 # BCM numbering
ACTIVE_HIGH = True       # False for relay boards that switch on a LOW signal
# --------------------------------------------------------------------------

_devices = {}


def _device(pin):
    """One long-lived OutputDevice per pin.

    Held in a module-level dict on purpose: letting it fall out of scope makes
    gpiozero close the pin and drop the output.
    """
    if pin not in _devices:
        _devices[pin] = OutputDevice(pin, active_high=ACTIVE_HIGH,
                                     initial_value=False)
    return _devices[pin]


def toggle(pin=PIN, on=True):
    """Drive `pin` on or off. Returns the resulting state."""
    device = _device(pin)
    device.on() if on else device.off()
    return device.value


if __name__ == "__main__":
    import time
    try:
        print("BCM {} -> on".format(PIN))
        toggle(PIN, True)
        time.sleep(2)
        print("BCM {} -> off".format(PIN))
        toggle(PIN, False)
    finally:
        for device in _devices.values():
            device.off()
