#!/bin/bash
# Boot-time registration, for a Pi not yet running systemd units.
#
# Prefer service/install.sh - it gives you logs and restarts. This exists for
# the @reboot cron line that is still on some nodes:
#   @reboot /home/pi/raspberrypi/projects/home-telemetry/service/bootup.sh
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../../.." && pwd)"
cd "$HERE/.."
PYTHONPATH="$REPO" exec python3 nodes/register_node.py
