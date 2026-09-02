#!/usr/bin/env python3
"""Announce this Pi on boot: who it is and where it is on the network.

Formerly _globalConfig/onready.py, which wrote to a text file in the repo.
Now it publishes, so the information is visible off-device.

    python3 nodes/register_node.py
"""
from pihome import identity, iot, log, uptime
from pihome.reading import Reading

logger = log.get_logger("register_node")


def main():
    device = identity.device_id()
    address = identity.outbound_ip()
    logger.info("registering %s at %s", device, address)

    client = iot.connect()
    try:
        iot.publish_event(client, "online", "{} booted".format(device),
                          hostname=identity.hostname())
        iot.publish(client, Reading("ip_address", address, "text"))
        try:
            iot.publish(client, Reading("uptime", uptime.uptime_seconds(), "s"))
        except OSError:
            pass          # no /proc/uptime off Linux; not worth failing boot for
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
