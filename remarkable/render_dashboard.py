#!/usr/bin/env python3
"""Render week.md into dashboard PNGs for the rM2 (1404x1872).

week.md convention: a `# Week of ...` title line, then `## Meals`,
`## Events`, and `## Projects` sections. Meals and Projects are bulleted
lists; Events are one per line, `<when> — <what>`. All sections render onto
a single page (`dashboard-week.png`); an empty or missing section is simply
skipped, and if all are empty the page is too. Two static nudge pages are
always rendered.

Filename conventions rotate.sh depends on: the `dashboard-` prefix marks the
dashboard pool, and an `@<day>` suffix (lowercase `date +%a`: mon..sun) makes
an image eligible only on that day.

Run after render.py — render.py clears rendered/*.png when it starts.
"""

import re
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Pillow is required. Install with: pip3 install pillow")

CANVAS = (1404, 1872)
MARGIN = 140

FONT_PATH = "/System/Library/Fonts/Avenir.ttc"
BOOK = 0
BOOK_OBLIQUE = 1
HEAVY = 4
MEDIUM = 8

TITLE_SIZE = 96
WEEK_LABEL_SIZE = 40
SECTION_SIZE = 42
ITEM_SIZE = 58
ITEM_MIN_SIZE = 40
NUDGE_MAX_SIZE = 170
LINE_SPACING = 1.3


def font(size, index=BOOK):
    return ImageFont.truetype(FONT_PATH, size, index=index)


def line_height(fnt, spacing=LINE_SPACING):
    ascent, descent = fnt.getmetrics()
    return int((ascent + descent) * spacing)


def wrap_text(text, fnt, max_width, draw):
    out = []
    line = ""
    for word in text.split():
        candidate = (line + " " + word).strip()
        if draw.textlength(candidate, font=fnt) <= max_width:
            line = candidate
        else:
            if line:
                out.append(line)
            line = word
    if line:
        out.append(line)
    return out or [""]


def parse_week(md_text):
    week_label = ""
    m = re.search(r"^#\s+(.+)$", md_text, flags=re.MULTILINE)
    if m:
        week_label = m.group(1).strip()

    sections = {}
    for name, body in re.findall(
        r"^##\s+(\w+)\s*$(.*?)(?=^##\s|\Z)", md_text, flags=re.MULTILINE | re.DOTALL
    ):
        items = []
        for line in body.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            items.append(re.sub(r"^[-*]\s+", "", line).lower())
        sections[name.lower()] = items
    return week_label, sections


def start_page(title, week_label):
    img = Image.new("L", CANVAS, color=255)
    draw = ImageDraw.Draw(img)

    title_font = font(TITLE_SIZE, HEAVY)
    draw.text((MARGIN, MARGIN), title.lower(), font=title_font, fill=0)
    y = MARGIN + line_height(title_font, 1.15)

    if week_label:
        label_font = font(WEEK_LABEL_SIZE, BOOK_OBLIQUE)
        draw.text((MARGIN, y), week_label.lower(), font=label_font, fill=0)
        y += line_height(label_font, 1.2)

    y += 40
    draw.line([(MARGIN, y), (CANVAS[0] - MARGIN, y)], fill=0, width=3)
    return img, draw, y + 80


def save(img, out_dir, name):
    out = out_dir / name
    img.save(out, "PNG", optimize=True)
    print(f"  week.md → {name}")


def warn_overflow(name, y):
    if y > CANVAS[1] - MARGIN:
        print(f"  WARNING: {name} overflows by {y - (CANVAS[1] - MARGIN)}px", file=sys.stderr)


def render_week(sections, week_label, out_dir):
    meals = sections.get("meals", [])
    projects = sections.get("projects", [])
    events = []
    for line in sections.get("events", []):
        parts = re.split(r"\s+—\s+|\s+-\s+", line, maxsplit=1)
        events.append(parts if len(parts) == 2 else ("", line))

    bottom = CANVAS[1] - MARGIN
    for size in range(ITEM_SIZE, ITEM_MIN_SIZE - 1, -2):
        head_font = font(SECTION_SIZE, MEDIUM)
        fnt = font(size)
        when_font = font(max(28, int(size * 0.72)), MEDIUM)
        box = int(size * 0.75)
        gap = int(size * 0.5)
        sect_gap = int(size * 1.2)

        img, draw, y = start_page(week_label or "this week", "")

        def section(title):
            nonlocal y
            draw.text((MARGIN, y), title, font=head_font, fill=0)
            y += line_height(head_font, 1.15) + 8

        if meals:
            section("meals")
            for meal in meals:
                for line in wrap_text(meal, fnt, CANVAS[0] - 2 * MARGIN, draw):
                    draw.text((MARGIN, y), line, font=fnt, fill=0)
                    y += line_height(fnt)
                y += gap
            y += sect_gap

        if events:
            section("events")
            when_w = max(draw.textlength(w, font=when_font) for w, _ in events)
            what_x = MARGIN + int(when_w) + 50
            avail_w = CANVAS[0] - MARGIN - what_x
            for when, what in events:
                draw.text((MARGIN, y + 8), when, font=when_font, fill=0)
                for line in wrap_text(what, fnt, avail_w, draw):
                    draw.text((what_x, y), line, font=fnt, fill=0)
                    y += line_height(fnt)
                y += gap
            y += sect_gap

        if projects:
            section("projects")
            text_x = MARGIN + box + 36
            avail_w = CANVAS[0] - MARGIN - text_x
            for project in projects:
                box_y = y + (line_height(fnt) - box) // 2 - 6
                draw.rectangle(
                    [MARGIN, box_y, MARGIN + box, box_y + box], outline=0, width=4
                )
                for line in wrap_text(project, fnt, avail_w, draw):
                    draw.text((text_x, y), line, font=fnt, fill=0)
                    y += line_height(fnt)
                y += gap
            y += sect_gap

        y -= sect_gap + gap
        if y <= bottom:
            break

    warn_overflow("dashboard-week.png", y)
    save(img, out_dir, "dashboard-week.png")


def render_nudge(text, name, out_dir):
    img = Image.new("L", CANVAS, color=255)
    draw = ImageDraw.Draw(img)
    avail_w = CANVAS[0] - 2 * MARGIN

    size = NUDGE_MAX_SIZE
    while size > ITEM_MIN_SIZE:
        if draw.textlength(text, font=font(size)) <= avail_w:
            break
        size -= 4

    fnt = font(size)
    w = draw.textlength(text, font=fnt)
    lh = line_height(fnt, 1.0)
    draw.text(((CANVAS[0] - w) // 2, (CANVAS[1] - lh) // 2), text, font=fnt, fill=0)
    save(img, out_dir, name)


def main():
    here = Path(__file__).parent
    out_dir = here / "rendered"
    out_dir.mkdir(exist_ok=True)
    for old in out_dir.glob("dashboard-*.png"):
        old.unlink()

    week_path = here / "week.md"
    week_label, sections = ("", {})
    if week_path.exists():
        week_label, sections = parse_week(week_path.read_text())
    else:
        print("  no week.md — rendering nudge pages only", file=sys.stderr)

    if any(sections.get(k) for k in ("meals", "events", "projects")):
        render_week(sections, week_label, out_dir)

    render_nudge("plan your meals!", "dashboard-nudge@sun.png", out_dir)
    render_nudge("update me!", "dashboard-nudge@mon.png", out_dir)


if __name__ == "__main__":
    main()
