# MQTT topics

The device is in the topic, not only the payload. That is what lets a consumer
subscribe to a single Pi, and what lets an AWS IoT rule route by device without
parsing the body.

| Topic | Direction | Payload |
|---|---|---|
| `home/<device>/telemetry/<metric>` | device → cloud | [Reading](reading.schema.json) |
| `home/<device>/event`              | device → cloud | [Event](event.schema.json) |
| `home/<device>/cmd`                | cloud → device | reserved for the web UI |

Wildcards a consumer will want:

- `home/+/telemetry/#` — every reading from every device
- `home/+/telemetry/temperature` — one metric across the fleet
- `home/sensehat-01/telemetry/#` — everything from one device
- `home/+/event` — all events

## Routing to storage

`SELECT * FROM 'home/+/telemetry/#'` lands in a table partitioned on `device`
and sorted on `ts` — the query shape a device dashboard needs. The old flat
`home/temperature` topic could express no such rule.

## Legacy topics

Pre-v1, and still mirrored while the fleet changes over. Retire once every node
reads the envelope (`PIHOME_LEGACY_MIRROR=0`).

| Topic | Old payload | Problem |
|---|---|---|
| `home/temperature` | `{"temp": "79"}` | no device, no time, no unit; more than one Pi published it |
| `network/message` | `{"message": "..."}` | superseded by Event |
| `registration/ipaddress` | `{"ipaddress": "..."}` | superseded by Reading `ip_address` |
| `security/sensors` | `{"sensor": "..."}` | superseded by Event `motion` |
