"""The published schema and the code that produces payloads must agree.

schema/*.json is the contract a web UI will be written against, and it is a
separate artefact from pihome.reading - nothing makes them move together. The
existing round-trip test does not catch drift, because from_json() ignores
unknown fields and only checks that the required ones are present: it would
happily accept a payload the schema rejects, and accept a schema that has
drifted away from the dataclass.

So this validates real payloads, produced by the code, against the real schema
files - and checks the two field lists still match, which is what actually
goes wrong when someone adds a field to one side.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

jsonschema = pytest.importorskip("jsonschema", reason="pip3 install jsonschema")

from pihome.reading import Event, Reading  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_DIR = os.path.join(REPO, "schema")


def _schema(name):
    with open(os.path.join(SCHEMA_DIR, name)) as handle:
        return json.load(handle)


READING_SCHEMA = _schema("reading.schema.json")
EVENT_SCHEMA = _schema("event.schema.json")

# One per shape the fleet actually publishes. A number, a boolean and a string
# value all appear in live code, so all three must be legal.
READINGS = [
    Reading("temperature", 79, "F", tags={"sensor": "sense-hat"}),
    Reading("humidity", 41.5, "%"),
    Reading("motion", True, "bool"),
    Reading("ip_address", "192.168.1.20", "text"),
    Reading("uptime", 88123.5, "s"),
    Reading("capture", 1, "count", tags={"image": "2026-09-01-182205.jpg"}),
]

EVENTS = [
    Event("online", "info", "node up"),
    Event("offline", "info", "node down"),
    Event("actuate", "warn", "fan on", tags={"source": "sensehat-01"}),
    Event("error", "error", 'quotes " and \n newlines'),
]


def _validator(schema):
    cls = jsonschema.validators.validator_for(schema)
    cls.check_schema(schema)
    return cls(schema)


def test_schemas_are_themselves_valid():
    _validator(READING_SCHEMA)
    _validator(EVENT_SCHEMA)


@pytest.mark.parametrize("reading", READINGS, ids=lambda r: r.metric)
def test_readings_validate(reading):
    errors = sorted(_validator(READING_SCHEMA).iter_errors(reading.to_dict()),
                    key=str)
    assert not errors, "\n".join(e.message for e in errors)


@pytest.mark.parametrize("event", EVENTS, ids=lambda e: e.kind)
def test_events_validate(event):
    errors = sorted(_validator(EVENT_SCHEMA).iter_errors(event.to_dict()),
                    key=str)
    assert not errors, "\n".join(e.message for e in errors)


def test_committed_examples_validate():
    """The examples are what a web UI author reads first. They must be real."""
    directory = os.path.join(SCHEMA_DIR, "examples")
    names = sorted(os.listdir(directory))
    assert names, "no examples to check"
    for name in names:
        with open(os.path.join(directory, name)) as handle:
            payload = json.load(handle)
        schema = EVENT_SCHEMA if "kind" in payload else READING_SCHEMA
        errors = sorted(_validator(schema).iter_errors(payload), key=str)
        assert not errors, "{}: {}".format(
            name, "; ".join(e.message for e in errors))


@pytest.mark.parametrize("cls, schema", [(Reading, READING_SCHEMA),
                                         (Event, EVENT_SCHEMA)],
                         ids=["reading", "event"])
def test_field_lists_match(cls, schema):
    """The drift that actually happens: a field added on one side only.

    Both schemas set additionalProperties: false, so a new dataclass field
    would make every payload invalid; a new schema property that no dataclass
    field fills would be a promise to consumers that nothing keeps.
    """
    in_code = set(cls.__dataclass_fields__)
    in_schema = set(schema["properties"])
    assert in_code == in_schema, (
        "schema and dataclass disagree - only in code: {}; only in schema: {}"
        .format(sorted(in_code - in_schema) or "none",
                sorted(in_schema - in_code) or "none"))


@pytest.mark.parametrize("cls, schema", [(Reading, READING_SCHEMA),
                                         (Event, EVENT_SCHEMA)],
                         ids=["reading", "event"])
def test_required_fields_are_always_produced(cls, schema):
    """Anything the schema calls required must be filled in automatically, or a
    node could publish a payload its own consumers reject."""
    produced = (Reading("temperature", 1, "F") if cls is Reading
                else Event("online"))
    missing = set(schema["required"]) - set(produced.to_dict())
    assert not missing, "never populated: {}".format(sorted(missing))
