"""A no-op RPi.GPIO, so BOARD-numbered nodes can be imported off a Pi.

gpiozero has a mock backend; RPi.GPIO has none, and three nodes need BOARD
numbering (physical header positions), which gpiozero cannot express. Without
this, merely importing those nodes fails on any machine that is not a Pi -
which is every machine a test runs on.

This records calls rather than driving anything. It is deliberately not a
simulator: it exists so an import succeeds and a smoke test can assert which
pins a node set up, not so you can develop pin logic off the hardware. Test
real GPIO behaviour with gpiozero's MockFactory instead - see
tests/test_recipes.py.
"""

BCM = "BCM"
BOARD = "BOARD"
OUT = "OUT"
IN = "IN"
HIGH = 1
LOW = 0

# What the caller did, in order. Tests can read these; nothing else should.
mode = None
setup_pins = {}
pin_states = {}
_warnings = True


class PWM:
    """Accepts the real constructor and calls, does nothing."""

    def __init__(self, pin, frequency):
        self.pin = pin
        self.frequency = frequency
        self.duty_cycle = 0

    def start(self, duty_cycle=0):
        self.duty_cycle = duty_cycle

    def ChangeDutyCycle(self, duty_cycle):
        self.duty_cycle = duty_cycle

    def ChangeFrequency(self, frequency):
        self.frequency = frequency

    def stop(self):
        self.duty_cycle = 0


def setwarnings(flag):
    global _warnings
    _warnings = flag


def setmode(new_mode):
    global mode
    mode = new_mode


def setup(pin, direction, **kwargs):
    setup_pins[pin] = direction
    pin_states.setdefault(pin, LOW)


def output(pin, value):
    pin_states[pin] = HIGH if value else LOW


def input(pin):
    """Always LOW. A stub cannot know what a sensor would have read."""
    return pin_states.get(pin, LOW)


def cleanup(pin=None):
    global mode
    if pin is None:
        mode = None
        setup_pins.clear()
        pin_states.clear()
    else:
        setup_pins.pop(pin, None)
        pin_states.pop(pin, None)
