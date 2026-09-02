"""Still capture. Started as recipes/camera/capture_still.py.

Diverged from the recipe: this one prunes old images, because the kennel
camera runs unattended and a full SD card stops the Pi writing anything at all.
"""
import os
import time

from pihome import log

logger = log.get_logger("capture")

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "data", "captures")


def capture(camera, output_dir=OUTPUT_DIR):
    """Take one photo. Returns the path written."""
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, time.strftime("%Y-%m-%d-%H%M%S") + ".jpg")
    camera.capture_file(path)
    return path


def prune(output_dir=OUTPUT_DIR, keep=500):
    """Delete the oldest images, keeping the newest `keep`. Returns how many went.

    `keep=None` disables pruning. `keep` must otherwise be a positive number:
    0 is rejected rather than guessed at, because it reads two opposite ways -
    "keep no images" and "no limit, keep everything" - and this node prunes
    immediately after every capture, so guessing wrong either deletes the photo
    just taken or lets the card fill up, which is the failure this whole
    function exists to prevent. Say None if you mean stop pruning.
    """
    if keep is None:
        return 0
    if keep <= 0:
        raise ValueError(
            "keep must be positive (got {!r}); pass keep=None to disable "
            "pruning. keep=0 would delete each capture as it was taken."
            .format(keep))

    if not os.path.isdir(output_dir):
        return 0
    images = sorted(
        (os.path.join(output_dir, n) for n in os.listdir(output_dir)
         if n.endswith(".jpg")),
        key=os.path.getmtime)

    removed = 0
    for path in images[:-keep]:
        os.remove(path)
        removed += 1
    if removed:
        logger.info("pruned %d old captures", removed)
    return removed
