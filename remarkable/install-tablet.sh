#!/bin/bash
# One-shot setup of the rM2 tablet:
#   1. Generate local SSH key if missing.
#   2. Copy public key to the tablet (asks for root password once).
#   3. Create project dir.
#   4. Clean up any leftover symlink from older installs.
#   5. Configure xochitl.conf with SleepScreenPath + short IdleSuspendDelay.
#   6. Deploy rotate.sh + systemd timer, enable it.
#   7. Restart xochitl so the new config takes effect.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

REMOTE="${RM_USER}@${RM_HOST}"

KEY="$HOME/.ssh/id_ed25519"
if [ ! -f "$KEY" ]; then
  echo "→ Generating SSH key at $KEY"
  ssh-keygen -t ed25519 -f "$KEY" -N ""
fi

if ! ssh -o BatchMode=yes -o ConnectTimeout=5 "$REMOTE" true 2>/dev/null; then
  echo "→ Copying public key to tablet (you'll be prompted for the root password)"
  echo "  Find it on the device under: Settings → Help → Copyrights and licenses"
  ssh-copy-id -i "$KEY.pub" "$REMOTE"
fi

ssh -o BatchMode=yes "$REMOTE" true
echo "✓ Passwordless SSH verified"

echo "→ Creating $RM_PROJECT_DIR"
ssh "$REMOTE" "mkdir -p '$RM_PROJECT_DIR/images' && touch '$RM_PROJECT_DIR/state'"

echo "→ Cleaning up any old suspended.png symlink"
ssh "$REMOTE" "
if [ -L '$RM_SUSPEND_PNG' ] && [ -f '$RM_SUSPEND_PNG.orig.bak' ]; then
  mount -o remount,rw /
  rm '$RM_SUSPEND_PNG'
  mv '$RM_SUSPEND_PNG.orig.bak' '$RM_SUSPEND_PNG'
  mount -o remount,ro / 2>/dev/null || true
fi
"

echo "→ Stopping xochitl (it rewrites xochitl.conf on exit, so we edit while it's down)"
ssh "$REMOTE" "systemctl stop xochitl"

echo "→ Configuring xochitl.conf (SleepScreenPath, IdleSuspendDelay)"
ssh "$REMOTE" "
set -e
CONF=/home/root/.config/remarkable/xochitl.conf
mkdir -p \"\$(dirname \"\$CONF\")\"
[ -f \"\$CONF\" ] || printf '[General]\n' > \"\$CONF\"
grep -q '^\[General\]\$' \"\$CONF\" || printf '\n[General]\n' >> \"\$CONF\"
sed -i '/^SleepScreenPath=/d' \"\$CONF\"
sed -i '/^IdleSuspendDelay=/d' \"\$CONF\"
sed -i '/^isCustomSleepScreen=/d' \"\$CONF\"
sed -i '/^\[General\]\$/a SleepScreenPath=$RM_PROJECT_DIR/current.png' \"\$CONF\"
sed -i '/^\[General\]\$/a IdleSuspendDelay=60000' \"\$CONF\"
sed -i '/^\[General\]\$/a isCustomSleepScreen=true' \"\$CONF\"
"

echo "→ Deploying rotate.sh and systemd units"
scp "$SCRIPT_DIR/tablet/rotate.sh" "$REMOTE:$RM_PROJECT_DIR/rotate.sh"
ssh "$REMOTE" "chmod +x '$RM_PROJECT_DIR/rotate.sh'"
scp "$SCRIPT_DIR/tablet/quote-rotate.service" "$REMOTE:/etc/systemd/system/"
scp "$SCRIPT_DIR/tablet/quote-rotate.timer"   "$REMOTE:/etc/systemd/system/"

echo "→ Enabling hourly timer"
ssh "$REMOTE" "
  systemctl daemon-reload
  systemctl enable --now quote-rotate.timer
  systemctl list-timers quote-rotate.timer --no-pager
"

echo "→ Starting xochitl with new config"
ssh "$REMOTE" "systemctl start xochitl"

echo
echo "✓ Tablet setup complete. Push your first batch with: ./sync.sh"
