"""Where a device's AWS IoT certificate and key live, and which endpoint to
reach.

One directory per credential set under secrets/, or wherever PIHOME_CERT_DIR
points. A device uses the set named by `credentials` in devices.json, and its
own id when that is not set - which is the simple case and the default.
"""
import os

from pihome import devices

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PORT = int(os.environ.get("PIHOME_IOT_PORT", "8883"))

_ROOT_CA_NAMES = ("AmazonRootCA1.cer", "AmazonRootCA1.pem", "root-CA.crt")


def endpoint():
    """The AWS IoT endpoint to connect to.

    $PIHOME_IOT_ENDPOINT first, then `iot_endpoint` in devices.json. There is
    deliberately no built-in default: an endpoint identifies one AWS account,
    and a wrong one fails as a TLS timeout on a Pi with no screen - which is
    indistinguishable from a network problem and takes an evening to diagnose.
    Refusing to guess turns that into one line of text.
    """
    env = os.environ.get("PIHOME_IOT_ENDPOINT")
    if env and env.strip():
        return env.strip()

    try:
        from pihome import devices
        configured = devices.iot_endpoint()
    except Exception:
        configured = None
    if configured:
        return configured

    raise RuntimeError(
        "no AWS IoT endpoint configured. Set \"iot_endpoint\" in devices.json "
        "to your account's endpoint, or export PIHOME_IOT_ENDPOINT. Find it "
        "with: aws iot describe-endpoint --endpoint-type iot:Data-ATS")


def port():
    return PORT


def _candidate_dirs(name):
    override = os.environ.get("PIHOME_CERT_DIR")
    if override:
        yield override
    yield os.path.join(_REPO, "secrets", name)


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
