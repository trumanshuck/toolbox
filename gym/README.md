# gym

Kettlebell-day timer for the old iPad mini 2 (iOS 12) in the basement: a big tap-to-start clock with an optional 30-second chime, and paddles to step through the exercises and their paired stretches.

`index.html` is the whole app. Edit `STEPS` in its script to change the session.

## Getting it onto the iPad

1. Run `python3 serve.py` on the Mac.
2. On the iPad (same Wi-Fi), open the printed `http://<mac>.local:8000/` in Safari, then Share > Add to Home Screen.

AppCache (`app.appcache`) keeps the page on the iPad, so the Mac only needs to be serving when you push an update.

## Updating

Bump the `# v` line in `app.appcache`, run `serve.py`, and open the app on the iPad twice: the first launch downloads the new version, the second shows it.
