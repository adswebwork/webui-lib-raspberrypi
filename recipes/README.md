# Recipes

Single-file scripts that do one thing on real hardware. **Copy one into a
project and edit it freely** — that is what they are for. Editing the original
never affects anything you have already copied.

## I want to…

### Switch something on and off

| Task | Recipe |
|---|---|
| Blink an LED or relay | [`gpio/blink_led.py`](gpio/blink_led.py) |
| Turn one output on or off, once | [`gpio/toggle_output.py`](gpio/toggle_output.py) |
| Cycle an output a set number of times | [`gpio/cycle_output.py`](gpio/cycle_output.py) |
| Sound a buzzer | [`gpio/pulse_buzzer.py`](gpio/pulse_buzzer.py) |
| Flash a light *and* sound a buzzer | [`gpio/alarm_sequence.py`](gpio/alarm_sequence.py) |
| Alternate two lights (traffic light) | [`gpio/alternate_lights.py`](gpio/alternate_lights.py) |
| Run a light along a row (stairs) | [`gpio/led_chase.py`](gpio/led_chase.py) |
| Dispense a measured amount with a servo | [`gpio/servo_ramp.py`](gpio/servo_ramp.py) |
| Test every relay channel | [`gpio/exercise_relays.py`](gpio/exercise_relays.py) |
| Force everything to a safe state | [`gpio/safe_shutdown.py`](gpio/safe_shutdown.py) |

### Sense something

| Task | Recipe |
|---|---|
| React to motion (PIR) | [`gpio/read_pir.py`](gpio/read_pir.py) |
| Read light level without an ADC | [`gpio/read_light_sensor.py`](gpio/read_light_sensor.py) |
| Switch an output when a sensor trips | [`gpio/sensor_triggers_output.py`](gpio/sensor_triggers_output.py) |
| Read temperature (Sense HAT) | [`sensehat/read_temperature.py`](sensehat/read_temperature.py) |
| Read the joystick | [`sensehat/read_joystick.py`](sensehat/read_joystick.py) |

### Show something on the LED matrix

| Task | Recipe |
|---|---|
| Scroll a message | [`sensehat/show_message.py`](sensehat/show_message.py) |
| Show this Pi's IP address | [`sensehat/show_ip_address.py`](sensehat/show_ip_address.py) |
| Draw a shape (heart, logo…) | [`sensehat/show_shape.py`](sensehat/show_shape.py) |
| Show the time as digits | [`sensehat/binary_clock.py`](sensehat/binary_clock.py) |
| Graph temp/pressure/humidity | [`sensehat/bar_graph.py`](sensehat/bar_graph.py) |
| Rainbow animation | [`sensehat/rainbow.py`](sensehat/rainbow.py) |
| Blank a stuck display | [`sensehat/clear_display.py`](sensehat/clear_display.py) |

### Take pictures

| Task | Recipe |
|---|---|
| One still | [`camera/capture_still.py`](camera/capture_still.py) |
| Timelapse, pruning old files | [`camera/capture_timelapse.py`](camera/capture_timelapse.py) |
| Photograph on motion | [`camera/capture_on_motion.py`](camera/capture_on_motion.py) |

### Talk to the fleet

| Task | Recipe |
|---|---|
| Publish a reading | [`iot/publish_reading.py`](iot/publish_reading.py) |
| Watch readings arrive | [`iot/subscribe_readings.py`](iot/subscribe_readings.py) |
| Act on another Pi's reading | [`iot/subscribe_and_act.py`](iot/subscribe_and_act.py) |

### Everything else

| Task | Recipe |
|---|---|
| How long has this Pi been up | [`system/show_uptime.py`](system/show_uptime.py) |
| Battery endurance log | [`system/log_uptime_to_xlsx.py`](system/log_uptime_to_xlsx.py) |
| This machine's LAN address | [`net/outbound_ip.py`](net/outbound_ip.py) |
| Outside temperature | [`net/fetch_weather.py`](net/fetch_weather.py) |

## Running one

```bash
python3 recipes/gpio/blink_led.py
```

Off a Pi, `tools/dev` supplies a Sense HAT emulator and mock GPIO pins:

```bash
tools/dev python3 recipes/sensehat/read_temperature.py
```

Each recipe's docstring says whether running it off-Pi is meaningful. Some are
not — measuring a capacitor's charge time needs a real capacitor.

## The convention

Every recipe:

- **is one file** that runs with `python3 <file>` and no arguments
- **puts every tunable in `UPPER_CASE` constants** in the first ~15 lines,
  above any logic — that is your edit surface after copying
- **has a docstring** covering what it does, hardware, wiring, how to run it on
  a Pi, how to run it off one, and what to keep when you copy it
- **restores the hardware in a `finally`** — never leave a relay energised
- **imports no other recipe**, so copying one is always safe
- **declares its dependencies** in a `requires:` line, so a project can
  assemble its own `requirements.txt` from the recipes it forked

New recipes use `gpiozero` (BCM numbering). `RPi.GPIO` appears only where the
hardware demands it — the relay board is wired to BOARD pin numbers, and the
light-sensor timing loop needs direct pin control. `gpiozero` is also the
library Raspberry Pi maintains: `RPi.GPIO` does not support the Pi 5's GPIO
chip at all.

## What not to copy

Recipes may import `pihome.display` (shapes, fonts) and `pihome.reading` (the
wire format). **Do not fork those.** The envelope is the contract the web UI
reads, and a forked copy will drift from it. Copy the shape of the code, not
the schema.
