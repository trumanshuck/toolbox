# mulch

Bun + TypeScript runner for fanning out FLUX.2 image-edit jobs that re-imagine
the deck-side mulch beds with different landscape treatments.

## Architecture

- **`run.ts`** — single-file runner. Reads `variations.yaml`, base64-encodes
  the source photo (and any per-variation reference images) into a FLUX.2
  request, submits async, polls the returned `polling_url`, downloads the
  signed result, and writes `outputs/<timestamp>/<name>.{png,json}`.
- **`variations.yaml`** — declarative list of named jobs.
- **`.env`** — holds `BFL_API_KEY` (auto-loaded by Bun).

## Scene constraints (preserve in prompts)

Cable-rail deck with composite decking, yellow steel raised planters, black
chain-link fence, multi-trunk shrub, daylilies along a curved paver edging,
dark navy siding. Prompts should explicitly call these out as preserved so the
edit only touches the wood-chip mulch beds.

## API notes

- Endpoints in `MODEL_ENDPOINTS` (pro / max / klein).
- Auth header is `x-key`.
- Status terminal values: `Ready`, `Error`, `Failed`, `Content Moderated`,
  `Request Moderated`.
- Signed result URL is 10-min TTL — the runner downloads immediately.
