# toolbox

A collection of scripts and utilities for macOS automation.

## Tools

### tuple-recording

Automatically record Tuple calls using MacWhisper. When a Tuple call connects, MacWhisper starts recording. When the call ends, recording stops.

**Prerequisites:**
- MacWhisper installed and running with menubar icon visible
- Tuple installed with triggers enabled
- Accessibility permission granted to Terminal (System Settings → Privacy & Security → Accessibility)

**Installation:**

```bash
cd tuple-recording
./install.sh
```

**Setup:**

1. Run `./discover-menu-items` to verify MacWhisper's menu item names match the scripts
2. If the menu items differ, update `MENU_ITEM` in `call-connected` and `call-ended`
3. Enable triggers in Tuple: Preferences (⌘,) → Triggers → Enable
4. Test with Tuple's simulator: Preferences → Triggers → Test Triggers → Simulate

**Logs:** `~/.tuple/triggers/triggers.log`
