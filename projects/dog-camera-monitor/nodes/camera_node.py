#!/usr/bin/env python3
"""Camera node: photograph the kennel on motion, and on a schedule.

Runs on the Pi with the camera module.

    PYTHONPATH=/home/pi/raspberrypi python3 nodes/camera_node.py
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pihome import config, hw, identity, iot, log  # noqa: E402
from pihome.reading import Reading                 # noqa: E402

from lib import capture, motion                    # noqa: E402

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = config.load(os.path.join(HERE, "config.json"))
SETTINGS = CONFIG["nodes"]["camera_node"]
MESSAGES = CONFIG["messages"]

logger = log.get_logger("camera_node")


def main():
    identity.assume(SETTINGS["device"])
    camera = hw.camera()
    camera.configure(camera.create_still_configuration())
    camera.start()
    time.sleep(2)                       # let exposure and white balance settle

    client = iot.connect()
    iot.publish_event(client, "online", "camera node up")

    def photograph(trigger):
        path = capture.capture(camera)
        capture.prune(keep=SETTINGS["keep_images"])
        name = os.path.basename(path)
        logger.info("captured %s (%s)", name, trigger)
        iot.publish(client, Reading("capture", 1, "count",
                                    tags={"image": name, "trigger": trigger}))
        return path

    watcher = motion.CooldownWatcher(
        SETTINGS["pir_pin"],
        on_motion=lambda: (
            iot.publish(client, Reading("motion", True, "bool")),
            iot.publish_event(client, "motion", MESSAGES["motion"]),
            photograph("motion"),
        ),
        cooldown_s=SETTINGS["motion_cooldown_s"],
    )

    try:
        while True:
            time.sleep(SETTINGS["capture_interval_s"])
            photograph("schedule")
    except KeyboardInterrupt:
        pass
    finally:
        watcher.sensor.close()
        camera.close()
        iot.publish_event(client, "offline", "camera node down")
        client.disconnect()


if __name__ == "__main__":
    main()
