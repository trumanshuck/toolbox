#!/usr/bin/env python3
"""Render a curated subset of content/**/*.md into rendered/*.png for the rM2 (1404x1872).

Markdown convention: body of the file is the quote (any markdown). An optional
`---` line separates the body from an attribution on the line(s) below.

Source layout (selection rules below depend on this):
  content/
    parenting/<set>/<file>.md   — always selected
    favorites/<file>.md          — always selected
    poetry/<author>/<file>.md    — pool, filtered by line count, picked to
                                   balance the total card count

Selection: every parenting and favorites card is included unconditionally.
Extras are pulled from the poetry/ pool so that total poems == parenting count,
split evenly between author subdirs, choosing only poems short enough to render
comfortably (body line count <= MAX_POEM_LINES). Picks are randomized fresh on
each run.

Output filenames flatten path parts with `-`, so content/poetry/oliver/foo.md
becomes rendered/poetry-oliver-foo.png. The tablet shuffles regardless of name
order, so clustering by prefix doesn't affect rotation.

Layout modes (auto-detected from body content):
- **Literal** (body has any internal newline): preserve all whitespace, no
  word-wrap, hard line breaks honored. The block is centered horizontally as
  a unit so relative indentation reads correctly. Use this for poetry,
  e.e. cummings, or any quote where line breaks and spacing matter.
- **Wrap** (body is a single line): word-wrap to fit canvas width, each line
  centered individually. Use this for prose quotes.
"""

import random
import re
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Pillow is required. Install with: pip3 install pillow")

CANVAS = (1404, 1872)
MARGIN = 140
ATTRIB_GAP = 80
TARGET_FILL = 0.85
MIN_BODY_SIZE = 22
MAX_BODY_SIZE = 130
ATTRIB_SIZE = 38
ATTRIB_LINE_SPACING = 1.25

# Poems longer than this (non-blank body lines) are excluded from the pool —
# they fit, but the auto-sizer drops the body font below ~40pt which is hard
# to read at glance distance on the e-ink display.
MAX_POEM_LINES = 25

FONT_PATH = "/System/Library/Fonts/Avenir.ttc"
BODY_FONT_INDEX = 0    # Book
ATTRIB_FONT_INDEX = 1  # Book Oblique


def line_spacing_for(line_count):
    """Tighten leading as content gets denser so long poems still fit."""
    if line_count >= 30:
        return 1.10
    if line_count >= 22:
        return 1.16
    return 1.25


def parse_quote(md_text):
    parts = re.split(r"^---+\s*$", md_text, maxsplit=1, flags=re.MULTILINE)
    body_raw = parts[0]
    attribution = parts[1].strip() if len(parts) > 1 else ""

    # Drop blank lines at the start and end, but preserve indentation within.
    lines = body_raw.split("\n")
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    # Strip blockquote / heading markers per-line; leave other whitespace alone.
    cleaned = []
    for line in lines:
        line = re.sub(r"^>\s?", "", line)
        line = re.sub(r"^#+\s+", "", line)
        cleaned.append(line)
    return "\n".join(cleaned), attribution


def is_literal(text):
    """Treat a body as pre-formatted (no word-wrap) when it contains explicit
    line breaks. Single-line prose falls through to the wrapping path."""
    return "\n" in text


def wrap_text(text, font, max_width, draw):
    out = []
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            out.append("")
            continue
        words = paragraph.split()
        line = ""
        for word in words:
            candidate = (line + " " + word).strip()
            if draw.textlength(candidate, font=font) <= max_width:
                line = candidate
            else:
                if line:
                    out.append(line)
                line = word
        if line:
            out.append(line)
    return out


def layout_lines(text, font, max_width, draw):
    if is_literal(text):
        return text.split("\n")
    return wrap_text(text, font, max_width, draw)


def measure(lines, font, line_spacing):
    ascent, descent = font.getmetrics()
    line_height = int((ascent + descent) * line_spacing)
    height = line_height * len(lines)
    return height, line_height


def fit_body_size(body_text, max_w, max_h, draw):
    target_h = max_h * TARGET_FILL
    body_line_count = len(body_text.split("\n")) if is_literal(body_text) else 1
    line_spacing = line_spacing_for(body_line_count)
    lo, hi = MIN_BODY_SIZE, MAX_BODY_SIZE
    best = lo
    while lo <= hi:
        mid = (lo + hi) // 2
        font = ImageFont.truetype(FONT_PATH, mid, index=BODY_FONT_INDEX)
        lines = layout_lines(body_text, font, max_w, draw)
        max_line_w = max((draw.textlength(line, font=font) for line in lines), default=0)
        h, _ = measure(lines, font, line_spacing)
        if h <= target_h and max_line_w <= max_w:
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return best, line_spacing


def render(body, attribution, out_path):
    img = Image.new("L", CANVAS, color=255)
    draw = ImageDraw.Draw(img)
    avail_w = CANVAS[0] - 2 * MARGIN

    attrib_lines, attrib_h, attrib_lh, attrib_font = [], 0, 0, None
    if attribution:
        attrib_font = ImageFont.truetype(FONT_PATH, ATTRIB_SIZE, index=ATTRIB_FONT_INDEX)
        attrib_lines = wrap_text(f"— {attribution}", attrib_font, avail_w, draw)
        attrib_h, attrib_lh = measure(attrib_lines, attrib_font, ATTRIB_LINE_SPACING)

    body_avail_h = CANVAS[1] - 2 * MARGIN - (ATTRIB_GAP + attrib_h if attribution else 0)
    body_size, body_line_spacing = fit_body_size(body, avail_w, body_avail_h, draw)
    body_font = ImageFont.truetype(FONT_PATH, body_size, index=BODY_FONT_INDEX)
    body_lines = layout_lines(body, body_font, avail_w, draw)
    body_h, body_lh = measure(body_lines, body_font, body_line_spacing)

    total_h = body_h + (ATTRIB_GAP + attrib_h if attribution else 0)
    if total_h > CANVAS[1] - 2 * MARGIN:
        overflow = total_h - (CANVAS[1] - 2 * MARGIN)
        print(f"  WARNING: {out_path.name} overflows by {overflow}px at body size {body_size}", file=sys.stderr)
    y = (CANVAS[1] - total_h) // 2

    if is_literal(body):
        # Center the whole block, left-align lines within it so relative
        # indentation is preserved.
        block_w = max((draw.textlength(line, font=body_font) for line in body_lines), default=0)
        block_x = (CANVAS[0] - block_w) // 2
        for line in body_lines:
            draw.text((block_x, y), line, font=body_font, fill=0)
            y += body_lh
    else:
        for line in body_lines:
            w = draw.textlength(line, font=body_font)
            x = (CANVAS[0] - w) // 2
            draw.text((x, y), line, font=body_font, fill=0)
            y += body_lh

    if attribution:
        y += ATTRIB_GAP
        for line in attrib_lines:
            w = draw.textlength(line, font=attrib_font)
            x = (CANVAS[0] - w) // 2
            draw.text((x, y), line, font=attrib_font, fill=0)
            y += attrib_lh

    img.save(out_path, "PNG", optimize=True)


def body_line_count(md_path):
    body, _ = parse_quote(md_path.read_text())
    return sum(1 for line in body.split("\n") if line.strip())


def select_files(content_dir):
    """Build the selected file set per the rules in the module docstring.

    Total poems == parenting count. Favorites are always in; the remaining
    poem slots are split evenly between author subdirs under poetry/, drawing
    only from poems with <= MAX_POEM_LINES body lines.
    """
    parenting = sorted((content_dir / "parenting").rglob("*.md"))
    favorites = sorted((content_dir / "favorites").rglob("*.md"))

    need = len(parenting) - len(favorites)
    extras = []
    if need > 0:
        author_dirs = sorted(d for d in (content_dir / "poetry").iterdir() if d.is_dir())
        pools = [
            [p for p in sorted(d.rglob("*.md")) if body_line_count(p) <= MAX_POEM_LINES]
            for d in author_dirs
        ]
        # Balanced fill: try to take an even share from each pool. If a pool
        # is short, the slack flows to the others on the next round.
        remaining = need
        while remaining > 0 and any(pools):
            live = [p for p in pools if p]
            share = max(1, remaining // len(live))
            for pool in pools:
                if not pool or remaining == 0:
                    continue
                take = min(share, len(pool), remaining)
                picked = random.sample(pool, take)
                extras.extend(picked)
                for x in picked:
                    pool.remove(x)
                remaining -= take

    return parenting + favorites + extras


def main():
    here = Path(__file__).parent
    content_dir = here / "content"
    out_dir = here / "rendered"
    out_dir.mkdir(exist_ok=True)

    selected = select_files(content_dir)
    if not selected:
        sys.exit(f"No .md files selected from {content_dir}")

    for old in out_dir.glob("*.png"):
        old.unlink()

    for md in selected:
        rel = md.relative_to(content_dir).with_suffix("")
        out = out_dir / ("-".join(rel.parts) + ".png")
        body, attribution = parse_quote(md.read_text())
        render(body, attribution, out)
        print(f"  {md.relative_to(here)} → {out.name}")


if __name__ == "__main__":
    main()
