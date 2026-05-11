#!/bin/sh
# Pick the next image, copy it to current.png, advance the shuffled queue,
# and restart xochitl so it re-caches the suspend image (xochitl loads it
# at startup, not at each suspend).
#
# $STATE holds the remaining shuffled queue (one path per line). When the
# queue is exhausted we regenerate a fresh shuffle of every PNG in $IMAGES.
# Result: every card is shown once before any repeats, and order is random.
#
# Pass --skip-if-active to skip if the device has been awake for more than
# AWAKE_THRESHOLD seconds — assumes that means the user is using it.
# Heuristic based on "PM: suspend exit" kernel log entries; the rotation
# will catch up on the next timer fire after the user puts the device down.
set -eu

DIR=/home/root/quote-display
IMAGES="$DIR/images"
STATE="$DIR/state"
CURRENT="$DIR/current.png"
AWAKE_THRESHOLD=30

if [ "${1:-}" = "--skip-if-active" ]; then
    last_resume=$(journalctl -b -k --no-pager -o short-unix 2>/dev/null | \
        grep "PM: suspend exit" | tail -1 | awk '{print $1}' | cut -d. -f1)
    if [ -n "$last_resume" ]; then
        awake_for=$(( $(date +%s) - last_resume ))
        if [ "$awake_for" -gt "$AWAKE_THRESHOLD" ]; then
            echo "rotate: skipping (awake ${awake_for}s, user likely active)"
            exit 0
        fi
    fi
fi

[ -d "$IMAGES" ] || exit 0

shuffle_queue() {
    ls "$IMAGES"/*.png 2>/dev/null | \
        awk 'BEGIN{srand()}{print rand(), $0}' | \
        sort | cut -d' ' -f2-
}

target=""
while [ -z "$target" ]; do
    if [ ! -s "$STATE" ]; then
        shuffle_queue > "$STATE"
        [ -s "$STATE" ] || exit 0
    fi
    target=$(head -n 1 "$STATE")
    tail -n +2 "$STATE" > "$STATE.tmp" && mv "$STATE.tmp" "$STATE"
    [ -f "$target" ] || target=""  # legacy/stale entry — try next
done

cp "$target" "$CURRENT.tmp"
mv "$CURRENT.tmp" "$CURRENT"

systemctl restart xochitl
