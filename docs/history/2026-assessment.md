# Codebase Assessment

*September 2026. Last substantive commit before this pass: December 2022.*

## What this is

A five-Pi home automation fleet built up over several years. Three distinct
projects share one repository:

1. **The `sysN` fleet** (`_globalConfig/`) — the newest and most coherent layer.
   Four Pis publish to and subscribe from AWS IoT Core over MQTT. sys1 reports
   Sense HAT temperature; sys3 subscribes to that topic and switches a fan when
   it crosses a threshold. That closed loop is the most interesting thing here.
2. **SmartHouse / "Phoenix"** (`smarthouse/automation/`) — an automated dog
   house: food and water dispensing, climate control, kennel occupancy, image
   capture. GPIO-driven, no networking. Feels like the older project.
3. **Loose experiments** (root, `pi3/`, `_ideas/`, `_archive/`) — single-purpose
   scripts for buzzers, light sensors, relays, cameras.

446 tracked files, 104 Python files — 49 of them under `_archive/`. 312 commits.

## Current state

**Structurally sound idea, thin execution.** The pub/sub design is right: nodes
are decoupled, the topic namespace (`home/temperature`, `network/message`,
`registration/ipaddress`, `security/sensors`) is sensible, and offline publish
queueing is configured so a node that drops off the network catches up. What's
missing is everything around it — no error handling, no tests, no dependency
manifest, no service supervision, no logging beyond `print`.

**Every script is a top-level program.** Configuration, hardware setup, network
connection, and the main loop all execute at import time. Nothing is callable,
nothing is importable without side effects, and nothing can be tested off a Pi.

**Copy-paste was the reuse mechanism.** Before this pass, the twenty-line
`AWSIoTMQTTClient` setup block appeared verbatim in seven files, and
`sensehat_config.py` existed as three byte-identical copies.

### What was actually broken

Found by reading, then confirmed by syntax check and static analysis:

| Issue | Where | Effect |
|---|---|---|
| Device private keys committed | 5 nodes, 19 files | Anyone with repo access can impersonate any node |
| `checkThreshold()` overwrote its own result | `sensehat_config.py` | Hot never displayed red — second assignment clobbered the first |
| `GPIO.setmode(BCM)` with BOARD pin numbers | `sys2.py` | Crashes on setup; pins 31–40 don't exist in BCM |
| `vars.sys4ca` never defined | `sys4.py` | `AttributeError` on startup — camera node has never run |
| `GPIO.cleanup()` inside the blink loop | `security.py` | Resets pin config every iteration, so the next write fails |
| String + int concatenation | `sys1.py`, `security.py` | `TypeError` on the first log line |
| CRLF line endings on shebang scripts | `_autostart/bootup.sh` + 8 more | `bad interpreter: /bin/bash^M` — **boot registration never ran** |
| `#!/usr/bin/python` | 5 files | Python 2 is gone on Raspberry Pi OS Bookworm |
| Python 2 syntax | 4 live files | `SyntaxError` — cannot run at all |
| `0600` and a bare email address as literals | `smarthouse/automation/db.py` | Module was never importable |
| Imports of names `settings.py` never defined | `flush.py` | `ImportError` |
| Undefined `pictureLed` | `routines.py` | `NameError` when that routine is called |
| JSON built by string concatenation | 7 files | Any quote or newline in a value produces a malformed payload |
| Payload `json.dumps`'d then `json.loads`'d | `ei_aws_publish.py` | Published a quoted string, not an object |
| Shell aliases via `os.system` / `subprocess` | `gitupdate.py`, `pictures.py` | Aliases don't exist in a non-interactive shell |
| `uptime` referenced before assignment | `runtime.py` | `NameError` if interrupted in the first 5 seconds |
| Paths relative to cwd, hard-coded `/home/pi` | several | Breaks unless launched from exactly the right directory |

## What I changed

**Security.** Untracked all 19 device certificate and key files (they stay on
disk, `.gitignore` now blocks them) and untracked 13 committed `.pyc` files.
The public Amazon root CAs stay tracked — those are meant to be public.

**A shared IoT layer.** New `_globalConfig/iot.py` with `connect(system)` and
`send(client, topic, key, value)`. `vars.py` gained `certs_for(system)`,
replacing the hand-maintained `sys1ca`/`sys1private`/`sys1cert` triples — which
is why sys4 was broken, since nobody added its set. `vars.rootUrl` now resolves
from `__file__` instead of assuming `/home/pi/raspberrypi`. Payloads go through
`json.dumps`. sys1–sys4, `aws-temperature.py`, and `awsiotcore.py` all sit on
this now, and each disconnects cleanly on exit.

**Bug fixes.** Every row in the table above. The `checkThreshold` fix also
corrects the temperature conversion, which was `×1.8 + 12` — the constant is
now written as the real C-to-F conversion minus a named 20°F self-heating
offset, which is what that 12 was standing in for. Same arithmetic, legible.

**Line endings.** Added `.gitattributes` (`* text=auto eol=lf`) and set
`core.autocrlf=input` for this repo. Your global `core.autocrlf=true` is what
introduced CRLF into a repo that only ever deploys to Linux.

**Deletions.** `aws-light.py` and `aws-temperature.py` at root (duplicates of
`light_fan.py` and `temperature.py` — verified identical modulo whitespace),
`_globalConfig/aws-control.py` (duplicate of `sys3.py`),
`smarthouse/automation/system4-initialize.py` (broken Python 2 twin of
`system4_initialize.py`), and `settings.py` / `pi3/settings.py` (two unused
imports each, nothing referenced them).

**Added.** `requirements.txt`, `README.md`, and this file.

All live Python now parses under Python 3, and `ruff` reports no undefined
names and no unused imports outside `_archive/`.

### Left alone deliberately

- **`_archive/`** — 49 Python-2 files. It's an archive; leave it as one.
- **The busy-wait loops** in `trigger.py`, `motion.py`, `noisetrigger.py`. They
  look like a CPU-burning bug but they aren't — counting iterations until a pin
  goes high *is* the measurement, the standard RC-charge-time trick for reading
  an analogue light sensor without an ADC. Replacing them would break them.
- **`sys2.py`'s `led3 = 35`**, which collides with `relay3`, and
  **`smarthouse/automation/settings.py`'s `waterLed = 35`**, which collides with
  `buzzerControl`. Both need a look at the actual board; I left `led3` unset
  with a `TODO` rather than guess a pin.
- **`vars.py` as a module name** shadows the `vars()` builtin. Renaming touches
  every import; worth doing, but not silently.

## Two things that need you

**1. Rotate the AWS IoT credentials.** Untracking them fixes the future, not the
past — the keys are still in all 312 commits, and the repo has been pushed. It's
private, which limits the exposure, but the certificates don't expire until 2049
and a leaked device key means anyone can publish to your topics or impersonate a
node. In the AWS IoT console: deactivate and delete the certificates for sys0,
sys1, sys2, and pi3, issue new ones, `scp` them to each Pi. History rewriting is
optional after that; rotation is not.

**2. Provision sys4.** The camera node has never connected — there's no
`_globalConfig/_sys4/` directory. It needs its own AWS IoT thing and certs.

Also worth knowing: `smarthouse/automation/demo.jpg` is a 4.2 MB image committed
into a repo that clones onto SD cards, and 26 non-archive files still have CRLF
endings. `git add --renormalize .` fixes the latter in one pass now that
`.gitattributes` exists — I held off because a 26-file whitespace diff would
have buried the actual changes.

---

# Where I'd take it

Four steps, each independently useful. Nothing here requires doing all of it.

## 1. Make it survive a reboot

The highest-value change and the smallest. Right now nothing restarts if a
script crashes or a Pi reboots, and `@reboot` cron gives you no logs and no
restart policy.

Write one systemd unit per node:

```ini
[Unit]
Description=Pi telemetry (sys1)
After=network-online.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/raspberrypi/_globalConfig/sys1.py
Restart=always
RestartSec=10
User=pi

[Install]
WantedBy=multi-user.target
```

`journalctl -u sys1 -f` then gives you the logs you currently only see by
SSH-ing in and watching stdout. Pair it with swapping `print` for the `logging`
module — same output on the console, but timestamped, levelled, and greppable.

## 2. One program, not four

sys1–sys4 are the same program with different hardware attached. Collapse them
into a single entry point driven by config:

```
raspberry_fleet/
  __init__.py
  config.py          # dataclass, loaded from a per-node TOML file
  iot.py             # already exists, keep it
  sensors/           # sensehat.py, motion.py, camera.py
  actuators/         # relay.py, fan.py
  nodes/             # what each role does, as functions
  __main__.py        # python3 -m raspberry_fleet --node sys1
```

The win isn't tidiness, it's that node identity, credentials, and pin
assignments stop being scattered across four files that drift apart. A node
becomes a TOML file:

```toml
[node]
name = "sys1"
role = "sensehat"

[gpio]
mode = "BOARD"

[thresholds]
ideal_temp_f = 80
```

Secrets stay out of it — credentials continue to live in `_sysN/`, referenced by
path.

## 3. Make it testable off the Pi

The blocker is that `import RPi.GPIO` fails on anything that isn't a Pi, so you
cannot run a single line of this on your laptop. Two options, and I'd take the
second:

- Stub `RPi.GPIO` and `sense_hat` in `conftest.py` with `unittest.mock`.
- **Move to `gpiozero`.** It has a built-in mock pin factory
  (`GPIOZERO_PIN_FACTORY=mock`), so the same code runs on a laptop under pytest
  and on a Pi unchanged. It's also the library Raspberry Pi actually maintains —
  `RPi.GPIO` doesn't support the Pi 5's new GPIO chip at all, so this is a
  hardware-compatibility question as much as a testing one.

`gpiozero` also removes most of the pin bookkeeping that's causing bugs here:

```python
from gpiozero import LED, MotionSensor

fan = LED(26)
pir = MotionSensor(4)
pir.when_motion = fan.on          # replaces the whole poll loop
```

The BCM-versus-BOARD confusion that breaks `sys2.py` simply doesn't exist in
gpiozero — it's BCM everywhere, always.

## 4. Modernise the platform

- **`picamera` → `picamera2`.** The legacy stack was removed in Bullseye; both
  camera scripts here are written against an API that no longer exists.
  `raspistill` is gone too, replaced by `libcamera-still` (already updated in
  `pi3/dev/pictures.py`).
- **`AWSIoTPythonSDK` → `awsiotsdk` (v2).** V1 is in maintenance mode. V2 is
  async, supports MQTT 5, and handles reconnection properly.
- **Pin the dependencies.** `requirements.txt` currently lists names, not
  versions. Once it works, freeze it — SD cards get reflashed and you want the
  same versions back.
- **Ruff in CI.** One GitHub Actions job running `ruff check` catches the entire
  class of bug that dominated this pass — undefined names, Python 2 leftovers,
  broken imports — before it ships to a device you have to walk over to.

## What I'd do first

Rotate the credentials. Then systemd units, because "did it come back after the
power blip" is the question that actually matters for hardware in a house. Then
gpiozero, because it makes everything after it testable.

The consolidation in step 2 is the most satisfying but the least urgent — the
code works or doesn't work per-node, and four nodes is few enough that the
duplication isn't yet the thing hurting you.
