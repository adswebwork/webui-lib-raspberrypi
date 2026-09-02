"""Which certificate a device authenticates with.

This resolution is the difference between a node connecting and a node sitting
in a restart loop, and it had no tests at all. Everything here runs against
temporary directories and dummy files - no real key is read, created or needed.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pihome import credentials  # noqa: E402


def _make_set(directory, name, root_ca=False):
    """A credential set with the two files certs_for() looks for."""
    folder = os.path.join(str(directory), name)
    os.makedirs(folder, exist_ok=True)
    for filename in ("private.pem.key", "certificate.pem.crt"):
        with open(os.path.join(folder, filename), "w") as handle:
            handle.write("dummy")
    if root_ca:
        with open(os.path.join(folder, "AmazonRootCA1.cer"), "w") as handle:
            handle.write("dummy")
    return folder


@pytest.fixture(autouse=True)
def no_ambient_override(monkeypatch):
    monkeypatch.delenv("PIHOME_CERT_DIR", raising=False)


def test_cert_dir_override_wins(tmp_path, monkeypatch):
    folder = _make_set(tmp_path, "anywhere", root_ca=True)
    monkeypatch.setenv("PIHOME_CERT_DIR", folder)

    ca, key, cert = credentials.certs_for("sensehat-01")

    assert key.startswith(folder) and cert.startswith(folder)
    assert ca.startswith(folder)


def test_found_under_secrets(tmp_path, monkeypatch):
    monkeypatch.setattr(credentials, "_REPO", str(tmp_path))
    _make_set(tmp_path / "secrets", "sys1", root_ca=True)

    ca, key, cert = credentials.certs_for("sys1")

    assert os.path.exists(key) and os.path.exists(cert) and os.path.exists(ca)


def test_device_id_resolves_through_the_registry(tmp_path, monkeypatch):
    """A device pointed at a shared credential set finds it. A node must not
    need to know which set it authenticates with."""
    monkeypatch.setattr(credentials, "_REPO", str(tmp_path))
    monkeypatch.setattr("pihome.devices._cache", {
        "devices": {"fan-01": {"role": "actuator", "credentials": "shared-01"}}})
    _make_set(tmp_path / "secrets", "shared-01", root_ca=True)

    _, key, _ = credentials.certs_for("fan-01")

    assert os.path.basename(os.path.dirname(key)) == "shared-01"


def test_root_ca_falls_back_to_the_shared_copy(tmp_path, monkeypatch):
    """Only the public Amazon root is shared; the key and cert never are."""
    monkeypatch.setattr(credentials, "_REPO", str(tmp_path))
    _make_set(tmp_path / "secrets", "sys1")           # no CA in the set
    shared = os.path.join(str(tmp_path), "secrets", "AmazonRootCA1.cer")
    with open(shared, "w") as handle:
        handle.write("dummy")

    ca, _, _ = credentials.certs_for("sys1")

    assert ca == shared


def test_missing_credentials_name_where_it_looked(tmp_path, monkeypatch):
    """The error has to be actionable at 3am on a Pi with no screen."""
    monkeypatch.setattr(credentials, "_REPO", str(tmp_path))

    with pytest.raises(FileNotFoundError) as excinfo:
        credentials.certs_for("camera-01")

    message = str(excinfo.value)
    assert "camera-01" in message, "should name the device"
    assert "secrets" in message, "should say where it looked"


def test_globalconfig_layout_is_no_longer_consulted(tmp_path, monkeypatch):
    """The pre-restructure fallback is gone. A set placed only in the old
    location must not silently satisfy a lookup - if it did, a Pi could keep
    running on a credential nobody knows is still in use."""
    monkeypatch.setattr(credentials, "_REPO", str(tmp_path))
    _make_set(tmp_path / "_globalConfig", "_sys1", root_ca=True)

    with pytest.raises(FileNotFoundError):
        credentials.certs_for("sys1")


def test_is_provisioned_reports_both_ways(tmp_path, monkeypatch):
    monkeypatch.setattr(credentials, "_REPO", str(tmp_path))
    _make_set(tmp_path / "secrets", "sys1", root_ca=True)

    assert credentials.is_provisioned("sys1") is True
    assert credentials.is_provisioned("camera-01") is False


def test_endpoint_comes_from_the_environment_first(monkeypatch):
    monkeypatch.setenv("PIHOME_IOT_ENDPOINT", "abc123-ats.iot.eu-west-1.amazonaws.com")
    assert credentials.endpoint() == "abc123-ats.iot.eu-west-1.amazonaws.com"


def test_endpoint_falls_back_to_the_registry(monkeypatch):
    monkeypatch.setattr("pihome.devices._cache",
                        {"iot_endpoint": "xyz-ats.iot.us-east-1.amazonaws.com",
                         "devices": {}})
    assert credentials.endpoint() == "xyz-ats.iot.us-east-1.amazonaws.com"


def test_unset_endpoint_raises_instead_of_guessing(monkeypatch):
    """The old default pointed at an AWS account that no longer exists. A
    wrong endpoint fails as a TLS timeout on a screenless Pi, which looks
    exactly like a network fault; refusing to guess makes it one line."""
    monkeypatch.setattr("pihome.devices._cache", {"iot_endpoint": None, "devices": {}})

    with pytest.raises(RuntimeError) as excinfo:
        credentials.endpoint()

    message = str(excinfo.value)
    assert "PIHOME_IOT_ENDPOINT" in message and "devices.json" in message
    assert "describe-endpoint" in message, "should say how to find the value"


def test_port_has_a_sane_default():
    assert credentials.port() == 8883
    assert isinstance(credentials.port(), int)
