"""Import one node and report whether importing it took any hardware.

Run as a subprocess by tests/test_nodes_import.py:

    python3 tests/_import_probe.py projects/<project>/nodes/<node>.py

Exits non-zero with an explanation if the import fails, or if it succeeds but
leaves a pin claimed. Checking only that the import succeeds is not enough:
gpiozero's mock pins let a module-scope `OutputDevice(26)` construct happily
off a Pi, so the failure this is meant to catch would slip through unnoticed
and only show up as a pin conflict on the real hardware.
"""
import importlib.util
import sys


def claimed_pins():
    """Pins taken during import, across both GPIO libraries."""
    taken = []

    # gpiozero, via the mock factory tools/dev selects. Keys are PinInfo
    # objects on recent gpiozero and plain numbers on older ones, and PinInfo
    # stringifies to a paragraph - so take the short name where there is one.
    gpiozero = sys.modules.get("gpiozero")
    if gpiozero is not None:
        factory = getattr(gpiozero.Device, "pin_factory", None)
        names = (getattr(p, "name", None) or str(p)
                 for p in getattr(factory, "pins", {}))
        for name in sorted(names):
            taken.append("gpiozero {}".format(name))

    # RPi.GPIO, via tools/devshim/RPi/GPIO.py
    gpio = sys.modules.get("RPi.GPIO")
    if gpio is not None:
        for pin in sorted(str(p) for p in getattr(gpio, "setup_pins", {})):
            taken.append("RPi.GPIO pin {}".format(pin))

    return taken


def main(path):
    spec = importlib.util.spec_from_file_location("node_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    taken = claimed_pins()
    if taken:
        sys.stderr.write(
            "importing this node claimed hardware: {}\n"
            "Take pins in main(), not at module scope - otherwise importing "
            "the module takes the pin, two nodes cannot be loaded in one "
            "process, and tests cannot touch it.\n".format(", ".join(taken)))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
