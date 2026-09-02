"""Food, water and climate relays for the dog house.

Was smarthouse/automation/routines.py. The pin map moved to pins.py and the
logging to pihome.log; what remains is the hardware control.
"""
import time

import RPi.GPIO as GPIO

from pihome import log

import pins

logger = log.get_logger("controls")

DELAY = 1
LONG_DELAY = 3

_pwm = None


def setup():
    """Configure every output low. Call once at start-up."""
    GPIO.setmode(GPIO.BOARD)
    for pin in pins.ALL_OUTPUTS:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)
    GPIO.setup(pins.WATER_MOTOR, GPIO.OUT)


def all_off():
    """Drop every output. Safe to call twice, and safe to call on the way out."""
    for pin in pins.ALL_OUTPUTS:
        GPIO.output(pin, GPIO.LOW)
    logger.info("all outputs off")


def add_water():
    """Run the dispensing servo through its calibrated duty ramp.

    The duty values are measured against the real servo and load - treat them
    as measurements, not defaults. See recipes/gpio/servo_ramp.py.
    """
    global _pwm
    if _pwm is None:
        _pwm = GPIO.PWM(pins.WATER_MOTOR, 50)

    _pwm.start(0)
    time.sleep(DELAY)
    duty = 2
    while duty <= 12:
        _pwm.ChangeDutyCycle(duty)
        time.sleep(0.3)
        _pwm.ChangeDutyCycle(0)
        time.sleep(0.7)
        duty += 1
    time.sleep(5)
    _pwm.ChangeDutyCycle(2)
    time.sleep(0.5)
    _pwm.ChangeDutyCycle(0)
    _pwm.stop()
    logger.info("water added")


def exercise_all():
    """Energise every control in turn, then drop them. A wiring smoke test."""
    for name, pin in (("food", pins.FOOD_CONTROL), ("water", pins.WATER_CONTROL),
                      ("heat", pins.HEAT_CONTROL), ("cool", pins.COOL_CONTROL)):
        logger.info("%s on", name)
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(DELAY)
    time.sleep(LONG_DELAY)
    all_off()


def blink_status(interval=DELAY):
    """Blink the status LED forever. Caller handles KeyboardInterrupt."""
    GPIO.output(pins.ACTIVE_LED, GPIO.HIGH)
    while True:
        GPIO.output(pins.STATUS_LED, GPIO.HIGH)
        time.sleep(interval)
        GPIO.output(pins.STATUS_LED, GPIO.LOW)
        time.sleep(interval)
