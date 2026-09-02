"""The wire format. These run on any machine - no Pi, no AWS, no certificate."""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pihome.reading import Event, Reading, from_json


def test_reading_roundtrips():
    original = Reading("temperature", 79, "F", tags={"room": "office"})
    assert from_json(original.to_json()) == original


def test_event_roundtrips():
    original = Event("online", "info", "node up")
    assert from_json(original.to_json()) == original


def test_identity_is_filled_in_automatically():
    """A node script cannot forget to say who it is."""
    r = Reading("temperature", 79, "F")
    assert r.device == "test-01"
    assert r.site and r.ts.endswith("Z") and r.boot_id


def test_value_stays_a_number():
    """The old format stringified everything, forcing consumers to re-parse."""
    payload = json.loads(Reading("temperature", 79, "F").to_json())
    assert payload["value"] == 79
    assert isinstance(payload["value"], (int, float))
    assert not isinstance(payload["value"], str)


def test_boolean_values_survive():
    payload = json.loads(Reading("motion", True, "bool").to_json())
    assert payload["value"] is True


def test_seq_is_monotonic():
    """Ordering must hold even when a clock-less Pi's timestamp jumps."""
    a, b = Reading("temperature", 1, "F"), Reading("temperature", 2, "F")
    assert b.seq > a.seq


def test_two_devices_are_distinguishable():
    """The whole point: the old {"temp": "79"} could not express this."""
    a = Reading("temperature", 79, "F", device="sensehat-01")
    b = Reading("temperature", 79, "F", device="camera-01")
    assert a.topic() != b.topic()
    assert json.loads(a.to_json())["device"] != json.loads(b.to_json())["device"]


def test_quotes_and_newlines_survive():
    text = 'fan "on"\nline two'
    assert from_json(Event("error", "warn", text).to_json()).message == text


@pytest.mark.parametrize("payload", [
    "not json", "[1, 2]", "null", '{"metric": "temperature"}', '{"kind": "online"}',
])
def test_malformed_payloads_raise(payload):
    """A silently-wrong reading is worse than a crash."""
    with pytest.raises(ValueError):
        from_json(payload)


def test_unknown_fields_are_ignored_not_fatal():
    """A newer device sending an extra field must not break an older reader."""
    payload = json.loads(Reading("temperature", 79, "F").to_json())
    payload["future_field"] = "whatever"
    assert from_json(json.dumps(payload)).metric == "temperature"


def test_examples_match_the_schema_shape():
    """The committed examples must stay parseable by the code."""
    here = os.path.dirname(os.path.abspath(__file__))
    examples = os.path.join(os.path.dirname(here), "schema", "examples")
    for name in os.listdir(examples):
        with open(os.path.join(examples, name)) as handle:
            from_json(handle.read())


def test_readings_are_hashable():
    """frozen=True generates a __hash__ over every field, and tags is a dict -
    so hashing raised TypeError and a reading could not go in a set."""
    assert hash(Reading("temperature", 79, "F", tags={"room": "office"}))
    assert hash(Event("online", tags={"source": "fan-01"}))


def test_equal_readings_hash_equal():
    """The invariant excluding tags from the hash must not break: equal objects
    have to hash equal, and tags are still part of equality."""
    import dataclasses
    a = Reading("temperature", 79, "F", device="d", site="s", ts="t",
                seq=1, boot_id="b", tags={"k": "v"})
    same = dataclasses.replace(a)
    other_tags = dataclasses.replace(a, tags={"k": "different"})

    assert a == same and hash(a) == hash(same)
    assert a != other_tags
    assert len({a, same}) == 1


def test_hash_survives_tag_mutation():
    """A frozen dataclass cannot stop you mutating the dict inside it. Leaving
    tags out of the hash means an object already in a set keeps its bucket."""
    reading = Reading("temperature", 79, "F", tags={"room": "office"})
    before = hash(reading)
    reading.tags["room"] = "kitchen"
    assert hash(reading) == before
