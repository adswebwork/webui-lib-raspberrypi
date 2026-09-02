#!/usr/bin/env python3
"""Capture a still every few seconds, discarding old ones.

What it does
    A timelapse loop that also prunes: without a retention limit an SD card
    fills silently and the Pi stops being able to write anything at all.

Hardware
    Raspberry Pi with a camera module.

Wiring
    Ribbon cable to the CSI connector.

Run on a Pi
    python3 recipes/camera/capture_timelapse.py

Run on your Mac
    Not meaningful - there is no camera.

Copy into a project
    Keep prune(). Run this as a systemd service rather than a cron loop, so
    it restarts if the camera stack wedges.

requires: picamera2
"""
import os
import time

from picamera2 import Picamera2

# --- tunables -------------------------------------------------------------
OUTPUT_DIR = os.path.expanduser("~/captures")
INTERVAL_SECONDS = 300
KEEP_IMAGES = 500        # oldest beyond this are deleted
WARMUP_SECONDS = 2
# --------------------------------------------------------------------------


def prune(output_dir=OUTPUT_DIR, keep=KEEP_IMAGES):
    """Delete the oldest images beyond `keep`. Returns how many went."""
    images = sorted(
        (os.path.join(output_dir, n) for n in os.listdir(output_dir)
         if n.endswith(".jpg")),
        key=os.path.getmtime)
    removed = 0
    for path in images[:-keep] if keep else []:
        os.remove(path)
        removed += 1
    return removed


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    camera = Picamera2()
    camera.configure(camera.create_still_configuration())
    camera.start()
    time.sleep(WARMUP_SECONDS)
    try:
        while True:
            path = os.path.join(OUTPUT_DIR,
                                time.strftime("%Y-%m-%d-%H%M%S") + ".jpg")
            camera.capture_file(path)
            dropped = prune()
            print("captured {}{}".format(
                path, " (pruned {})".format(dropped) if dropped else ""))
            time.sleep(INTERVAL_SECONDS)
    except KeyboardInterrupt:
        pass
    finally:
        camera.close()
