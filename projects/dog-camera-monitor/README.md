# dog-camera-monitor

Watches the kennel: photographs it when something moves, reports the
temperature where the dog actually is, and runs a fan if it gets too warm.

Built by copying recipes and editing them. This is the reference for how a
project is put together.

## Nodes

| Node | Device | Hardware | What it does |
|---|---|---|---|
| `camera_node` | `camera-01` | Pi camera + PIR | Photographs on motion and on a schedule |
| `kennel_node` | `sensehat-01` | Sense HAT | Publishes kennel temperature |
| `alert_node` | `fan-01` | Relay | Runs the fan when it gets too warm |

## Running

```bash
PYTHONPATH=/home/pi/raspberrypi python3 nodes/kennel_node.py
```

As a service:

```bash
sudo cp service/dog-camera-monitor@.service /etc/systemd/system/
sudo systemctl enable --now dog-camera-monitor@kennel_node
journalctl -u dog-camera-monitor@kennel_node -f
```

## How this was built

| File | Copied from | What changed |
|---|---|---|
| `lib/capture.py` | `recipes/camera/capture_still.py` | Added pruning — the camera runs unattended and a full SD card stops the Pi writing at all |
| `lib/climate.py` | `recipes/sensehat/read_temperature.py` | Returns a *state* against the animal's safe range, not a colour |
| `lib/motion.py` | `recipes/gpio/read_pir.py` | Added a cooldown — one dog crossing the kennel should make one photo, not forty |

Those three are forked. Edit them freely; nothing propagates back.

**Not copied, imported:** `pihome.iot`, `pihome.reading`, `pihome.display`,
`pihome.config`. The envelope is the contract the web UI reads — a forked copy
would drift from it.

## Configuration

Everything tunable is in `config.json` — thresholds, intervals, pins, the
messages each alert carries. Nothing about *which Pi this is* lives there;
that comes from `pihome.identity`.

```bash
echo camera-01 | sudo tee /etc/pihome/device
```

## Before this runs

**`camera-01` is not provisioned.** It has no AWS IoT credentials — see
`secrets/README.md`. This project is a new deployment, not a migration: the
old `sys4.py` never ran.
