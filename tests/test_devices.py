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


def test_fan_node_authenticates_as_sys2():
    """Records existing behaviour: the fan node has always used sys2's cert."""
    assert devices.credentials_name("fan-01") == "sys2"


def test_camera_is_flagged_unprovisioned():
    """It has never connected; the UI should show unknown, not offline."""
    assert devices.get("camera-01")["provisioned"] is False
