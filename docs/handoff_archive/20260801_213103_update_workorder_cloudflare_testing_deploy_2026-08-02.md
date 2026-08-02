# UPDATE — work order issued: automate testing-site deploys via Cloudflare

Claude-02, 2026-08-02. Work order only. Nothing built, no commits, no pushes.

## Decision on record

Sleven's call: automate deployment for the **testing site only**, on Cloudflare.
The live site stays on Netlify and stays manual. Netlify production deploys are
currently blocked by an account credit limit — that is being waited out
deliberately, not worked around, and the live site is unaffected because
published sites stay up.

## Why this came up

Deploying the testing site is a hand-drag of 478 files / 349 MB into a browser
upload widget. It stalled tonight. The browser tab is a single point of failure
for a 358 MB transfer, and the whole loop of "build something, look at it live,
iterate" depends on that step working.

## The order, in brief

Set up wrangler for project `citizen-compass-testing` on the Cloudflare account
`Citizencompass.contact@gmail.com` (account id `ad974500ce73c9694e94213c4d762f3e`),
deploying `testing/_deploy/` as a static site with `index.html` as entry and
`keybinds.html` reachable at `/keybinds.html`. Wrap it in a one-step script.

**Check Cloudflare's current docs before choosing a command.** Static hosting has
moved from Pages to Workers static assets and the dashboard now presents it as
"Create a Worker". The syntax should be read, not recalled.

API token goes in `.env` (already gitignored, already holds `UEX_API_TOKEN` and
`DATABASE_URL`). Never into the repo, a log, or a manifest.

## Bundled fix — a silent failure already armed

`build_full.py` generates `testing/_deploy/` and does **not** copy
`keybinds.html` into it. That file is currently present only because it was
placed by hand. The next full build drops it with no error and the KEYBINDS tab
404s.

Add: `testing/_src/keybinds.src.html` -> `testing/_deploy/keybinds.html`

Also: `testing/_src/` holds the master layer source and all three build scripts,
is not gitignored, and is the only copy. It should be committed.

## Verification required — rule 12

A zero exit code is not proof. The order requires fetching the deployed URL and
asserting: index serves, `/keybinds.html` serves, the served index contains
`id="cc-kb"` and `cc-ship::after`, a model file returns 200 with a plausible
size, and a second deploy reuses the same URL rather than minting a new one.

The model check matters — a deploy that silently drops the 358 MB models folder
would otherwise present as success.

## Boundaries

Live site, `static/preview.html`, `releases/latest.html`, database and all source
snapshots out of scope. Commit the wrangler config, deploy script, the
`build_full.py` fix and `testing/_src/`. Do not commit `.env`, `testing/_deploy/`
or anything under `sc-ships/`.

## Context for whoever picks this up

A `testing/_deploy_lite/` folder also exists — 243 files, 6 MB, same site without
the models. Created so the operator could get a working deploy up in seconds
while the full upload was stalling. It is a convenience copy, not a build output,
and nothing generates it.
