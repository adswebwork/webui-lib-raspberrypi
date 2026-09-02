# home-telemetry

The original four-Pi fleet. One node reads temperature, another switches a fan
when it climbs — the closed loop this whole message bus exists for.

Formerly `_globalConfig/sys1.py` … `sys4.py`.

## Nodes

| Node | Device | Runs on | What it does |
|---|---|---|---|
| `sensehat_node` | `sensehat-01` | Pi 3 + Sense HAT | Publishes temperature, humidity, pressure |
| `mains_node` | `mains-01` | Pi + relay board | Four relay channels, PIR motion |
| `fan_node` | `fan-01` | Pi + relay | Subscribes to temperature, switches the fan |
| `camera_node` | `camera-01` | Pi + camera | Captures stills — **not yet provisioned** |
| `register_node` | any | any | Announces the Pi on boot |
| `bus_monitor` | — | a laptop | Diagnostic: prints everything on the bus |

## Running

```bash
PYTHONPATH=/home/pi/raspberrypi python3 nodes/sensehat_node.py
```

As a service, which is what you actually want:

```bash
sudo ../../tools/install-service.sh home-telemetry sensehat_node
journalctl -u home-telemetry@sensehat_node -f
```

## Which Pi am I?

A node never hard-codes its identity. It asks `pihome.identity`, which checks
`$PIHOME_DEVICE`, then `/etc/pihome/device`, then the hostname against
`devices.json`. Provision a Pi with:

```bash
echo sensehat-01 | sudo tee /etc/pihome/device
```

## Bringing the fleet up

Every Pi is a clean Raspberry Pi OS install, so there is no changeover: nothing
has ever run the pre-v1 flat topics, and the code that bridged them has been
removed. Nodes publish and read the envelope only.

Bring them up in this order, the consumer last so it is never subscribed to a
topic nobody is publishing:

1. `sensehat-01` (publisher)
2. `mains-01`
3. `camera-01`
4. `fan-01` (consumer)

## Known

- **`camera-01` has never run.** Its predecessor script referenced
  `vars.sys4ca`, which was never defined, so it crashed on import.
- **No device is provisioned.** The fleet is being stood up on a new AWS
  account; see [`../../docs/aws-iot.md`](../../docs/aws-iot.md).
- **`mains_node` uses BOARD pin numbering**, unlike the rest. Its relay board
  is wired that way. A third LED was assigned to pin 35, which relay3 already
  claims — unresolved, see `docs/pinmap.md`.
