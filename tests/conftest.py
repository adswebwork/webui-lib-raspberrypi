"""Test setup.

PIHOME_DEVICE is set here, before any test module imports pihome, so device
identity is deterministic regardless of the order pytest collects modules in.
Tests that care about a specific device pass it explicitly.
"""
import logging
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["PIHOME_DEVICE"] = "test-01"
os.environ["PIHOME_SITE"] = "home"


@pytest.fixture
def pihome_caplog(caplog):
    """caplog, but attached to the `pihome` logger rather than to root.

    pihome.log sets propagate=False so a record reaches its own handler and
    nowhere else - which is the point, otherwise anything configuring the root
    logger prints every line twice. That also means records never arrive at
    root, so plain `caplog` captures nothing from them.

    Whether plain caplog appears to work is a pytest-version accident: pytest 9
    happens to attach its capture handler to non-root loggers as well, pytest 8
    attaches only at root. The fleet runs Python 3.9, which resolves pytest 8,
    so a test relying on that difference passes locally and fails in CI.
    Attaching the handler explicitly works on both.
    """
    logger = logging.getLogger("pihome")
    logger.addHandler(caplog.handler)
    try:
        yield caplog
    finally:
        logger.removeHandler(caplog.handler)
