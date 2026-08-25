# reMarkable Quote Display

Show rotating quotes and a household dashboard (weekly meals, events,
projects) on a sleeping reMarkable 2. Content lives as markdown files on your
Mac, gets rendered to PNGs, syncs to the tablet over Wi-Fi, and the tablet
cycles through them by swapping its suspend image on a timer.

## How it works

- `~/.config/remarkable/xochitl.conf` on the tablet has
  `SleepScreenPath=/home/root/quote-display/current.png`, so xochitl uses
  `current.png` as its suspend image.
- A pair of systemd timers (`WakeSystem=true`) run `rotate.sh`, which picks
  the next image from `/home/root/quote-display/images/`, overwrites
  `current.png`, and restarts xochitl (xochitl caches the suspend PNG at
  startup, so a restart is required to pick up the new file).
  `rotate-dash.timer` fires at the top of each hour and shows a dashboard
  page (round-robin); `rotate-quote.timer` fires at :15 and shows a quote
  (shuffled, each shown once before any repeats) — so the household
  dashboard holds the screen for the first quarter hour and a quote holds
  the rest.
- After xochitl restarts, the short `IdleSuspendDelay=30000` (30s) makes it
  idle-suspend on its own — that's the path that actually paints the suspend
  image. External `systemctl suspend` does **not** trigger the paint, so we
  let xochitl drive its own sleep.
- E-ink holds the image at zero power, so the device displays the quote
  between rotations on roughly the same battery curve as a normal sleeping
  tablet.

## One-time setup

```bash
pip3 install pillow
./install-tablet.sh   # asks for the tablet's root password once
```

The tablet's root password is on the device under Settings → Help → About →
Copyrights and licenses. (Newer firmware also requires `rm-ssh-over-wlan on`
once via USB SSH to enable Wi-Fi SSH; the device shows the exact command on
that same screen.)

## Adding / changing quotes

Drop markdown files into `quotes/`. The body of the file is the quote
(markdown allowed); add an optional `---` line followed by an attribution.

```markdown
The only way out is through.

---

Robert Frost
```

Then:

```bash
./sync.sh
```

This renders, rsyncs, triggers an immediate rotation, and the tablet
idle-suspends ~30 seconds later showing the freshly-pushed quote.

## The household dashboard

`week.md` holds the week's meals, events, and projects; `render_dashboard.py`
turns it into one page per section (a section left empty or missing just
skips its page):

```markdown
# Week of Aug 24

## Meals
- tacos al pastor
- coconut chickpea curry

## Events
Wed 6:00p — soccer practice

## Projects
- Paint the hallway trim
```

Meals and Projects are bulleted lists (meals are the week's picks, not
day-assigned); Events are one per line as `<when> — <what>`.

Two static nudge pages are always rendered and only show on their day:
"plan your meals!" on Sundays and "update me!" on Mondays — the Monday nudge
stops appearing once you've synced that day. Day gating runs on the tablet's
own clock, so it works with Wi-Fi off.

The intended rhythm: plan the week Sunday/Monday, rewrite `week.md`, then
wake the tablet, turn its Wi-Fi on, run `./sync.sh`, and turn Wi-Fi back
off. Everything on the dashboard is week-scoped, so nothing goes stale
between syncs.

## Manual refresh

To force a fresh batch when the tablet is asleep:

1. Press the power button to wake the tablet (Wi-Fi comes up with it).
2. Run `./sync.sh` from the Mac.

## Tuning

- **Rotation cadence** — `tablet/rotate-dash.timer` (dashboard, :00) and
  `tablet/rotate-quote.timer` (quote, :15), hourly from 7am to 10pm ET.
  Edit the `OnCalendar` lines and re-run `./install-tablet.sh` to redeploy;
  keep fires ≳2 minutes apart (xochitl needs ~72s to repaint and suspend).
- **Idle suspend delay** — set in `xochitl.conf` by `install-tablet.sh`
  (`IdleSuspendDelay=30000`, in ms). Shorter = device sleeps faster after
  each rotation but cuts your normal-use window; longer = more comfortable
  to use the tablet but more battery burned per rotation.
- **Fonts** — Avenir by default (ships with macOS). Edit `FONT_PATH` and
  the index constants at the top of `render.py` to swap.

## Files

```
config.sh                 # tablet IP, paths
content/**/*.md           # source quotes
week.md                   # this week's meals / events / projects
render.py                 # quote md → 1404×1872 PNG (auto-fits font size)
render_dashboard.py       # week.md → dashboard + nudge PNGs
sync.sh                   # render + rsync + remote rotate
install-tablet.sh         # one-time tablet setup
tablet/
  rotate.sh               # picks from dashboard/quote pools, restarts xochitl
  rotate-dash.service     # systemd oneshot: rotate.sh dash
  rotate-dash.timer       # WakeSystem=true, hourly at :00
  rotate-quote.service    # systemd oneshot: rotate.sh quote
  rotate-quote.timer      # WakeSystem=true, hourly at :15
```

## Notes / gotchas

- **OS updates** rotate the SSH host key and the root password (your
  authorized_keys persists, so passwordless SSH keeps working). Expect a
  `REMOTE HOST IDENTIFICATION HAS CHANGED` warning after a firmware update;
  clear with `ssh-keygen -R <ip>`.
- **Wi-Fi SSH is off by default** on firmware 3.20+. Enable once via USB SSH
  with `rm-ssh-over-wlan on` (persists across reboots and updates).
- **If the timer doesn't actually wake the tablet** from suspend on your
  firmware, the fallback is an `rtcwake -m mem -s <interval>` loop instead of
  the systemd timer. Holler and we'll swap it in.
