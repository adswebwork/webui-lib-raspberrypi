import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pihome import iot, topics
from pihome.reading import Event, Reading


def test_publish_emits_valid_json_on_the_device_topic():
    client = iot.MockClient()
    iot.publish(client, Reading("temperature", 79, "F", device="sensehat-01"))
    topic, payload = client.published[0]
    assert topic == "home/sensehat-01/telemetry/temperature"
    assert json.loads(payload)["device"] == "sensehat-01"


def test_subscriber_drops_bad_payloads_instead_of_dying():
    """One malformed message from one node must not take down a subscriber."""
    client = iot.MockClient()
    got = []
    iot.subscribe_readings(client, got.append)
    client.deliver("home/sensehat-01/telemetry/temperature", b"{ not json")
    client.deliver("home/sensehat-01/telemetry/temperature",
                   Reading("temperature", 71, "F").to_json())
    assert len(got) == 1 and got[0].value == 71


def test_subscriber_receives_from_any_device():
    client = iot.MockClient()
    got = []
    iot.subscribe_readings(client, got.append)
    for device in ("sensehat-01", "camera-01"):
        client.deliver("home/{}/telemetry/temperature".format(device),
                       Reading("temperature", 70, "F", device=device).to_json())
    assert sorted(r.device for r in got) == ["camera-01", "sensehat-01"]


def test_events_subscriber_also_drops_bad_payloads():
    """bus_monitor used a raw client.subscribe with an unguarded lambda; it is
    the tool you run during a changeover, when bad payloads are likeliest."""
    client = iot.MockClient()
    got = []
    iot.subscribe_events(client, got.append)
    client.deliver("home/sensehat-01/event", b"{ not json")
    client.deliver("home/sensehat-01/event", Event("online", "info", "up").to_json())
    assert len(got) == 1 and got[0].kind == "online"


def test_subscribe_readings_uses_the_shared_topic_builder():
    """The topic was built inline here, duplicating pihome.topics - which is
    the one place that is supposed to know the layout."""
    client = iot.MockClient()
    iot.subscribe_readings(client, lambda r: None, device="fan-01",
                           metric="temperature")
    assert client.subscriptions[0][0] == topics.telemetry("fan-01", "temperature")
