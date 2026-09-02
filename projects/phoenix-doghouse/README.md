# phoenix-doghouse

Food, water and climate control for a dog house, built for a dog named Phoenix.
The oldest project here — it predates the message bus, and has been brought
onto it.

Was `smarthouse/automation/`.

## Nodes

| Node | Device | What it does |
|---|---|---|
| `climate_node` | `sensehat-01` | Reads kennel temperature, drives heat/cool, publishes |
| `sustenance_node` | `mains-01` | Food and water relays, dispensing servo |
| `status_node` | `mains-01` | Blinks the status LED so you can see it is alive |
| `camera_node` | `camera-01` | Kennel stills — **needs provisioning** |

## Running

```bash
PYTHONPATH=/home/pi/raspberrypi python3 nodes/climate_node.py
```

## What changed in the migration

The original had **eleven** `system{1..4}_{initialize,register}.py` files that
were the same five-line template with different labels. They collapse to the
four nodes above.

Two were outright broken:

- `system4_initialize.py` was a byte-for-byte copy of `system2_initialize.py`,
  including `sysNum = '2'` — so system 4 logged itself as system 2.
- `system4_register.py` ran `os.system("source ~/.bashrc && pwd && msg")`,
  reaching for a shell alias a non-interactive shell never sees, then printed
  the exit code as though it had worked.

`settings.py` split: the pin map became [`pins.py`](pins.py), the animal
profile and thresholds became `config.json`, and the logging helpers were
dropped in favour of `pihome.log` (they wrote to a hard-coded
`/home/pi/raspberrypi/...` path and produced an unparseable run-together log).

`routines.py` became [`lib/controls.py`](lib/controls.py). **`add_water()`'s
PWM duty ramp is preserved exactly** — those numbers are calibrated against the
real servo and load.

`senseHatRoutines.py` became [`lib/display.py`](lib/display.py), with the bar
rendering moved into `pihome.display` so it is testable without hardware.

## Known

- **BOARD pin 35 is claimed twice.** The original assigned it to both
  `buzzerControl` and `waterLed`. `WATER_LED` is commented out in `pins.py`
  rather than guessed at — trace it on the board. See `docs/pinmap.md`.
- **This project uses BOARD numbering**, unlike most of the repo. Its relay
  board is wired that way.
- **`camera-01` is not provisioned.** See `secrets/README.md`.
