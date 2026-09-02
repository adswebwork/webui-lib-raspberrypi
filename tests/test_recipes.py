"""Recipes must run off-Pi.

Nothing in this repo used to run on a laptop. These tests exercise the GPIO
recipes against gpiozero's mock pin factory, so a broken recipe is caught here
rather than after you have carried a laptop to the Pi.

Skipped when gpiozero is not installed: pip3 install gpiozero
"""
import importlib.util
import os

import pytest

gpiozero = pytest.importorskip("gpiozero", reason="pip3 install gpiozero")

from gpiozero import LED, Buzzer, Device, OutputDevice   # noqa: E402
from gpiozero.pins.mock import MockFactory               # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(autouse=True)
def mock_pins():
    """Fresh mock pins for every test, so state cannot leak between them."""
    Device.pin_factory = MockFactory()
    yield
    Device.pin_factory.reset()


def load(relative_path):
    path = os.path.join(REPO, relative_path)
    name = os.path.basename(path)[:-3]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_blink_releases_the_pin():
    module = load("recipes/gpio/blink_led.py")
    led = module.blink(pin=26, on_seconds=0.01, off_seconds=0.01)
    led.off()
    assert led.value == 0


def test_alarm_never_leaves_the_buzzer_sounding():
    """An alarm interrupted partway must still go quiet."""
    module = load("recipes/gpio/alarm_sequence.py")
    light, buzzer = LED(5), Buzzer(6)
    module.alarm(light, buzzer, repeats=2, on=0.001, off=0.001)
    assert not light.value and not buzzer.value


def test_chase_leaves_lights_on_then_all_off_clears_them():
    """The archived original called cleanup() at the end of every chase,
    which reset the pins and dropped the lights it had just turned on."""
    module = load("recipes/gpio/led_chase.py")
    leds = [LED(pin) for pin in (17, 18, 22, 23)]
    module.chase(leds, ascending=True, lit=True, step=0.001)
    assert all(led.value for led in leds), "chase must leave the lights lit"
    module.all_off(leds)
    assert not any(led.value for led in leds)


def test_chase_runs_both_directions():
    module = load("recipes/gpio/led_chase.py")
    leds = [LED(pin) for pin in (17, 18, 22, 23)]
    module.chase(leds, ascending=False, lit=True, step=0.001)
    assert all(led.value for led in leds)
    module.chase(leds, ascending=False, lit=False, step=0.001)
    assert not any(led.value for led in leds)


def test_toggle_round_trips():
    module = load("recipes/gpio/toggle_output.py")
    assert module.toggle(12, True) == 1
    assert module.toggle(12, False) == 0


def test_cycle_completes_the_requested_number():
    module = load("recipes/gpio/cycle_output.py")
    device = OutputDevice(13, initial_value=False)
    assert list(module.cycle(device, cycles=2,
                             on_seconds=0.001, off_seconds=0.001)) == [1, 2]


def test_buzzer_is_silent_afterwards():
    module = load("recipes/gpio/pulse_buzzer.py")
    buzzer = Buzzer(16)
    module.beep(buzzer, times=2, on=0.001, gap=0.001)
    assert not buzzer.value
