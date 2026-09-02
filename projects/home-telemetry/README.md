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

## Changeover

`fan_node` currently subscribes to **both** the new envelope and the old flat
`home/temperature` topic, so it keeps working whichever a publisher is using.
`pihome.iot` likewise mirrors every reading onto the old topic.

Once every node publishes and reads the envelope, set `PIHOME_LEGACY_MIRROR=0`
and drop `subscribe_legacy` from `fan_node`.

Cut over in this order — the consumer last, so it is never reading a topic
nobody is publishing:

1. `sensehat-01` (publisher)
2. `mains-01`
3. `camera-01`
4. `fan-01` (consumer) — then turn the mirror off

## Known

- **`camera-01` has never run.** No `secrets/sys4/` credential set exists. The
  old `sys4.py` referenced `vars.sys4ca`, which was never defined, so it
  crashed on import.
- **`fan-01` authenticates with `sys2`'s certificate.** Long-standing; recorded
  in `devices.json` rather than left as a surprise in the code.
- **`mains_node` uses BOARD pin numbering**, unlike the rest. Its relay board
  is wired that way. A third LED was assigned to pin 35, which relay3 already
  claims — unresolved, see `docs/pinmap.md`.
