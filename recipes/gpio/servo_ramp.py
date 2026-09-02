#!/usr/bin/env python3
"""Drive a servo through a duty-cycle ramp, to dispense a measured amount.

What it does
    Steps a servo's PWM duty cycle up in small increments with a pause between
    each, then returns it. Written for a water dispenser: the ramp is what
    makes it pour steadily instead of slopping.

    The duty values are calibrated against real hardware. Treat them as
    measurements, not defaults - re-tune them for your own servo and load.

Hardware
    A hobby servo on a PWM-capable pin, powered separately if it stalls.

Wiring
    BOARD 11 -> servo signal. Servo power from its own 5V supply, grounds
    tied together.

Run on a Pi
    python3 recipes/gpio/servo_ramp.py

Run on your Mac
    Not meaningful - RPi.GPIO has no mock backend and PWM timing is real.

Copy into a project
    Keep ramp(). Preserve the duty numbers unless you have re-measured them.

requires: RPi.GPIO
"""
import time

import RPi.GPIO as GPIO

# --- tunables (calibrated against real hardware - re-measure before changing)
PIN = 11                 # BOARD numbering
FREQUENCY_HZ = 50        # standard hobby servo
DUTY_START = 2
DUTY_END = 12
PULSE_SECONDS = 0.3      # servo driven
REST_SECONDS = 0.7       # servo released between steps
SETTLE_SECONDS = 5
# --------------------------------------------------------------------------


def ramp(pwm, duty_start=DUTY_START, duty_end=DUTY_END):
    """Step the duty cycle up, pulsing and resting at each position."""
    pwm.start(0)
    time.sleep(1)
    duty = duty_start
    while duty <= duty_end:
        pwm.ChangeDutyCycle(duty)
        time.sleep(PULSE_SECONDS)
        pwm.ChangeDutyCycle(0)
        time.sleep(REST_SECONDS)
        duty += 1

    # Let it settle, then return to the start position and release.
    time.sleep(SETTLE_SECONDS)
    pwm.ChangeDutyCycle(duty_start)
    time.sleep(0.5)
    pwm.ChangeDutyCycle(0)


if __name__ == "__main__":
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(PIN, GPIO.OUT)
    pwm = GPIO.PWM(PIN, FREQUENCY_HZ)
    try:
        ramp(pwm)
        print("ramp complete")
    except KeyboardInterrupt:
        pass
    finally:
        pwm.stop()
        GPIO.cleanup()
