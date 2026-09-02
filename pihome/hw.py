"""Hardware access that degrades gracefully off a Pi.

Nothing in this repo used to run on a laptop: every script did
`import RPi.GPIO` or `from sense_hat import SenseHat` at module scope, which
raises on any other machine. These helpers pick real hardware on a Pi and an
emulator or mock elsewhere, so core code and tests run anywhere.

Recipes do NOT use this - they import sense_hat directly and stay plain Pi
code. tools/dev puts a shim on PYTHONPATH to make them work off-Pi instead.
"""
import os

from pihome import log

_logger = log.get_logger("hw")
_MODEL = "/proc/device-tree/model"


def is_pi():
    """True on Raspberry Pi hardware."""
    try:
        with open(_MODEL) as handle:
            return "raspberry pi" in handle.read().lower()
    except OSError:
        return False


def SenseHat():
    """A Sense HAT: the real one on a Pi, sense_emu off it.

    Raises ImportError naming both options if neither is installed, rather
    than a bare "No module named sense_hat".
    """
    try:
        from sense_hat import SenseHat as _Real
        return _Real()
    except ImportError:
        pass
    try:
        from sense_emu import SenseHat as _Emulated
        _logger.info("using sense_emu (no Sense HAT present)")
        return _Emulated()
    except ImportError:
        raise ImportError(
            "no Sense HAT available. On a Pi: sudo apt install python3-sense-hat. "
            "On a laptop: pip3 install sense-emu, then run the emulator.")


def pin_factory():
    """gpiozero pin factory: native on a Pi, MockFactory elsewhere.

    Set GPIOZERO_PIN_FACTORY=mock to force mocking anywhere.
    """
    if os.environ.get("GPIOZERO_PIN_FACTORY") == "mock" or not is_pi():
        from gpiozero.pins.mock import MockFactory
        return MockFactory()
    return None          # gpiozero picks its own native factory


def use_mock_pins():
    """Point gpiozero at mock pins process-wide. For tests and desktop runs."""
    from gpiozero import Device
    from gpiozero.pins.mock import MockFactory
    Device.pin_factory = MockFactory()
    return Device.pin_factory


def camera():
    """A picamera2 Picamera2 on a Pi; raises with guidance elsewhere."""
    try:
        from picamera2 import Picamera2
        return Picamera2()
    except ImportError:
        raise ImportError(
            "picamera2 not available. On Raspberry Pi OS Bullseye or later: "
            "sudo apt install python3-picamera2. The legacy `picamera` module "
            "and raspistill were removed in Bullseye.")
