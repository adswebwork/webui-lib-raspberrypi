#!/usr/bin/env python3
"""Watch everything on the bus. A diagnostic, not a deployed node.

Subscribes to every device's telemetry and events, plus the pre-schema topics,
and prints what arrives. Run it on a laptop while changing the fleet over.

    python3 nodes/bus_monitor.py
"""
import time

from pihome import iot, log, topics

logger = log.get_logger("bus_monitor")


def show(item):
    if hasattr(item, "metric"):
        print("{}  {:10s} {:12s} {:>8} {}".format(
            item.ts, item.device, item.metric, item.value, item.unit))
    else:
        print("{}  {:10s} {:12s} {}".format(
            item.ts, item.device, item.kind, item.message))


def main():
    client = iot.connect()
    try:
        iot.subscribe_readings(client, show)
        # Via pihome rather than a raw client.subscribe with a lambda, which
        # had no error handling: this is the tool you run *during* a changeover,
        # exactly when half-migrated nodes are emitting payloads that will not
        # parse, and it must not fall over on the first one.
        iot.subscribe_events(client, show)
        logger.info("watching %s and %s",
                    topics.all_telemetry(), topics.all_events())
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
