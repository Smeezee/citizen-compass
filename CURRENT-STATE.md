# CURRENT STATE — which URL is which

Last updated 2026-08-02.

**This file tells future sessions which address is current. It does nothing for
people who already hold an old link.** See the note at the bottom.

---

## Testing / preview site — CLOUDFLARE (current)

```
https://citizencompasstesting.citizencompass-contact.workers.dev
```

- Cloudflare Workers static assets. Worker name **`citizencompasstesting`** —
  the Worker name *is* the subdomain, so changing it publishes a different site
  rather than updating this one.
- Deploy with **one command**: `powershell -File .\scripts\deploy_testing.ps1`
- Config: `testing/wrangler.toml`. Serves `testing/_deploy/` (477 files,
  ~347 MB, 235 `.glb` models).
- **No custom domain**, deliberately. If `citizencompass.net` is bought, the
  testing site belongs on `testing.<domain>` and the apex stays reserved for the
  real site.
- Behind a browser-side password gate. **The gate is not access control** — the
  full page content is inline and served to any request; it hides the page from
  a casual browser visitor and nothing more. True on the old host too; the move
  neither caused nor worsened it.
- Why Cloudflare: Cloudflare states *"Requests to static assets are free and
  unlimited"* with *"no additional cost for storing Assets"*. 347 MB of ship
  models is bandwidth-heavy. The Netlify credit block was the trigger; unmetered
  bandwidth is the reason.

## Testing / preview site — NETLIFY (superseded, still serving)

```
https://citizen-compass-preview.netlify.app
```

- **Still returns HTTP 200**, frozen at **v0.3.9**. The Netlify credit limit
  blocks *deploys*, not *delivery*.
- **Do not delete it.** Superseded for testing, but people hold this link.

## Live site — NETLIFY (out of scope, unchanged)

```
https://citizencompass.netlify.app
```

- Hand-deployed via Netlify Drop from `static/preview.html` mirrored into
  `releases/latest.html`. **Not** built or deployed by anything in
  `scripts/deploy_testing.ps1`.

---

## OPEN HUMAN ACTION — this file does not close it

Anyone already holding the Netlify preview link is on a **frozen v0.3.9 build**
and will report bugs that are already fixed, with no signal to them or to us.

**A notice cannot be added to the old site, because Netlify deploys are exactly
what the credit limit blocks.** So the only channel to those reviewers is
**Sleven telling them directly.**

Recommendation, not acted on: leave the old site up until reviewers have moved,
then take it down. Taking it down now converts a stale-build problem into a
dead-link problem for people who have not been told yet.

## Cloudflare free-tier headroom

| limit | ceiling | now | headroom |
|---|---|---|---|
| files per Worker version | 20,000 | 477 | 42x |
| individual file size | 25 MiB | 5.22 MiB (`Starfarer_Gemini.glb`) | 4.8x |
| static asset requests | free and unlimited | — | not a constraint |
| asset storage | no additional cost | 347 MB | not a constraint |
