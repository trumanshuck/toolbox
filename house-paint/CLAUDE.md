# house-paint

Bun + TypeScript runner for fanning out FLUX.2 image-edit jobs that re-imagine
the house in different exterior paint colors.

## Architecture

- **`run.ts`** — single-file runner. Reads `variations.yaml`, base64-encodes
  the source photo (and any per-variation reference images) into a FLUX.2
  request, submits async, polls the returned `polling_url`, downloads the
  signed result, and writes `outputs/<timestamp>/<name>.{png,json}`.
- **`variations.yaml`** — declarative list of named jobs (one per color scheme).
- **`.env`** — holds `BFL_API_KEY` (auto-loaded by Bun).

## The house (scene constraints — preserve in prompts)

Classic American Foursquare: grey hipped shingle roof with a central dormer,
red-brick chimney. The base photo (`IMG_2814.jpeg`) is a three-quarter view from
the front-left showing the concrete driveway and a detached garage at the rear,
with the neighbor's white house at the right.

**Material map (the model gets these wrong unless told — change COLOR, never the
material):**
- **Cedar-shake shingles** on the dormer and upper portion. FLUX tends to flatten
  these into lap siding — explicitly say to keep the shake texture.
- **Wood lap siding** on the main body (second floor + first-floor field).
- **Brick porch columns** and a **brick porch foundation**. FLUX tends to convert
  these to wood/smooth siding — explicitly say to keep them as brick.
- Currently white siding with charcoal-grey accents (the right-side wall and the
  band beneath the second-floor windows). The belt line under those windows is the
  natural divider for top/bottom two-tone schemes.

Prompts should change **only paint colors**, leaving every material and texture
intact. The user wants **two-tone** schemes (a body color plus a distinct second
color, often split top/bottom at the belt line). Everything else must be
explicitly preserved: the roof, chimney, all windows and glass, the porch
structure and concrete steps, the detached garage, the neighbor's house, the
driveway, the lawn and foundation plantings, the overhead power lines, the sky,
and the existing daylight, perspective, and shadows.

## API notes

- Endpoints in `MODEL_ENDPOINTS` (pro / max / klein).
- Auth header is `x-key`.
- Status terminal values: `Ready`, `Error`, `Failed`, `Content Moderated`,
  `Request Moderated`.
- Signed result URL is 10-min TTL — the runner downloads immediately.
