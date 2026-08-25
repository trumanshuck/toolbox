---
name: week
description: Interviews the household through the weekly plan — meals, events, projects — rewrites remarkable/week.md, renders the dashboard pages for review, and offers to sync the reMarkable. Use when the user invokes /week for the weekly planning ritual.
disable-model-invocation: true
---

# Weekly Planning Interview

Walk the user through planning the household week, then produce and preview
the reMarkable dashboard. Everything lives under `remarkable/` in this repo.
Output: a rewritten `remarkable/week.md`, fresh
`remarkable/rendered/dashboard-*.png`, and optionally a completed sync to the
tablet.

## Phase 1: Recall

Read `remarkable/week.md`. Note last week's meals and treat its projects as
carry-over candidates. If the file is missing, start a fresh interview.

## Phase 2: Interview

One section at a time, conversationally — this is a household chat, not a
form. An empty answer is fine anywhere: an empty section is simply left off
the dashboard.

1. **Meals** — ask for this week's picks (usually three, mix-and-match, not
   day-assigned). Mention last week's so repeats are deliberate.
2. **Events** — ask what's on this week. Normalize each line to
   `<when> — <what>` (e.g. `Wed 6:00p — soccer practice`);
   render_dashboard.py splits on the em dash to build the when/what columns.
3. **Projects** — list last week's projects, ask which carry over, then ask
   for new ones.

**Stop.** Read the plan back in brief and get a nod before writing.

## Phase 3: Write

Rewrite `remarkable/week.md` in exactly this shape. The title is the Monday
of the current week: today if it's Monday, otherwise the most recent Monday.

```markdown
# Week of Aug 24

## Meals

- tacos al pastor

## Events

Wed 6:00p — soccer practice

## Projects

- Paint the hallway trim
```

## Phase 4: Render and review

Run `python3 render_dashboard.py` from `remarkable/` (if Pillow is missing:
`pip3 install pillow`). Read the rendered `dashboard-week.png` and show it to
the user. Apply edits and re-render until they're satisfied.

## Phase 5: Sync

Offer to run `./sync.sh`. It touches the live tablet, so get explicit
confirmation first, and remind the user to wake the tablet and turn its
Wi-Fi on before agreeing. If ssh hangs or times out, the tablet is asleep or
Wi-Fi is still off — check with the user, then retry once. After a
successful sync, remind them to turn the tablet's Wi-Fi back off.

## Rules

1. Never invent meals, events, or projects — everything that reaches the
   tablet came from the user.
2. Keep each interview round to one short question; don't enumerate options
   for free-form answers.
3. Preserve the user's wording — the renderer handles styling; don't rewrite
   their text.
4. Don't run render.py or touch `content/` — quotes are out of scope here.

Start by reading `remarkable/week.md`.
