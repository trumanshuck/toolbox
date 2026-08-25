# house-paint

Re-imagining the house in different exterior paint colors using BFL's FLUX.2
image-edit API.

## Setup

```bash
cd house-paint
bun install
cp .env.example .env   # paste your BFL_API_KEY
```

## Usage

Edit `variations.yaml` — list each color scheme as a named entry with a prompt
that locks in everything except the painted siding. Then:

```bash
bun run run.ts                     # uses variations.yaml
bun run run.ts other-config.yaml   # different config
CONCURRENCY=5 bun run run.ts       # crank parallelism
```

Outputs land in `outputs/<timestamp>/<name>.png` along with a `.json` sidecar
recording the prompt, source, endpoint, and signed result URL (10-min TTL —
the PNG itself is already saved locally).

## Photos

- `IMG_2814.jpeg` — three-quarter front-left, full facade + driveway/garage (base photo)
- `IMG_2815.jpeg` — near straight-on frontal, cleanest facade view
- `IMG_2816.jpeg` — angled from the left, more foreground landscaping
- `IMG_2817.jpeg` — wide street view
- `IMG_2818.jpeg` — close yard view, house cut off at top

## Models

- `flux-2-max` — final picks (default here; best at preserving architectural detail)
- `flux-2-pro-preview` — fast iteration
- `flux-2-klein-preview` — throwaway grids

## Notes

- The runner assumes multi-image fields are named `input_image`, `input_image_2`,
  `input_image_3`, … which matches BFL's FLUX.2 multi-image format. If a future
  API revision renames these, adjust in `run.ts`.
- Kontext-lineage models degrade after ~6 turns of edits; once a direction is
  settled, save the winner and start a fresh thread rather than stacking edits.
