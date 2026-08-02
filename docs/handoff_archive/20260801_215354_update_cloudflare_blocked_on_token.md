# UPDATE — Cloudflare deploy built and verified; STOPPED, blocked on the API token

Everything that does not require the credential is done and proven. The deploy
itself cannot proceed: **no Cloudflare token exists and I cannot create one** —
that needs a dashboard login I do not have and should not have.

## THE BLOCKER

`.env` holds `DATABASE_URL` and `UEX_API_TOKEN` only — no Cloudflare key of any
kind. `npx wrangler whoami` reports *"You are not authenticated."*

**Sleven needs to create a scoped token** at
`https://dash.cloudflare.com/profile/api-tokens`, "Create Custom Token", with
exactly the minimum the addendum specifies:

```
Account | Workers Scripts | Edit
Account Resources: Include | <the Citizencompass account>
```

then add one line to `.env`:

```
CLOUDFLARE_API_TOKEN=<token>
```

**Please do not paste the token into chat.** Put it straight into `.env`. This
project has already had the UEX token exposed in a screenshot and it *still has
not been rotated* — no reason to repeat that. I never need to see the value; the
script reads it from `.env` and passes it via the environment only.

## THE BIG FINDING — `_deploy/` cannot be rebuilt on this machine at all

The order asked me to sweep `_deploy/` for files the build does not generate.
**The answer is all 477 of them**, and the reason is worse than the order
assumed.

`build_full.py` is hardcoded to a Linux cloud sandbox that does not exist here:

| path it requires | present? |
|---|---|
| `/home/claude/t128/node_modules/three` | **MISSING** |
| `/home/claude/model_files.txt` | **MISSING** |
| `/home/claude/cc-testing-layer.html` | **MISSING** |
| `/home/claude/latest.html` | **MISSING** |
| `OUT = /home/claude/full` | **MISSING** |

6 hardcoded `/home/claude` references. `build_portable.py` has 5 more.
`testing/build.py` writes `testing/index.html` — **not `_deploy/` at all**.

So the framing "a file the build does not generate will vanish on the next full
build" understates it. **No build on this machine produces `_deploy/`.** It is
not at risk of being overwritten — it is *unreproducible*. If those 477 files
were lost today they could not be regenerated here.

That is a real defect and it is bigger than this order. **Reported, not fixed** —
making `build_full.py` run on Windows means sourcing a three.js tree,
`model_files.txt`, and the two source HTML inputs, which is a separate job.

## `keybinds.html` — orphan status confirmed independently, then removed

Verified against the built page rather than accepted from the order:

| pattern in `_deploy/index.html` | count |
|---|---:|
| `id="cc-kb"` | 1 |
| `id="cc-kb-tab"` | 1 |
| `cc-ship::after` | 1 |
| `keybinds.html` | **0** |

Nothing anywhere in `_deploy/` references it. It is a self-contained in-page
overlay now.

**Decision: it does not ship.** Moved to
`_to_delete/keybinds_orphan_from_deploy_20260801/` — **moved, not deleted**, per
rule 1. `_deploy/` is 477 files now. No copy step was added; copying an
unreachable file into a deploy is not a fix.

**I left `testing/_src/keybinds.src.html` and `kb_overlay.inc.html` alone.** They
were written by Claude-02 **50 minutes ago** and are that session's live work.
Deleting another session's fresh source is exactly the coordination failure this
project keeps having. Whether the standalone source stays is Sleven's or
Claude-02's call, not mine.

## THE PASSWORD GATE IS NOT ACCESS CONTROL — and this predates the move

Correction 3 asked me to verify the gate survives the move. Examining it first
found something more important.

The gate is client-side only: an FNV-1a hash comparison (`H = 2714512690` over
`'cc-2026-' + password`) that adds a `cc-locked` CSS class and removes an
overlay div. **All 1.5 MB of page content — the full 254-ship matrix — is inline
in the HTML and is served to every unauthenticated request.**

Confirmed against the *existing live* preview: fetching
`citizen-compass-preview.netlify.app` with no stored state returned **200 OK**
and the complete ship matrix, alongside the *"Private preview. Enter the
password you were given."* prompt. The `/models/*.glb` files are likewise
directly addressable.

To be precise about what it does and does not do: **it stops a casual visitor in
a browser. It does not prevent anyone from retrieving the content.** That is
true on Netlify today and will be equally true on Cloudflare — the move neither
causes nor worsens it.

**Reported, not changed.** The password literal is not in the file (only its
hash), which is the one thing done right. Altering the gate is not in this
order's scope, and A5 explicitly says not to "fix" the per-origin storage
behaviour.

## The old Netlify preview IS still serving

The order said to find out rather than assume. **It serves: HTTP 200, title
"Citizen Compass v0.3.9".** So the credit limit blocks *deploys*, not
*delivery* — which is precisely the bad case Correction 2 describes: reviewers
will sit on a frozen v0.3.9 build indefinitely and report bugs that are already
fixed, with no signal to them or to us.

Not touched, not taken down. That is Sleven's call.

## Cloudflare limits — headroom, from current docs

Checked against Cloudflare's live documentation, not memory. Static hosting has
moved from Pages to Workers static assets, so the config is `[assets]` in
`wrangler.toml` and the command is `wrangler deploy`.

| limit (free plan) | ceiling | current | headroom |
|---|---|---|---|
| files per Worker version | **20,000** | 477 | **42x** |
| individual file size | **25 MiB** | 5.22 MiB (`Starfarer_Gemini.glb`) | **4.8x** |
| static asset requests | *"free and unlimited"* | — | not a constraint |
| asset storage | *"no additional cost"* | 347.2 MB | not a constraint |

**This confirms the order's premise:** Cloudflare states plainly that "Requests
to static assets are free and unlimited". The bandwidth reason for the move is
real, independent of the credit block.

The free plan's 100,000 requests/day applies to *Worker script invocations*.
This is an assets-only Worker with no script, and asset requests are the
unlimited category — but I have not been able to confirm by behaviour that no
invocation is counted, so treat that as documented-but-unverified.

## Built and proven

`testing/wrangler.toml` — assets-only, `workers_dev = true`, **no custom
domain** per A2.

`scripts/deploy_testing.ps1` — one step, with the final permission list in its
header so the token can be rotated without rediscovering what it needed.

Rule 12 on its guards, each driven with input that must fail:

| case | result |
|---|---|
| no `CLOUDFLARE_API_TOKEN` | **ABORT**, exit 1, with token-creation instructions |
| `CLOUDFLARE_GLOBAL_API_KEY` present | **ABORT**, exit 1 — refuses a Global key outright |
| models folder empty | **ABORT**, exit 1 — the silent-success case |
| valid payload, `-WhatIf` | exit 0, **nothing uploaded** |

The dry run was proven by behaviour, not by reading it — the lesson from
`setup_checks_task.ps1` earlier today.

Payload measured before upload: **477 files, 347.2 MB, 235 `.glb` models,
largest `Starfarer_Gemini.glb` at 5.22 MB** — matching the order's 5,478,516
bytes exactly.

## What is NOT done

The deploy, both URLs, the second-deploy URL-stability check, and the served
verifications (index, `id="cc-kb"`, `cc-ship::after`, a real model file, the
gate). All of it waits on the token.

`CURRENT-STATE.md` **does not exist anywhere in the repo**. I will create it
with the new URL once there is one.

## Open human actions — stated plainly, not implied

1. **Create the scoped token** and put it in `.env` (above).
2. **Tell the reviewers directly.** Recording the new URL in `CURRENT-STATE.md`
   helps *future sessions only*. It does nothing for people already holding the
   Netlify link, and **a notice cannot be added to the old site, because Netlify
   deploys are exactly what the credit limit blocks.** Sleven is the only
   channel to those people.
3. **The UEX token is still unrotated** after being exposed in a screenshot.
4. **`.env` will hold three secrets and has no backup.** It is gitignored, so it
   exists in exactly one place on one machine, and it compounds with the open
   offsite-backup gap. Flagged per A3, not solved. Whoever solves it: encrypted
   store or password manager only — a secrets file inside an unencrypted backup
   is worse than none, because it feels solved.
