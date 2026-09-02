#!/bin/bash
# Install and start one node as a systemd service.
#
#   sudo tools/install-service.sh home-telemetry sensehat_node
#
# Replaces the @reboot cron approach: you get logs (journalctl), a restart
# policy, and ordering after the network is actually up.
#
# The unit files are templates. This fills in @REPO@ and @USER@ from the clone
# it is run out of, rather than shipping a unit that hard-codes
# /home/pi/raspberrypi and fails to start anywhere else - which is what the
# per-project install.sh this replaces did, while installing a unit whose own
# header criticised cron for exactly that.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
    echo "usage: $0 <project> <node>" >&2
    echo "  e.g. $0 home-telemetry sensehat_node" >&2
    echo >&2
    echo "projects:" >&2
    for unit in "$REPO"/projects/*/service/*@.service; do
        [ -e "$unit" ] || continue
        echo "  $(basename "$(dirname "$(dirname "$unit")")")" >&2
    done
    exit 64
}

PROJECT="${1:-}"
NODE="${2:-}"
if [ -z "$PROJECT" ] || [ -z "$NODE" ]; then
    usage
fi

PROJECT_DIR="$REPO/projects/$PROJECT"
UNIT_TEMPLATE="$PROJECT_DIR/service/$PROJECT@.service"

[ -d "$PROJECT_DIR" ] || { echo "no such project: $PROJECT" >&2; usage; }
[ -f "$UNIT_TEMPLATE" ] || { echo "no unit template: $UNIT_TEMPLATE" >&2; exit 1; }

if [ ! -f "$PROJECT_DIR/nodes/$NODE.py" ]; then
    echo "no such node: $PROJECT/$NODE" >&2
    echo "available:" >&2
    for candidate in "$PROJECT_DIR/nodes"/*.py; do
        echo "  $(basename "$candidate" .py)" >&2
    done
    exit 1
fi

[ "$(id -u)" -eq 0 ] || {
    echo "must run as root to write /etc/systemd/system - re-run with sudo" >&2
    exit 1
}

# Run as whoever owns the clone, not a hard-coded "pi". Raspberry Pi OS has not
# created a default `pi` user since 2022 - the account is named at first boot.
RUN_AS="$(stat -c '%U' "$REPO")"
id "$RUN_AS" >/dev/null 2>&1 || {
    echo "clone is owned by $RUN_AS, which is not a user on this machine" >&2
    exit 1
}
if [ "$RUN_AS" = "root" ]; then
    echo "warning: this clone is owned by root, so the node would run as root." >&2
    echo "         A node needs GPIO and network, not the whole machine." >&2
    echo "         chown the clone to the account you log in as, then re-run." >&2
fi

INSTALLED="/etc/systemd/system/$PROJECT@.service"
sed -e "s|@REPO@|$REPO|g" -e "s|@USER@|$RUN_AS|g" "$UNIT_TEMPLATE" > "$INSTALLED"
chmod 644 "$INSTALLED"

if grep -q '@REPO@\|@USER@' "$INSTALLED"; then
    echo "placeholders left unfilled in $INSTALLED - refusing to start" >&2
    rm -f "$INSTALLED"
    exit 1
fi

echo "installed $INSTALLED (repo $REPO, user $RUN_AS)"
systemctl daemon-reload
systemctl enable --now "$PROJECT@$NODE"
systemctl --no-pager status "$PROJECT@$NODE" || true

echo
echo "logs:  journalctl -u $PROJECT@$NODE -f"
