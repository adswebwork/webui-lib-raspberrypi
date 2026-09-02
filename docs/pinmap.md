# Pin numbering

Two schemes are in use, because the hardware is wired two ways. **Do not
silently renumber anything** — the numbers match physical wiring that is not
visible from the code.

| Scheme | Means | Used by |
|---|---|---|
| **BCM** | Broadcom GPIO line number | Everything new, all `gpiozero` recipes |
| **BOARD** | Physical position on the 40-pin header | The relay board, `mains_node`, `phoenix-doghouse` |

`gpiozero` is BCM-only, which is one reason new work uses it: the BCM/BOARD
confusion cannot arise.

## Conversion

| BOARD | BCM | | BOARD | BCM |
|---|---|---|---|---|
| 3 | 2 | | 23 | 11 |
| 5 | 3 | | 24 | 8 |
| 7 | 4 | | 26 | 7 |
| 8 | 14 | | 29 | 5 |
| 10 | 15 | | 31 | 6 |
| 11 | 17 | | 32 | 12 |
| 12 | 18 | | 33 | 13 |
| 13 | 27 | | 35 | 19 |
| 15 | 22 | | 36 | 16 |
| 16 | 23 | | 37 | 26 |
| 18 | 24 | | 38 | 20 |
| 19 | 10 | | 40 | 21 |
| 21 | 9 | | | |

A full pinout diagram is at [`assets/gpio-header.png`](assets/gpio-header.png).

## Open hardware questions

These are conflicts in the original code that cannot be resolved without
looking at the physical boards. Both are recorded rather than guessed at.

### BOARD 35 is claimed twice, in two different projects

- `home-telemetry/nodes/mains_node.py` — a third status LED was assigned to 35,
  which `relay3` already uses. The LED is left unconfigured with a `TODO`.
- `phoenix-doghouse/pins.py` — `buzzerControl = 35` and `waterLed = 35`.

Two independent files disagree about what physical pin 35 drives. Trace it on
the board before enabling either.

### BCM 26 vs BOARD 37

`fan_node` drives BCM 26, which is BOARD 37. `phoenix-doghouse` uses BOARD 37
for `motion`. If those ever run on the same Pi they will fight. They currently
do not.
