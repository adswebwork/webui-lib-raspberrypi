#!/bin/bash
# Pull the latest scripts on a Pi. Intended for cron or a manual refresh.
#
# Replaces _globalConfig/gitupdate.py, which shelled out to `pi && git l` -
# interactive shell aliases that os.system never loads.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
git -C "$REPO" pull --ff-only
echo "updated $(git -C "$REPO" rev-parse --short HEAD)"
