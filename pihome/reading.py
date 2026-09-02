"""The device-to-web wire format.

Everything a device sends is a Reading (a measurement) or an Event (something
happened). Both carry who sent them, when, and in what units - none of which
the old `{"temp": "79"}` payload had.

This module is the contract. schema/*.json is its language-neutral twin, and a
web UI should be written against that rather than against this file.
"""
import itertools
import json
import time
from dataclasses import dataclass, field, asdict

from pihome import identity

SCHEMA_VERSION = 1

_seq = itertools.count(1)


def _now_iso():
    """UTC, ISO-8601, millisecond precision, explicit Z.

    Samples the clock once - reading it twice can straddle a second boundary
    and yield a timestamp a full second wrong.
    """
    now = time.time()
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(now)) + \
        ".{:03d}Z".format(int((now % 1) * 1000))


def _next_seq():
    return next(_seq)


@dataclass(frozen=True)
class Reading:
    """A single measurement from one device.

    Only metric, value and unit are yours to supply - identity and timing fill
    themselves in, so a node script cannot forget them or get them wrong.
    """
    metric: str                 # "temperature" | "humidity" | "motion" | "uptime"
    value: object               # number, or bool for a detector. A string only
                                # for a genuinely textual metric such as
                                # ip_address - never a stringified number, which
                                # is what the old {"temp": "79"} payload did and
                                # what forced every consumer to re-parse.
    unit: str                   # "F" | "C" | "%" | "hPa" | "bool" | "s" | "text"
    device: str = field(default_factory=identity.device_id)
    site: str = field(default_factory=identity.site)
    ts: str = field(default_factory=_now_iso)
    seq: int = field(default_factory=_next_seq)
    boot_id: str = field(default_factory=identity.boot_id)
    # hash=False: frozen=True generates a __hash__ from every field, and a dict
    # is unhashable, so hash(reading) raised TypeError - readings could not go
    # in a set or be used as a dict key. Excluding tags is sound rather than a
    # dodge: __eq__ still compares them, so two equal objects still hash equal.
    # It also keeps the hash stable, since a "frozen" dataclass cannot stop you
    # mutating the dict inside it.
    tags: dict = field(default_factory=dict, hash=False)
    v: int = SCHEMA_VERSION

    def to_dict(self):
        return asdict(self)

    def to_json(self):
        return json.dumps(self.to_dict(), sort_keys=True)

    def topic(self):
        from pihome import topics
        return topics.telemetry(self.device, self.metric)


@dataclass(frozen=True)
class Event:
    """Something happened that is not a measurement."""
    kind: str                   # "online" | "offline" | "motion" | "capture" | "error"
    level: str = "info"         # "info" | "warn" | "error"
    message: str = ""
    device: str = field(default_factory=identity.device_id)
    site: str = field(default_factory=identity.site)
    ts: str = field(default_factory=_now_iso)
    seq: int = field(default_factory=_next_seq)
    boot_id: str = field(default_factory=identity.boot_id)
    tags: dict = field(default_factory=dict, hash=False)   # see Reading.tags
    v: int = SCHEMA_VERSION

    def to_dict(self):
        return asdict(self)

    def to_json(self):
        return json.dumps(self.to_dict(), sort_keys=True)

    def topic(self):
        from pihome import topics
        return topics.events(self.device)


_READING_REQUIRED = ("metric", "value", "unit", "device", "ts")
_EVENT_REQUIRED = ("kind", "device", "ts")


def from_json(raw):
    """Parse a payload into a Reading or an Event.

    Raises ValueError on anything malformed rather than returning a
    half-populated object - a silently-wrong reading is worse than a crash.
    """
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode("utf-8")
    try:
        data = json.loads(raw)
    except (ValueError, TypeError) as exc:
        raise ValueError("payload is not JSON: {}".format(exc))

    if not isinstance(data, dict):
        raise ValueError("payload is not a JSON object: {!r}".format(type(data).__name__))

    if "kind" in data:
        missing = [k for k in _EVENT_REQUIRED if k not in data]
        if missing:
            raise ValueError("event missing {}".format(", ".join(missing)))
        return Event(**_known_fields(data, Event))

    missing = [k for k in _READING_REQUIRED if k not in data]
    if missing:
        raise ValueError("reading missing {}".format(", ".join(missing)))
    return Reading(**_known_fields(data, Reading))


def _known_fields(data, cls):
    allowed = set(cls.__dataclass_fields__)
    return {k: v for k, v in data.items() if k in allowed}


# --- legacy bridge ---------------------------------------------------------
# The fleet published {"temp": "79"} to home/temperature for years, from more
# than one device, with no way to tell them apart. These let a consumer read
# the old shape during the changeover.

def is_legacy(raw):
    """True if this looks like a pre-schema payload."""
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode("utf-8")
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        return False
    return isinstance(data, dict) and "v" not in data and (
        "temp" in data or "message" in data or "ipaddress" in data or "sensor" in data)


_LEGACY_METRICS = {
    "temp": ("temperature", "F"),
    "ipaddress": ("ip_address", "text"),
    "message": ("message", "text"),
    "sensor": ("sensor", "text"),
}


def upgrade_legacy(raw, device):
    """Turn an old payload into a Reading, given the device it came from.

    The device must be supplied because the old format does not carry it -
    which is the entire reason for the new one.
    """
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode("utf-8")
    data = json.loads(raw)
    for key, (metric, unit) in _LEGACY_METRICS.items():
        if key in data:
            value = data[key]
            if unit in ("F", "C"):
                try:
                    value = float(value)
                except (TypeError, ValueError):
                    raise ValueError("legacy {} is not numeric: {!r}".format(key, value))
            return Reading(metric=metric, value=value, unit=unit, device=device)
    raise ValueError("unrecognised legacy payload: {!r}".format(data))
