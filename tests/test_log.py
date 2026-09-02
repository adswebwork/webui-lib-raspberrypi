"""Log output under a service manager.

The pihome logger owns its own handler and format. If a record also reaches
the root logger, anything that configures root - basicConfig() in a caller, a
test runner, a supervising process - prints it a second time in its own
format, which under journalctl is two entries for one event.

The line-counting check runs in a subprocess on purpose. pytest attaches its
own capture handlers directly to the `pihome` logger and to the root, so
counting handlers or captured output in-process measures pytest's plumbing
rather than what a node prints on a Pi.
"""
import logging
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from pihome import log  # noqa: E402


def _run(code):
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        env=dict(os.environ, PYTHONPATH=REPO, PIHOME_DEVICE="test-01"),
        timeout=60)
    return result.stdout.decode("utf-8", "replace")


def test_pihome_records_do_not_reach_the_root_logger():
    log.get_logger("probe")                      # forces _configure()
    assert logging.getLogger("pihome").propagate is False


def test_one_call_produces_one_line_when_a_caller_configures_root():
    """The regression in plain terms: configure root, log once, count lines."""
    out = _run(
        "import logging;"
        "logging.basicConfig(level=logging.INFO, format='ROOT: %(message)s');"
        "from pihome import log;"
        "log.get_logger('probe').warning('one event')")

    assert out.count("one event") == 1, "logged twice:\n" + out
    assert "ROOT:" not in out, "root logger also printed it:\n" + out


def test_the_record_still_carries_level_and_name():
    """propagate=False must not cost the format journalctl is filtered on."""
    out = _run("from pihome import log;"
               "log.get_logger('probe').warning('one event')")
    assert "WARNING" in out and "pihome.probe" in out, out


def test_configure_does_not_stack_handlers():
    """_configure() runs on every get_logger call and must be idempotent."""
    out = _run(
        "import logging;"
        "from pihome import log;"
        "[log.get_logger(n) for n in 'abcde'];"
        "print('HANDLERS', len(logging.getLogger('pihome').handlers))")
    assert "HANDLERS 1" in out, out
