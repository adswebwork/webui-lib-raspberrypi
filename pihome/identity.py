"""Who am I? Device identity, resolved once per process.

A node script should never hard-code which Pi it is running on. It asks here,
and the answer comes from the environment or the machine, so the same code
runs on any node.
"""
import os
import socket
import uuid

from pihome import log

_logger = log.get_logger("identity")

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DEVICE_FILE = "/etc/pihome/device"

# Set by assume(), from a project's config.json. The weakest source there is:
# it says what the config expected to run here, not what this machine is.
_assumed = None

# Random per-process. A Pi has no real-time clock, so between boot and NTP
# sync its timestamps are wrong. boot_id plus a monotonic sequence number lets
# a consumer order readings correctly even when the clock jumps.
_BOOT_ID = uuid.uuid4().hex[:6]


def boot_id():
    """Short random id, stable for the life of this process."""
    return _BOOT_ID


def hostname():
    return socket.gethostname()


def outbound_ip():
    """LAN address of the interface that reaches the internet."""
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(("8.8.8.8", 80))
        return probe.getsockname()[0]
    except OSError:
        return "0.0.0.0"
    finally:
        probe.close()


def _from_machine():
    """What this machine says it is, or None if it says nothing.

    These are the authoritative sources: each describes the Pi the process is
    actually running on, rather than what someone expected to run there.
    """
    env = os.environ.get("PIHOME_DEVICE")
    if env:
        return env.strip()

    try:
        with open(_DEVICE_FILE) as handle:
            value = handle.read().strip()
            if value:
                return value
    except OSError:
        pass

    host = hostname()
    try:
        from pihome import devices
        for name, spec in devices.all().items():
            if spec.get("hostname") == host:
                return name
    except Exception:
        pass

    return None


def assume(device):
    """Declare, from project config, which node this process is meant to be.

    This is the weakest identity source and never overrides the machine:
    $PIHOME_DEVICE, /etc/pihome/device and a devices.json hostname match all
    still win, because they describe the Pi, while a config file only describes
    what was expected to run on it. It exists so an unprovisioned Pi publishes
    as a device the registry knows rather than as a bare hostname.

    A disagreement with any of those is logged loudly. That is the case worth
    catching - the Pi and the config differ about which node this is, so
    readings are about to be filed under the wrong device, which is exactly
    what the schema exists to prevent.
    """
    global _assumed
    machine = _from_machine()
    if machine is not None and machine != device:
        _logger.warning(
            "config says this node is %r but this machine identifies as %r; "
            "using %r. Check /etc/pihome/device and the node's config.json.",
            device, machine, machine)
    _assumed = device
    return device_id()


def device_id():
    """This device's id, in order of preference:

    1. $PIHOME_DEVICE            - overrides everything, useful for testing
    2. /etc/pihome/device        - one line, the right answer on a provisioned Pi
    3. hostname matched against devices.json
    4. whatever assume() was told by the project config
    5. the hostname itself
    """
    return _from_machine() or _assumed or hostname()


def site():
    """Logical site name, for when there is more than one location."""
    env = os.environ.get("PIHOME_SITE")
    if env:
        return env.strip()
    try:
        from pihome import devices
        return devices.site()
    except Exception:
        return "home"
