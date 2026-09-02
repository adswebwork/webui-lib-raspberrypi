"""Every node must be importable on a machine that is not a Raspberry Pi.

This is the check that caught fan_node and alert_node claiming their GPIO pin
at module scope, and sensehat_node building a Sense HAT at module scope. Those
are easy to reintroduce and invisible until someone runs the node, so the check
lives here rather than in a reviewer's shell history.

Each node is imported in its own subprocess, exactly as `tools/dev` would run
it: devshim first on PYTHONPATH, mock gpiozero pins. A subprocess rather than
an in-process import because RPi.GPIO and sense_hat are process-global once
imported, and one node's module-scope side effects must not decide whether the
next node passes.

Importing must not touch hardware, connect to anything, or read a clock that
matters. If a node needs a pin, a camera or a Sense HAT, it takes it in main().
"""
import glob
import os
import subprocess
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NODES = sorted(glob.glob(os.path.join(REPO, "projects", "*", "nodes", "*.py")))


def _relative(path):
    return os.path.relpath(path, REPO)


def test_there_are_nodes_to_check():
    """Guard against the glob silently matching nothing after a move."""
    assert len(NODES) >= 13


@pytest.mark.parametrize("node", NODES, ids=_relative)
def test_node_imports_off_pi(node):
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([
        os.path.join(REPO, "tools", "devshim"), REPO])
    env["GPIOZERO_PIN_FACTORY"] = "mock"
    env["PIHOME_DEVICE"] = "test-01"
    env["PIHOME_SITE"] = "home"

    probe = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "_import_probe.py")
    result = subprocess.run(
        [sys.executable, probe, node],
        env=env, cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        timeout=60)

    assert result.returncode == 0, "{}:\n{}".format(
        _relative(node), result.stdout.decode("utf-8", "replace"))
