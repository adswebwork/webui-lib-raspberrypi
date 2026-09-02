#!/usr/bin/env python3
"""Camera node: capture stills and report them.

Formerly _globalConfig/sys4.py, which had never run - it referenced
vars.sys4ca (never defined) and called a Sense HAT temperature function on a
Pi with no Sense HAT.

This node is NOT yet provisioned: there is no secrets/sys4/ credential set.
See secrets/README.md.

    python3 nodes/camera_node.py
"""
import os
import time

from pihome import config, hw, identity, iot, log
from pihome.reading import Reading

CONFIG = config.load(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  os.pardir, "config.json"))
SETTINGS = CONFIG["nodes"]["camera_node"]

OUTPUT_DIR = os.path.expanduser("~/captures")
logger = log.get_logger("camera_node")


def capture(camera):
    """Take one photo. Returns the path written."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, time.strftime("%Y-%m-%d-%H%M%S") + ".jpg")
    camera.capture_file(path)
    return path


def main():
    identity.assume(SETTINGS["device"])
    camera = hw.camera()
    camera.configure(camera.create_still_configuration())
    camera.start()
    time.sleep(2)                      # let exposure settle

    client = iot.connect()
    iot.publish_event(client, "online", "camera node up")

    try:
        while True:
            path = capture(camera)
            logger.info("captured %s", path)
            iot.publish(client, Reading("capture", 1, "count",
                                        tags={"image": os.path.basename(path)}))
            time.sleep(SETTINGS["publish_interval_s"])
    except KeyboardInterrupt:
        pass
    finally:
        camera.close()
        iot.publish_event(client, "offline", "camera node down")
        client.disconnect()


if __name__ == "__main__":
    main()
