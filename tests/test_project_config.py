"""Project configs must name devices the registry actually knows.

`device` and `source_device` are only meaningful if they resolve. A typo in
either is silent at import - the node reads it in main(), on the Pi, at 3am -
so it is checked here instead. This is what keeps them live configuration
rather than decoration.
"""
import glob
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pihome import config, devices

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGS = sorted(glob.glob(os.path.join(REPO, "projects", "*", "config.json")))

# Nodes that drive something in response to another device's readings. Each
# must name its one source rather than subscribing to every device on the bus.
ACTUATORS = ("fan_node", "alert_node")


def _project(path):
    return os.path.basename(os.path.dirname(path))


def _node_blocks(path):
    """(node name, settings) for every node in a project config."""
    data = config.load(path)
    return sorted(data.get("nodes", {}).items())


def test_registry_is_well_formed():
    assert devices.validate() == []


def test_there_are_configs_to_check():
    assert len(CONFIGS) >= 3


@pytest.mark.parametrize("path", CONFIGS, ids=_project)
def test_every_node_names_a_known_device(path):
    known = set(devices.all())
    for node, settings in _node_blocks(path):
        assert "device" in settings, \
            "{}: {} has no device; identity.assume() would raise".format(
                _project(path), node)
        assert settings["device"] in known, \
            "{}: {} claims unknown device {!r}; devices.json knows {}".format(
                _project(path), node, settings["device"], ", ".join(sorted(known)))


@pytest.mark.parametrize("path", CONFIGS, ids=_project)
def test_actuators_name_one_source_device(path):
    """Never a wildcard: a relay switching mains should answer to a named Pi."""
    known = set(devices.all())
    for node, settings in _node_blocks(path):
        if node not in ACTUATORS:
            continue
        source = settings.get("source_device")
        assert source, "{}: {} must name a source_device".format(
            _project(path), node)
        assert source != "+", "{}: {} must not listen to every device".format(
            _project(path), node)
        assert source in known, \
            "{}: {} listens to unknown device {!r}".format(
                _project(path), node, source)


def test_json_stays_parseable():
    """A trailing comma here breaks every node on the Pi at once."""
    for path in CONFIGS + [os.path.join(REPO, "devices.json")]:
        with open(path) as handle:
            json.load(handle)
