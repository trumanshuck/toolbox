# reMarkable Quote Display

Renders markdown quotes to PNGs on a Mac, syncs them to a reMarkable 2 over
Wi-Fi, and the tablet cycles them as its suspend image. See `README.md` for
the full architecture and setup steps before making changes.

## Two sides, different constraints

- **Mac side**: `render.py`, `sync.sh`, `install-tablet.sh`, `content/`. Run
  here, edit freely.
- **Tablet side**: `tablet/rotate.sh`, `tablet/quote-rotate.{service,timer}`.
  Deployed to `/home/root/quote-display/` on the rM2 by `install-tablet.sh`.
  Editing these files locally has no effect until they're redeployed.

## Things that will bite you

- **xochitl rewrites `xochitl.conf` on exit.** Any config edit must happen
  while xochitl is stopped, or it gets clobbered. `install-tablet.sh` already
  handles this — preserve that pattern in any script that touches the conf.
- **xochitl caches the suspend PNG at startup.** Swapping `current.png`
  isn't enough; xochitl must be restarted to re-read it. `rotate.sh` does
  this.
- **External `systemctl suspend` does not paint the suspend image.** Only
  xochitl's own idle-suspend path (driven by `IdleSuspendDelay`) actually
  renders the PNG to the e-ink display. Don't replace the idle-suspend flow
  with a manual suspend trigger.
- **Tablet root filesystem is read-only.** Anything that writes outside
  `/home/root/` needs `mount -o remount,rw /` first.

## Don't run these without asking

- `./sync.sh` and `./install-tablet.sh` both touch the live tablet (SSH,
  rsync, systemd changes, xochitl restart). Confirm before running.

## Render specifics

- `render.py` auto-picks layout mode from the body: any internal newline →
  literal (preserve whitespace, no wrap), single line → wrap. Don't
  "normalize" multi-line quotes — the line breaks are intentional (poetry).
- Font path is macOS-specific (`/System/Library/Fonts/Avenir.ttc`). Rendering
  won't work on Linux without changing `FONT_PATH`.
- Output filenames flatten subfolder paths with `-`, so
  `content/poetry/frost.md` → `rendered/poetry-frost.png`. PNGs from the
  same subfolder sort together in the rotation.

## Adding quotes

Drop `.md` files into `content/<set>/`. Body is the quote (markdown ok); an
optional `---` line separates body from attribution. No frontmatter.
