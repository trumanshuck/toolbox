#!/bin/bash
# xochitl must drive its own idle-suspend to paint the pushed image — the
# tablet shows it ~30s after the rotation this script triggers.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

REMOTE="${RM_USER}@${RM_HOST}"

# Idle-suspend (60s) can put the tablet to sleep mid-sync; hold a systemd
# sleep inhibitor for the ritual. The 600s timeout self-releases if we die.
echo "→ Holding tablet awake"
ssh -o ConnectTimeout=10 "$REMOTE" \
  "command -v systemd-inhibit >/dev/null &&
   { systemd-inhibit --what=sleep --who=sync --why='sync in progress' \
       sleep 600 >/dev/null 2>&1 & echo \$! > /tmp/sync-inhibit.pid; } ||
   echo '  (no systemd-inhibit on tablet — continuing without)'" \
  || echo "  (tablet unreachable — continuing, rsync will retry contact)"

release_inhibitor() {
  ssh -o ConnectTimeout=10 "$REMOTE" \
    "kill \$(cat /tmp/sync-inhibit.pid) 2>/dev/null; rm -f /tmp/sync-inhibit.pid" \
    2>/dev/null || true
}
trap release_inhibitor EXIT

echo "→ Rendering quotes"
python3 "$SCRIPT_DIR/render.py"

echo "→ Rendering dashboard"
python3 "$SCRIPT_DIR/render_dashboard.py"

echo "→ Syncing to tablet"
rsync -avz --delete \
  "$SCRIPT_DIR/rendered/" \
  "$REMOTE:$RM_PROJECT_DIR/images/"

echo "→ Resetting rotation state"
ssh "$REMOTE" ": > '$RM_PROJECT_DIR/state'; rm -f '$RM_PROJECT_DIR/slot' '$RM_PROJECT_DIR/dash-index'; date +%Y-%m-%d > '$RM_PROJECT_DIR/last-sync'"

release_inhibitor

echo "→ Rotating"
ssh "$REMOTE" "$RM_PROJECT_DIR/rotate.sh dash"

echo "✓ Done — tablet will idle-suspend with the new dashboard in ~30s"
