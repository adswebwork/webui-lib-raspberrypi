#!/usr/bin/env python3
"""Capture a timestamped still from the Pi camera.

What it does
    Takes one photo, named for the moment it was taken, into a directory of
    your choosing.

Hardware
    Raspberry Pi with a camera module on the CSI ribbon connector.

Wiring
    Ribbon cable, silver contacts facing the HDMI port. Enable the camera with
    raspi-config if it is not already on.

Run on a Pi
    python3 recipes/camera/capture_still.py

Run on your Mac
    Not meaningful - there is no camera. Run it on the camera Pi.

Copy into a project
    Keep capture(). Uses picamera2: the legacy `picamera` module and
    raspistill were both removed in Raspberry Pi OS Bullseye, so anything
    written against those will not run on a current Pi.

requires: picamera2
"""
import os
import time

from picamera2 import Picamera2

# --- tunables -------------------------------------------------------------
OUTPUT_DIR = os.path.expanduser("~/captures")
WARMUP_SECONDS = 2       # let exposure and white balance settle
ROTATION = 0             # 0, 90, 180 or 270
# --------------------------------------------------------------------------


def capture(output_dir=OUTPUT_DIR, warmup=WARMUP_SECONDS):
    """Take one photo. Returns the path written."""
    os.makedirs(output_dir, exist_ok=True)
    filename = time.strftime("%Y-%m-%d-%H%M%S") + ".jpg"
    path = os.path.join(output_dir, filename)

    camera = Picamera2()
    try:
        camera.configure(camera.create_still_configuration())
        camera.start()
        time.sleep(warmup)
        camera.capture_file(path)
    finally:
        camera.close()
    return path


if __name__ == "__main__":
    print("captured", capture())
