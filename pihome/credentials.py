"""Where a device's AWS IoT certificate and key live.

Resolution order is deliberate: secrets/ is where credentials belong, but the
legacy _globalConfig/_sysN/ layout is checked as a fallback so a running Pi
keeps authenticating through the restructure without being touched.
"""
import os

from pihome import devices

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ENDPOINT = os.environ.get(
    "PIHOME_IOT_ENDPOINT", "a2r4022mytw4qr-ats.iot.us-east-1.amazonaws.com")
PORT = int(os.environ.get("PIHOME_IOT_PORT", "8883"))

_ROOT_CA_NAMES = ("AmazonRootCA1.cer", "AmazonRootCA1.pem", "root-CA.crt")


def endpoint():
    return ENDPOINT


def port():
    return PORT


def _candidate_dirs(name):
    override = os.environ.get("PIHOME_CERT_DIR")
    if override:
        yield override
    yield os.path.join(_REPO, "secrets", name)
    yield os.path.join(_REPO, "_globalConfig", "_" + name)   # legacy layout


def _find_root_ca(folder):
    for candidate in _ROOT_CA_NAMES:
        path = os.path.join(folder, candidate)
        if os.path.exists(path):
            return path
    shared = os.path.join(_REPO, "secrets", "AmazonRootCA1.cer")
    if os.path.exists(shared):
        return shared
    return os.path.join(folder, _ROOT_CA_NAMES[0])


def certs_for(device):
    """(ca, private key, certificate) for a device id or a raw credential name.

    Accepts either - 'sensehat-01' is looked up in devices.json to find which
    credential set it uses, and 'sys1' is used directly.
    """
    try:
        name = devices.credentials_name(device)
    except KeyError:
        name = device

    for folder in _candidate_dirs(name):
        key = os.path.join(folder, "private.pem.key")
        cert = os.path.join(folder, "certificate.pem.crt")
        if os.path.exists(key) and os.path.exists(cert):
            return (_find_root_ca(folder), key, cert)

    searched = " or ".join(_candidate_dirs(name))
    raise FileNotFoundError(
        "no credentials for {!r} (credential set {!r}); looked in {}. "
        "Provision them per secrets/README.md.".format(device, name, searched))


def is_provisioned(device):
    try:
        certs_for(device)
        return True
    except (FileNotFoundError, KeyError):
        return False
