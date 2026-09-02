# Working without a Pi

Nothing in this repo used to run on a laptop — every script did
`import RPi.GPIO` or `from sense_hat import SenseHat` at module scope, which
raises anywhere else. That is fixed.

## Setup

```bash
pip3 install -e ".[dev]"
```

On Raspberry Pi OS Bookworm that hits PEP 668
(`error: externally-managed-environment`). Either use a virtualenv:

```bash
python3 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"
```

or, if you accept the risk of mixing with apt-managed packages:

```bash
pip3 install -e ".[dev]" --break-system-packages
```

## Running a recipe on your machine

```bash
tools/dev python3 recipes/sensehat/read_temperature.py
```

`tools/dev` does three things:

- puts `tools/devshim/` on `PYTHONPATH`, where a stub `sense_hat` module
  shadows the real one and re-exports `sense_emu`
- sets `GPIOZERO_PIN_FACTORY=mock`
- sets `PIHOME_DEVICE=dev-local`

The shim is why recipes still say `from sense_hat import SenseHat` — they stay
plain Pi code with no trace of this repo's tooling, so copying one onto a Pi
or into another project just works.

For the Sense HAT emulator's GUI (sliders for temperature, humidity, the
joystick):

```bash
sense_emu_gui
```

## What does not work off-Pi

- **`recipes/gpio/read_light_sensor.py`** and `sensor_triggers_output.py` —
  they measure how long a real capacitor takes to charge. Mock pins return
  instantly.
- **`recipes/gpio/servo_ramp.py`** — `RPi.GPIO` has no mock backend, and PWM
  timing is real.
- **Anything using the camera** — there is no camera.

Each recipe's docstring says which category it is in.

## Tests

```bash
python3 -m pytest tests/ -q
```

Passing with no Pi, no AWS account and no certificate. The GPIO recipe tests
skip if `gpiozero` is not installed rather than failing.

`pihome.iot.MockClient` stands in for the AWS client and records what was
published, so the whole publish path is exercised offline.
