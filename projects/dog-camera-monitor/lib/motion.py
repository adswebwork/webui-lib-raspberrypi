"""Motion watching with a cooldown. Started as recipes/gpio/read_pir.py.

Diverged from the recipe: a cooldown is built in, because one dog crossing the
kennel should produce one photograph, not forty.
"""
import time

from gpiozero import MotionSensor

from pihome import log

logger = log.get_logger("motion")


class CooldownWatcher:
    """Calls `on_motion` when the PIR trips, at most once per cooldown."""

    def __init__(self, pin, on_motion, cooldown_s=30):
        self.cooldown_s = cooldown_s
        self.on_motion = on_motion
        self._last = 0.0
        self.sensor = MotionSensor(pin)
        self.sensor.when_motion = self._fire

    def _fire(self):
        now = time.time()
        if now - self._last < self.cooldown_s:
            logger.debug("motion within cooldown, ignoring")
            return
        self._last = now
        self.on_motion()
