# webui-lib-raspberrypi

Scripts for a five-Pi home automation fleet, organised so that starting a new
project means copying known-good code rather than remembering where the last
one lived.

> **No AWS account is attached.** The account this fleet previously used is
> gone, and its certificates with it. Nothing connects until an endpoint,
> policy, thing and certificate exist — see [`docs/aws-iot.md`](docs/aws-iot.md).
> This repository has a clean history and CI runs `gitleaks` on every push, so
> no credential has ever been committed here.

```
recipes/     copy from here   single-file scripts, one per hardware task
pihome/      import from here shared core: wire format, MQTT, display, identity
projects/    real deployments each owns its code and config
schema/      the contract      JSON Schema the web UI reads
```

**Copy from `recipes/`. Import from `pihome/`.** A recipe is a starting point
and forking one is the point. `pihome` is the contract — fork it and one Pi
quietly disagrees with the rest of the fleet.

## Starting something new

```bash
cp -r projects/_template projects/my-project
```

Then find what you need in [`recipes/README.md`](recipes/README.md), which is
indexed by task — *"I want to photograph on motion → `camera/capture_on_motion.py`"*.
Copy those files into `projects/my-project/lib/` and edit them freely.

[`projects/dog-camera-monitor/`](projects/dog-camera-monitor/) is the worked
example, and its README shows which recipe each file came from and what changed.

## The fleet

Five Pis: one on a Touch pHAT, one on a breadboard with lights and a relay, one
Pi 3 with a Sense HAT, one with a camera, one spare. See
[`docs/fleet.md`](docs/fleet.md) and `devices.json`.

| Project | What it does |
|---|---|
| [`home-telemetry`](projects/home-telemetry/) | The original fleet: temperature in, fan out |
| [`dog-camera-monitor`](projects/dog-camera-monitor/) | Kennel camera, climate, alerts |
| [`phoenix-doghouse`](projects/phoenix-doghouse/) | Food, water and climate control |

## Setup on a Pi

Assumes a fresh Raspberry Pi OS install.

```bash
sudo apt update
sudo apt install -y git python3-pip

# Hardware libraries come from apt, not pip: they are built against the system
# libraries, and picamera2 in particular does not install cleanly from PyPI.
# Install only what THIS node has attached.
sudo apt install -y python3-sense-hat        # sensehat-01
sudo apt install -y python3-gpiozero         # fan-01, and anything with a relay
sudo apt install -y python3-rpi.gpio         # mains-01 - BOARD numbering (see note)
sudo apt install -y python3-picamera2        # camera-01

# The AWS IoT SDK is not packaged for apt. Raspberry Pi OS Bookworm marks the
# system Python as externally managed (PEP 668), so pip needs to be told:
pip3 install --break-system-packages AWSIoTPythonSDK

git clone https://github.com/adswebwork/webui-lib-raspberrypi.git
cd webui-lib-raspberrypi

# Tell the Pi which node it is. mkdir first - tee will not create the
# directory, and without it this prints the name, reports an error that is
# easy to miss, and creates nothing. The node then falls back to its hostname
# and publishes under the wrong device.
sudo mkdir -p /etc/pihome
echo sensehat-01 | sudo tee /etc/pihome/device
cat /etc/pihome/device                       # confirm it is actually there
```

`pihome` itself does not need installing: it has no dependencies of its own,
and the service unit puts the repository on `PYTHONPATH`. `pip3 install
--break-system-packages -e .` is still useful if you want `import pihome` to
work from an interactive shell.

Provision that node's AWS IoT credentials into `secrets/<name>/` — see
[`secrets/README.md`](secrets/README.md) — then install the service:

```bash
sudo tools/install-service.sh home-telemetry sensehat_node
journalctl -u home-telemetry@sensehat_node -f
```

Check it before walking away:

```bash
systemctl is-active home-telemetry@sensehat_node
python3 -c "import sys; sys.path.insert(0,'.'); from pihome import identity; print(identity.device_id())"
```

That last line must print the device id you wrote to `/etc/pihome/device`. If
it prints a hostname instead, the file is missing and readings will be filed
under the wrong device.

**Note on `python3-rpi.gpio`:** only `mains_node` needs it, for BOARD (physical
header) numbering. It does not work on a Pi 5 — use `python3-rpi-lgpio`, which
is a drop-in replacement, if that node ever moves to one.

## Working without a Pi

```bash
tools/dev python3 recipes/sensehat/read_temperature.py
python3 -m pytest tests/ -q
```

`tools/dev` supplies a Sense HAT emulator and mock GPIO pins. See
[`docs/off-pi-dev.md`](docs/off-pi-dev.md).

## What devices send

Every message is a `Reading` or an `Event`, defined once in
[`pihome/reading.py`](pihome/reading.py) and published as JSON Schema in
[`schema/`](schema/).

```json
{"v": 1, "site": "home", "device": "sensehat-01", "metric": "temperature",
 "value": 79, "unit": "F", "ts": "2026-09-01T18:22:03.412Z",
 "seq": 412, "boot_id": "9f2c1e", "tags": {"room": "office"}}
```

The device is in the payload *and* the topic
(`home/<device>/telemetry/<metric>`), so a consumer can subscribe to one Pi and
always knows where a reading came from. See [`schema/topics.md`](schema/topics.md).

## Before you rely on this

- **Stand up the AWS account.** No endpoint, policy or certificate exists yet; the fleet cannot publish until they do. See [`docs/aws-iot.md`](docs/aws-iot.md).
- **`camera-01` has never run** — it has no credentials.
- **BOARD pin 35 is claimed twice.** See [`docs/pinmap.md`](docs/pinmap.md).

[`docs/history/2026-assessment.md`](docs/history/2026-assessment.md) records
what this looked like before, and why it changed.
