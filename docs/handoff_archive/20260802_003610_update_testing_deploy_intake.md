# UPDATE — deploying the testing site

Filed on intake per rule 13.

## Pre-stage re-hash — all three match

Re-hashed immediately before staging, as instructed, not just before deploying.

| file | expected == actual |
|---|---|
| `testing/_src/_layer.src.html` | `c26caed…6167634` YES |
| `testing/_layer.html` | `058d9ce…3582c65` YES |
| `testing/_deploy/index.html` | `be79501…08de8fb08` YES |

Landed 00:19:25-27, re-hashed 00:29:56 — stable for ten minutes, no drift.

## What is being deployed

Cloudflare Workers static assets, per `testing/wrangler.toml`:

- worker name **`citizencompasstesting`** — the name IS the subdomain, so this
  updates the existing site rather than creating a second one
- `testing/_deploy/` — 480 files, 349 MB, 235 `.glb` models
- **The live Netlify site is not touched by any of this.**

480 files is far inside the 20,000-file static-asset cap.

## What changed in this build

KEYBINDS and FIND moved from the right edge to a new left dock (`#cc-ldock`)
alongside MANUFACTURERS. DISPLAY and FEEDBACK stay on the right. The dock is
vertically centred rather than stacked downward from 44%, which is what put the
fifth tab at 1045px on a 1080px viewport.

Verified by Sleven at 1920x1080, 1600x900, 1366x768, 1280x720, 1024x600 and
390x844 — every tab on screen, zero overlaps, zero page errors.

## Verification plan — served bytes, not exit code

The deploy script has already reported **exit 1 on a fully successful deploy
once**, so the exit code is not trusted as evidence. After deploying I will
fetch from the served URL and confirm:

- index serves
- a model file serves with a plausible byte count
- the page contains `cc-ldock`, `cc-kb-tab`, `cc-fi-tab`, `cc-mtab`,
  `id="cc-kb"` and `cc-ship::after`
