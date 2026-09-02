import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pihome import devices


def test_registry_is_valid():
    assert devices.validate() == []


def test_every_device_has_a_role():
    assert all("role" in spec for spec in devices.all().values())


def test_unknown_device_error_lists_known_ids():
    try:
        devices.get("nope-99")
    except KeyError as exc:
        assert "sensehat-01" in str(exc)
    else:
        raise AssertionError("expected KeyError")


def test_credential_set_defaults_to_the_device_id():
    """The simple case: a device uses a set named after itself."""
    for device in devices.all():
        assert devices.credentials_name(device) == device


def test_a_device_can_name_a_different_credential_set(monkeypatch):
    """Two devices sharing one certificate has to stay expressible - the old
    fleet did exactly that - but it is recorded as data, not hidden in code."""
    monkeypatch.setattr(devices, "_cache", {
        "devices": {"fan-01": {"role": "actuator", "credentials": "shared-01"}}})
    assert devices.credentials_name("fan-01") == "shared-01"


def test_nothing_is_flagged_provisioned_yet():
    """The fleet is being stood up on a new AWS account; no node has a
    certificate. A registry claiming otherwise sends someone hunting for
    credentials that were never created."""
    assert not any(spec.get("provisioned") for spec in devices.all().values())


def test_camera_is_flagged_unprovisioned():
    """It has never connected; the UI should show unknown, not offline."""
    assert devices.get("camera-01")["provisioned"] is False
