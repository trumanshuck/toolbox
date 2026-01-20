#!/bin/bash
# Install Tuple triggers for MacWhisper recording

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TRIGGER_DIR="$HOME/.tuple/triggers/macwhisper-recording"

echo "Installing Tuple MacWhisper recording triggers..."

# Create trigger directory
mkdir -p "$TRIGGER_DIR"

# Symlink the trigger scripts
ln -sf "$SCRIPT_DIR/call-connected" "$TRIGGER_DIR/call-connected"
ln -sf "$SCRIPT_DIR/call-ended" "$TRIGGER_DIR/call-ended"

# Ensure scripts are executable
chmod +x "$SCRIPT_DIR/call-connected"
chmod +x "$SCRIPT_DIR/call-ended"

echo "Installed triggers to: $TRIGGER_DIR"
echo ""
echo "Next steps:"
echo "1. Enable triggers in Tuple:"
echo "   Tuple → Preferences (⌘,) → Triggers → Enable"
echo "2. Test with Tuple's simulator:"
echo "   Preferences → Triggers → Test Triggers → call-connected → Simulate"
echo ""
echo "Logs will be written to: ~/.tuple/triggers/triggers.log"
