#!/usr/bin/env python3
"""Camera node: photograph the kennel on a schedule.

Was smarthouse/automation/system4_register.py, which ran
`os.system("source ~/.bashrc && pwd && msg")` - sourcing an interactive rc
file to reach a shell alias that a non-interactive shell never sees. It then
printed the exit code as though it had worked.

    PYTHONPATH=/home/pi/raspberrypi python3 nodes/camera_node.py
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pihome import config, hw, identity, iot, log  # noqa: E402
from pihome.reading import Reading                 # noqa: E402

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = config.load(os.path.join(HERE, "config.json"))
SETTINGS = CONFIG["nodes"]["camera_node"]
OUTPUT_DIR = os.path.join(HERE, "data", "captures")

logger = log.get_logger("camera_node")


def main():
    identity.assume(SETTINGS["device"])
    camera = hw.camera()
    camera.configure(camera.create_still_configuration())
    camera.start()
    time.sleep(2)

    client = iot.connect()
    iot.publish_event(client, "online", "camera node up")
    try:
        while True:
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            path = os.path.join(OUTPUT_DIR,
                                time.strftime("%Y-%m-%d-%H%M%S") + ".jpg")
            camera.capture_file(path)
            logger.info("captured %s", os.path.basename(path))
            iot.publish(client, Reading("capture", 1, "count",
                                        tags={"image": os.path.basename(path)}))
            time.sleep(SETTINGS["interval_s"])
    except KeyboardInterrupt:
        pass
    finally:
        camera.close()
        iot.publish_event(client, "offline", "camera node down")
        client.disconnect()


if __name__ == "__main__":
    main()
