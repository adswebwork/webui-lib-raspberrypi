import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pihome import topics
from pihome.iot import _topic_matches


def test_device_appears_in_the_topic():
    assert topics.telemetry("sensehat-01", "temperature") == \
        "home/sensehat-01/telemetry/temperature"


def test_wildcards():
    assert topics.all_telemetry() == "home/+/telemetry/#"
    assert topics.all_telemetry("temperature") == "home/+/telemetry/temperature"


def test_wildcard_matches_every_device():
    pattern = topics.all_telemetry("temperature")
    for device in ("sensehat-01", "camera-01"):
        assert _topic_matches(pattern, topics.telemetry(device, "temperature"))


def test_hash_matches_deeper_levels():
    assert _topic_matches("home/+/telemetry/#",
                          "home/sensehat-01/telemetry/temperature")


def test_plus_does_not_cross_a_level():
    assert not _topic_matches("home/+/event", "home/sensehat-01/telemetry/x")


def test_one_device_subscription_excludes_others():
    pattern = "home/sensehat-01/telemetry/#"
    assert _topic_matches(pattern, "home/sensehat-01/telemetry/temperature")
    assert not _topic_matches(pattern, "home/camera-01/telemetry/temperature")
