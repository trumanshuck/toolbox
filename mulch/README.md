# mulch

Re-imagining the deck-side mulch beds with different landscape treatments using
BFL's FLUX.2 image-edit API.

## Setup

```bash
cd mulch
bun install
cp .env.example .env   # paste your BFL_API_KEY
```

## Usage

Edit `variations.yaml` — list each treatment as a named entry with a prompt
(and optionally extra reference images for materials). Then:

```bash
bun run run.ts                     # uses variations.yaml
bun run run.ts other-config.yaml   # different config
CONCURRENCY=5 bun run run.ts       # crank parallelism
```

Outputs land in `outputs/<timestamp>/<name>.png` along with a `.json` sidecar
recording the prompt, source, endpoint, and signed result URL (10-min TTL —
the PNG itself is already saved locally).

## Reference images

- `ref-1.jpeg` — side angle, mulch bed dominant (good base for new ground covering)
- `ref-2.jpeg` — looking back at house, paver path + daylily bed
- `ref-3.jpeg` — side angle from yard side
- `ref-4.jpeg` — deck-down view, planters + umbrella
- `ref-5.jpeg` — deck-down looking across lawn

## Models

- `flux-2-max` — final picks
- `flux-2-pro-preview` — iteration (default)
- `flux-2-klein-preview` — throwaway grids

## Notes

- The runner assumes multi-image fields are named `input_image`, `input_image_2`,
  `input_image_3`, … which matches BFL's FLUX.2 multi-image format. If a future
  API revision renames these, adjust in `run.ts`.
- Kontext-lineage models degrade after ~6 turns of edits; once a direction is
  settled, save the winner and start a fresh thread rather than stacking edits.
