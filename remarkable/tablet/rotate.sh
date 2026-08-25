#!/bin/sh
# xochitl loads the suspend PNG at startup, not per-suspend — a restart is
# required after swapping current.png.
set -eu

DIR="${QUOTE_DIR:-/home/root/quote-display}"
IMAGES="$DIR/images"
STATE="$DIR/state"
CURRENT="$DIR/current.png"
SLOT="$DIR/slot"
DASH_INDEX="$DIR/dash-index"
LAST_SYNC="$DIR/last-sync"
AWAKE_THRESHOLD=30

# Usage: rotate.sh [--skip-if-active] [dash|quote]
# Without a slot argument, alternates dash/quote each run.
FORCE=""
skip_if_active=no
for arg; do
    case "$arg" in
        --skip-if-active) skip_if_active=yes ;;
        dash|quote) FORCE="$arg" ;;
    esac
done

if [ "$skip_if_active" = yes ]; then
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

today=$(date +%a | tr '[:upper:]' '[:lower:]')
synced_today=no
[ "$(cat "$LAST_SYNC" 2>/dev/null)" = "$(date +%Y-%m-%d)" ] && synced_today=yes

# Day gating must happen here at rotation time — a shuffle queue can outlive
# the day it was built on.
dash_candidates() {
    for f in "$IMAGES"/dashboard-*.png; do
        [ -f "$f" ] || continue
        case "$f" in
            *@"$today".png)
                [ "$today" = mon ] && [ "$synced_today" = yes ] && continue
                ;;
            *@*.png) continue ;;
        esac
        echo "$f"
    done
}

pick_dash() {
    set -- $(dash_candidates)
    [ $# -gt 0 ] || return 0
    i=$(cat "$DASH_INDEX" 2>/dev/null || echo 0)
    i=$(( i % $# ))
    j=0
    for f; do
        if [ "$j" -eq "$i" ]; then echo "$f"; break; fi
        j=$(( j + 1 ))
    done
    echo $(( i + 1 )) > "$DASH_INDEX"
}

shuffle_queue() {
    ls "$IMAGES"/*.png 2>/dev/null | grep -v '/dashboard-[^/]*\.png$' | \
        awk 'BEGIN{srand()}{print rand(), $0}' | \
        sort | cut -d' ' -f2-
}

pick_quote() {
    while :; do
        if [ ! -s "$STATE" ]; then
            shuffle_queue > "$STATE"
            [ -s "$STATE" ] || return 0
        fi
        t=$(head -n 1 "$STATE")
        tail -n +2 "$STATE" > "$STATE.tmp" && mv "$STATE.tmp" "$STATE"
        if [ -f "$t" ]; then echo "$t"; return 0; fi
    done
}

if [ -n "$FORCE" ]; then
    want=$FORCE
else
    last=$(cat "$SLOT" 2>/dev/null || true)
    if [ "$last" = "dash" ]; then want=quote; else want=dash; fi
fi

target=""
if [ "$want" = dash ]; then
    target=$(pick_dash)
    [ -n "$target" ] || want=quote
fi
if [ "$want" = quote ]; then
    target=$(pick_quote)
    if [ -z "$target" ]; then
        want=dash
        target=$(pick_dash)
    fi
fi
[ -n "$target" ] || exit 0
echo "$want" > "$SLOT"

cp "$target" "$CURRENT.tmp"
mv "$CURRENT.tmp" "$CURRENT"

systemctl restart xochitl
