#!/usr/bin/env python3
"""Photograph whatever set off the motion sensor.

What it does
    Watches a PIR and takes a still when it trips, with a cooldown so one
    person walking past does not produce forty photographs.

Hardware
    Raspberry Pi with a camera module and a PIR sensor.

Wiring
    Camera to the CSI connector. PIR OUT -> BCM 4, VCC -> 5V, GND -> ground.

Run on a Pi
    python3 recipes/camera/capture_on_motion.py

Run on your Mac
    Not meaningful - there is no camera.

Copy into a project
    Keep the cooldown. Publish an Event alongside each capture so the image
    shows up off-device:
    pihome.iot.publish_event(client, "capture", path, image=name)

requires: picamera2, gpiozero
"""
import os
import time
from signal import pause

from gpiozero import MotionSensor
from picamera2 import Picamera2

# --- tunables -------------------------------------------------------------
PIR_PIN = 4              # BCM
OUTPUT_DIR = os.path.expanduser("~/captures")
COOLDOWN_SECONDS = 30    # ignore further motion for this long after a capture
WARMUP_SECONDS = 2
# --------------------------------------------------------------------------

_last_capture = 0.0


def on_motion(camera, output_dir=OUTPUT_DIR, cooldown=COOLDOWN_SECONDS):
    """Capture, unless we captured too recently. Returns a path or None."""
    global _last_capture
    now = time.time()
    if now - _last_capture < cooldown:
        return None
    _last_capture = now

    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, time.strftime("%Y-%m-%d-%H%M%S") + ".jpg")
    camera.capture_file(path)
    return path


if __name__ == "__main__":
    camera = Picamera2()
    camera.configure(camera.create_still_configuration())
    camera.start()
    time.sleep(WARMUP_SECONDS)

    sensor = MotionSensor(PIR_PIN)
    sensor.when_motion = lambda: print("captured", on_motion(camera) or "(cooldown)")

    print("watching for motion (Ctrl-C to stop)")
    try:
        pause()
    except KeyboardInterrupt:
        pass
    finally:
        camera.close()
