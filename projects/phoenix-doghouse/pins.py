"""Physical wiring for the dog house.

BOARD numbering - header positions, not BCM lines. That is how this relay
board is wired and documented; see docs/pinmap.md for the conversion.

Was smarthouse/automation/settings.py, which also carried logging helpers and
the animal's profile. Logging now lives in pihome.log and the profile in
config.json, so this file is only the wiring.
"""

PIN_MODE = "BOARD"

# Inputs
FOOD_SENSOR = 20
WATER_SENSOR = 21
MOTION_SENSOR = 22

# Output controls
FOOD_CONTROL = 32
WATER_CONTROL = 36
WATER_MOTOR = 11          # PWM servo - see recipes/gpio/servo_ramp.py
HEAT_CONTROL = 38
COOL_CONTROL = 40
BUZZER_CONTROL = 35

# Status LEDs
COOL_LED = 29
HEAT_LED = 31
FOOD_LED = 33
STATUS_LED = 37
ACTIVE_LED = 7

# CONFLICT: the original also had waterLed = 35, which BUZZER_CONTROL claims.
# Unresolved - it needs tracing on the physical board. Left out rather than
# guessed at. See docs/pinmap.md.
# WATER_LED = 35

ALL_OUTPUTS = [
    FOOD_CONTROL, WATER_CONTROL, HEAT_CONTROL, COOL_CONTROL, BUZZER_CONTROL,
    COOL_LED, HEAT_LED, FOOD_LED, STATUS_LED, ACTIVE_LED,
]
