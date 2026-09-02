"""Logging that survives being run as a service.

print() goes nowhere useful under systemd. These loggers write to stdout with
a level and a timestamp, which journalctl captures and can filter.
"""
import logging
import os
import sys

_LEVEL = os.environ.get("PIHOME_LOG_LEVEL", "INFO").upper()
_configured = False


def _configure():
    global _configured
    if _configured:
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S"))
    root = logging.getLogger("pihome")
    root.addHandler(handler)
    root.setLevel(getattr(logging, _LEVEL, logging.INFO))
    # This handler is the only one that should print a pihome record. Left
    # propagating, a record also travels to the root logger, so anything that
    # configures root - logging.basicConfig() in a caller, a test runner, a
    # supervising process - gets every line twice, once in this format and once
    # in theirs. Under journalctl that is two entries per event.
    root.propagate = False
    _configured = True


def get_logger(name):
    _configure()
    return logging.getLogger("pihome." + name)
