#!/usr/bin/env python3
"""Show this Pi's name and LAN address on the LED matrix.

What it does
    Scrolls the hostname and IP address, so you can find a headless Pi on the
    network without plugging in a monitor. Repeats until interrupted.

Hardware
    Raspberry Pi with a Sense HAT.

Wiring
    None.

Run on a Pi
    python3 recipes/sensehat/show_ip_address.py

Run on your Mac
    tools/dev python3 recipes/sensehat/show_ip_address.py

Copy into a project
    Keep outbound_ip(). It finds the address of the interface that actually
    reaches the internet, which gethostbyname(hostname()) often gets wrong on
    a multi-homed Pi (it can return 127.0.1.1).

requires: sense-hat  (dev: sense-emu)
"""
import socket
import time

from sense_hat import SenseHat

# --- tunables -------------------------------------------------------------
ROTATION = 90
INTERVAL_SECONDS = 5
NAME_COLOUR = (255, 255, 255)
IP_COLOUR = (0, 255, 0)
# --------------------------------------------------------------------------

sense = SenseHat()
sense.set_rotation(ROTATION)
sense.low_light = True


def outbound_ip():
    """LAN address of the interface that reaches the internet."""
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(("8.8.8.8", 80))
        return probe.getsockname()[0]
    except OSError:
        return "0.0.0.0"
    finally:
        probe.close()


if __name__ == "__main__":
    hostname = socket.gethostname()
    address = outbound_ip()
    print("{} at {}".format(hostname, address))
    try:
        while True:
            sense.show_message(hostname, text_colour=NAME_COLOUR)
            time.sleep(1)
            sense.show_message("IP " + address, text_colour=IP_COLOUR)
            time.sleep(INTERVAL_SECONDS)
    except KeyboardInterrupt:
        pass
    finally:
        sense.clear()
