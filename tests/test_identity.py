"""Device identity resolution.

The device id decides which topic a reading lands on and which certificate the
node authenticates with, so getting it from the wrong place is how readings end
up filed under the wrong Pi - the exact failure the schema exists to prevent.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pihome import identity


@pytest.fixture(autouse=True)
def clean_identity():
    """Undo assume() and the env override between tests."""
    saved_env = os.environ.get("PIHOME_DEVICE")
    saved_assumed = identity._assumed
    yield
    identity._assumed = saved_assumed
    if saved_env is None:
        os.environ.pop("PIHOME_DEVICE", None)
    else:
        os.environ["PIHOME_DEVICE"] = saved_env


def test_env_beats_config():
    """The machine wins. A config file says what was meant to run here, not
    what this Pi is."""
    os.environ["PIHOME_DEVICE"] = "mains-01"
    identity.assume("fan-01")
    assert identity.device_id() == "mains-01"


def test_config_is_used_when_the_machine_says_nothing():
    """An unprovisioned Pi should publish as a device the registry knows,
    rather than as a bare hostname that means nothing to a consumer."""
    os.environ.pop("PIHOME_DEVICE", None)
    identity._assumed = None
    fallback = identity.device_id()
    identity.assume("fan-01")
    assert identity.device_id() == "fan-01"
    assert fallback == identity.hostname()


def test_mismatch_is_logged(pihome_caplog):
    """Config and machine disagreeing is the case worth catching."""
    os.environ["PIHOME_DEVICE"] = "mains-01"
    with pihome_caplog.at_level("WARNING", logger="pihome.identity"):
        identity.assume("fan-01")
    assert "fan-01" in pihome_caplog.text and "mains-01" in pihome_caplog.text


def test_registry_hostname_match_beats_config_and_warns(pihome_caplog, monkeypatch):
    """The subtle case: no /etc/pihome/device, but devices.json recognises this
    machine's hostname. That is still the machine talking, so it wins over the
    config and the disagreement is reported."""
    os.environ.pop("PIHOME_DEVICE", None)
    identity._assumed = None
    monkeypatch.setattr(identity, "hostname", lambda: "kitchen-pi")
    monkeypatch.setattr(
        "pihome.devices.all",
        lambda: {"mains-01": {"hostname": "kitchen-pi", "role": "actuator"}})

    with pihome_caplog.at_level("WARNING", logger="pihome.identity"):
        identity.assume("fan-01")

    assert identity.device_id() == "mains-01"
    assert "fan-01" in pihome_caplog.text and "mains-01" in pihome_caplog.text


def test_agreement_is_quiet(pihome_caplog):
    os.environ["PIHOME_DEVICE"] = "fan-01"
    with pihome_caplog.at_level("WARNING", logger="pihome.identity"):
        identity.assume("fan-01")
    assert not pihome_caplog.text
