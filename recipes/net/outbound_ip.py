#!/usr/bin/env python3
"""Find this machine's LAN address.

What it does
    Reports the address of the interface that actually reaches the internet.

    It opens a UDP socket toward a public address and asks what local address
    the kernel chose. No packet is sent - UDP connect() only sets the route.
    socket.gethostbyname(hostname()) is the obvious alternative and is often
    wrong on a Pi: it happily returns 127.0.1.1.

Hardware
    Any machine.

Wiring
    None.

Run on a Pi
    python3 recipes/net/outbound_ip.py

Run on your Mac
    python3 recipes/net/outbound_ip.py

Copy into a project
    Import from pihome.identity instead of copying.

requires: (nothing)
"""
import socket


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
    print("hostname:   ", socket.gethostname())
    print("outbound ip:", outbound_ip())
    try:
        print("gethostbyname:", socket.gethostbyname(socket.gethostname()),
              "  <- often 127.0.1.1 on a Pi, which is why we do not use it")
    except socket.gaierror as exc:
        print("gethostbyname failed:", exc)
