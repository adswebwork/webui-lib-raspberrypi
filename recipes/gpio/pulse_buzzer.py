#!/usr/bin/env python3
"""Sound a buzzer in short pulses.

What it does
    Three short beeps, then stops. The audible half of an alert.

Hardware
    An active buzzer on a BCM pin. (A passive buzzer needs PWM - see
    servo_ramp.py for the PWM pattern.)

Wiring
    BCM 19 -> buzzer +, buzzer - -> ground.

Run on a Pi
    python3 recipes/gpio/pulse_buzzer.py

Run on your Mac
    tools/dev python3 recipes/gpio/pulse_buzzer.py
    (mock pins - you will see no output, but the logic runs)

Copy into a project
    Keep beep(). Call it from an alarm handler rather than looping here.

requires: gpiozero
"""
import time

from gpiozero import Buzzer

# --- tunables -------------------------------------------------------------
PIN = 19                 # BCM numbering
BEEPS = 3
BEEP_SECONDS = 0.2
GAP_SECONDS = 1.0
# --------------------------------------------------------------------------


def beep(buzzer, times=BEEPS, on=BEEP_SECONDS, gap=GAP_SECONDS):
    """Sound `times` short pulses."""
    for _ in range(times):
        buzzer.on()
        time.sleep(on)
        buzzer.off()
        time.sleep(gap)


if __name__ == "__main__":
    buzzer = Buzzer(PIN)
    try:
        beep(buzzer)
        print("done")
    finally:
        buzzer.off()
