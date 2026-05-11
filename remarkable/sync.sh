#!/bin/bash
# Render quotes/*.md → rendered/*.png, push to the tablet, trigger an
# immediate rotation. The tablet will idle-suspend ~30s later showing the
# new quote (xochitl needs to drive its own suspend to paint the image).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

REMOTE="${RM_USER}@${RM_HOST}"

echo "→ Rendering quotes"
python3 "$SCRIPT_DIR/render.py"

echo "→ Syncing to tablet"
rsync -avz --delete \
  "$SCRIPT_DIR/rendered/" \
  "$REMOTE:$RM_PROJECT_DIR/images/"

echo "→ Resetting shuffle queue"
ssh "$REMOTE" ": > '$RM_PROJECT_DIR/state'"

echo "→ Rotating"
ssh "$REMOTE" "$RM_PROJECT_DIR/rotate.sh"

echo "✓ Done — tablet will idle-suspend with the new quote in ~30s"
