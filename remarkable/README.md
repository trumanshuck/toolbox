# reMarkable Quote Display

Show rotating quotes on a sleeping reMarkable 2. Quotes live as markdown files
on your Mac, get rendered to PNGs, sync to the tablet over Wi-Fi, and the
tablet cycles through them by swapping its suspend image on a timer.

## How it works

- `~/.config/remarkable/xochitl.conf` on the tablet has
  `SleepScreenPath=/home/root/quote-display/current.png`, so xochitl uses
  `current.png` as its suspend image.
- A systemd timer (`WakeSystem=true`) runs `rotate.sh`, which picks the next
  image from `/home/root/quote-display/images/`, overwrites `current.png`,
  increments a sentinel index, and restarts xochitl (xochitl caches the
  suspend PNG at startup, so a restart is required to pick up the new file).
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

## Manual refresh

To force a fresh batch when the tablet is asleep:

1. Press the power button to wake the tablet (Wi-Fi comes up with it).
2. Run `./sync.sh` from the Mac.

## Tuning

- **Rotation cadence** — `tablet/quote-rotate.timer`. Default is `minutely`
  for testing; change to `hourly` (or `OnCalendar=*:0/15` for every 15
  minutes, etc.) and re-run `./install-tablet.sh` to redeploy.
- **Idle suspend delay** — set in `xochitl.conf` by `install-tablet.sh`
  (`IdleSuspendDelay=30000`, in ms). Shorter = device sleeps faster after
  each rotation but cuts your normal-use window; longer = more comfortable
  to use the tablet but more battery burned per rotation.
- **Fonts** — Avenir by default (ships with macOS). Edit `FONT_PATH` and
  the index constants at the top of `render.py` to swap.

## Files

```
config.sh                 # tablet IP, paths
quotes/*.md               # source quotes
render.py                 # md → 1404×1872 PNG (auto-fits font size)
sync.sh                   # render + rsync + remote rotate
install-tablet.sh         # one-time tablet setup
tablet/
  rotate.sh               # picks next image, updates current.png, restarts xochitl
  quote-rotate.service    # systemd oneshot
  quote-rotate.timer      # WakeSystem=true (minutely / hourly)
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
