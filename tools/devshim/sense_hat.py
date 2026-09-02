"""Stand-in for the real `sense_hat` module on a machine without one.

tools/dev puts this directory on PYTHONPATH, where it shadows the real module
and re-exports the desktop emulator. A recipe written for a Pi then runs
unmodified on a laptop.

The point is that recipes keep saying `from sense_hat import SenseHat` - plain
Pi code, with no trace of this repo's dev tooling in it. Copy one onto a Pi,
or into someone else's project, and it just works.
"""
from sense_emu import *        # noqa: F401,F403
from sense_emu import SenseHat  # noqa: F401
