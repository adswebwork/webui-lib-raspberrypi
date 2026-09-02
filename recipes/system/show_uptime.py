#!/usr/bin/env python3
"""Report how long this Pi has been up.

What it does
    Reads /proc/uptime and prints it in English - "3 days, 4 hrs, 12 mins,
    7 secs". Useful for spotting a node that has been quietly rebooting.

Hardware
    Any Pi. (Linux only - /proc/uptime does not exist on macOS.)

Wiring
    None.

Run on a Pi
    python3 recipes/system/show_uptime.py

Run on your Mac
    The formatter works anywhere; reading /proc/uptime does not. Pass a number
    to human_uptime() to see the formatting.

Copy into a project
    Import from pihome.uptime rather than copying. Publish it as a reading and
    a dashboard can show which nodes restarted overnight:
    Reading("uptime", uptime_seconds(), "s")

requires: (nothing)
"""
from pihome.uptime import human_uptime

if __name__ == "__main__":
    try:
        print("up time:", human_uptime())
    except OSError:
        print("no /proc/uptime here; formatter demo:")
        for seconds in (45, 3600, 273907):
            print("  {:>8}s -> {}".format(seconds, human_uptime(seconds)))
