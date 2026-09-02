"""MQTT topic construction.

The device goes in the topic, not just the payload. That is what lets a
consumer subscribe to one Pi, and what lets an AWS IoT rule route by device
without parsing the body. The old flat `home/temperature` could express
neither: two different Pis published to it indistinguishably.
"""
from pihome import identity


def _site():
    return identity.site()


def telemetry(device, metric):
    """home/<device>/telemetry/<metric>"""
    return "{}/{}/telemetry/{}".format(_site(), device, metric)


def events(device):
    """home/<device>/event"""
    return "{}/{}/event".format(_site(), device)


def commands(device):
    """home/<device>/cmd - inbound, for a future web UI to drive a device."""
    return "{}/{}/cmd".format(_site(), device)


def all_telemetry(metric="#"):
    """Every device's telemetry, for a dashboard or the bus monitor."""
    return "{}/+/telemetry/{}".format(_site(), metric)


def all_events():
    return "{}/+/event".format(_site())
