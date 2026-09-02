# Projects

Real deployments. Each one owns its code and its configuration, and is free to
diverge from whatever it was copied from.

| Project | What it is |
|---|---|
| [`home-telemetry`](home-telemetry/) | The original four-Pi fleet: temperature in, fan out |
| [`dog-camera-monitor`](dog-camera-monitor/) | Kennel camera, climate, alerts. The worked example |
| [`phoenix-doghouse`](phoenix-doghouse/) | Food, water and climate control for the dog house |
| [`_template`](_template/) | Empty scaffold for a new project |

## These three projects share the same Pis — run one at a time

They are not three systems. They are three deployments of the same four
machines, so **only one may be running against the fleet at any moment.**

| Physical device | `home-telemetry` | `dog-camera-monitor` | `phoenix-doghouse` |
|---|---|---|---|
| `sensehat-01` | `sensehat_node` | `kennel_node` | `climate_node` |
| `mains-01` | `mains_node` | — | `sustenance_node`, `status_node` |
| `fan-01` (GPIO 26) | `fan_node` | `alert_node` | — |
| `camera-01` | `camera_node` | `camera_node` | `camera_node` |

Run two at once and you get two processes contending for GPIO 26, two fan
controllers with different thresholds fighting over the same relay, and one
device publishing `temperature` under two different meanings.

Every actuator therefore names the single device it listens to
(`source_device` in `config.json`) rather than subscribing to `home/+/`. A fan
switching mains voltage should answer to a named Pi, not to whatever happens to
be on the bus. If you genuinely need two of these running together, give them
separate sites (`PIHOME_SITE`) so their topics cannot collide, and separate
relays.

## Starting a new one

```bash
cp -r projects/_template projects/my-project
cd projects/my-project
```

Then:

1. **Find the recipes you need** — [`recipes/README.md`](../recipes/README.md)
   is indexed by task.
2. **Copy them into `lib/`** and edit freely. Rename them for what they do
   *here*, not what they did in the recipe.
3. **Write a node** per physical Pi, in `nodes/`. Name it for its role.
4. **Put every tunable in `config.json`.** Pins, thresholds, intervals,
   message strings. Start `main()` with `identity.assume(SETTINGS["device"])`
   so the node declares which Pi it is meant to be — a mismatch against
   `/etc/pihome/device` is then logged instead of silently misfiling readings.
5. **Import from `pihome`** for anything that crosses the device boundary —
   `iot`, `reading`, `display`, `config`. Never fork those.
6. **Add a service unit** so it restarts after a power cut.

## The rule

**Copy from `recipes/`. Import from `pihome/`.**

A recipe is a starting point; forking one is the point. `pihome` is the
contract — the wire format, the topic layout, the device registry — and
forking it means one Pi quietly disagreeing with the rest of the fleet.
