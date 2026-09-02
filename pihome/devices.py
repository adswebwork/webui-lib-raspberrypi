"""Read-only access to devices.json, the fleet registry."""
import json
import os

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PATH = os.environ.get("PIHOME_DEVICES", os.path.join(_REPO, "devices.json"))

_cache = None


def _load():
    global _cache
    if _cache is None:
        with open(_PATH) as handle:
            _cache = json.load(handle)
    return _cache


def all():
    """Every device, as {device_id: spec}."""
    return _load()["devices"]


def site():
    return _load().get("site", "home")


def iot_endpoint():
    """The fleet's AWS IoT endpoint, or None if it has not been set.

    Fleet-level, so it lives beside `site` rather than being repeated per
    device. None is the honest default: an endpoint belongs to one AWS
    account, and this repository does not ship with one.
    """
    return _load().get("iot_endpoint") or None


def get(device_id):
    """One device's spec. Raises KeyError with the known ids listed."""
    registry = all()
    if device_id not in registry:
        raise KeyError(
            "unknown device {!r}; devices.json knows: {}".format(
                device_id, ", ".join(sorted(registry))))
    return registry[device_id]


def by_role(role):
    return {k: v for k, v in all().items() if v.get("role") == role}


def credentials_name(device_id):
    """Which credential directory this device authenticates with.

    Not always the device's own name - see fan-01 in devices.json.
    """
    return get(device_id).get("credentials", device_id)


def validate():
    """Check the registry is well formed. Returns a list of problems."""
    problems = []
    for name, spec in all().items():
        if "role" not in spec:
            problems.append("{}: missing role".format(name))
        if spec.get("pin_mode") not in (None, "BCM", "BOARD"):
            problems.append("{}: pin_mode must be BCM, BOARD or null".format(name))
        for key in ("publishes", "subscribes", "hardware"):
            if key in spec and not isinstance(spec[key], list):
                problems.append("{}: {} must be a list".format(name, key))
    return problems
