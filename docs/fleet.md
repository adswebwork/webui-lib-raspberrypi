# The fleet

Five Raspberry Pis. The physical inventory is
[`assets/raspberry-pi-inventory.pdf`](assets/raspberry-pi-inventory.pdf):
one on a Touch pHAT, one on a breadboard driving lights and a relay, one Pi 3
with a Sense HAT, one with a camera module, and one spare.

`devices.json` at the repo root is the machine-readable version, and the file a
web UI should read to render a device list before any message arrives.

| Device | Role | Hardware | Credentials | Provisioned |
|---|---|---|---|---|
| `sensehat-01` | telemetry | Sense HAT | `sys1` | yes |
| `mains-01` | actuator | 4 relays, PIR (BOARD pins) | `sys2` | yes |
| `fan-01` | actuator | relay (BCM 26) | `sys2` | yes |
| `camera-01` | camera | Pi camera | `sys4` | **no** |
| `spare-01` | spare | — | — | no |

**The mapping from a physical Pi to a device id is inferred** from what each
script drives. It has not been confirmed against the running hardware — verify
before relying on it.

## Which Pi am I?

Identity is never hard-coded. `pihome.identity.device_id()` checks, in order:

1. `$PIHOME_DEVICE`
2. `/etc/pihome/device` — one line, the right answer on a provisioned Pi
3. hostname matched against `devices.json`
4. the hostname itself

```bash
echo sensehat-01 | sudo tee /etc/pihome/device
```

## Notes

- **`fan-01` authenticates with `sys2`'s certificate.** Long-standing; recorded
  in `devices.json` as data rather than hidden in a call.
- **`camera-01` has never run.** The old `sys4.py` referenced a variable that
  was never defined, so it crashed on import, and no credentials exist for it.
