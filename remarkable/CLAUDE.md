# reMarkable Quote Display

Renders markdown quotes and a weekly household dashboard (`week.md`) to PNGs
on a Mac, syncs them to a reMarkable 2 over Wi-Fi, and the tablet cycles them
as its suspend image. See `README.md` for the full architecture and setup
steps before making changes.

## Two sides, different constraints

- **Mac side**: `render.py`, `render_dashboard.py`, `sync.sh`,
  `install-tablet.sh`, `content/`, `week.md`. Run here, edit freely.
- **Tablet side**: `tablet/rotate.sh`, `tablet/rotate-{dash,quote}.{service,timer}`.
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
- **Day gating must happen at rotation time, never at queue-build time.**
  The quote shuffle queue is built once and consumed over days, so
  `rotate.sh` evaluates `@<day>` filename suffixes fresh on every timer
  fire. Day-gated images must never enter the queue.
- **The tablet keeps Wi-Fi off.** No push or pull can be automated; updates
  land only during the manual sync ritual. All time/date logic must run on
  the tablet's own clock (RTC — fine at day granularity without NTP).

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
- Filename conventions `rotate.sh` depends on: a `dashboard-` prefix puts an
  image in the dashboard pool (round-robin, shown at :00 by
  `rotate-dash.timer`; quotes shuffle at :15 via `rotate-quote.timer`); an
  `@<day>` suffix (lowercase `date +%a`: `mon`..`sun`) limits it
  to that day. The `@` marker is what keeps quote names like
  `poetry-august-sun.png` out of the gating logic.
- `render_dashboard.py` must run after `render.py` (which clears
  `rendered/*.png` at startup). `sync.sh` already orders them correctly.
- `rotate.sh` is POSIX/busybox sh — no bashisms. Test locally with
  `QUOTE_DIR=<dir>` and a stubbed `systemctl` on `PATH`.

## Adding quotes

Drop `.md` files into `content/<set>/`. Body is the quote (markdown ok); an
optional `---` line separates body from attribution. No frontmatter.
