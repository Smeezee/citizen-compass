# UPDATE — DEPLOYED and verified from the served site, not from an exit code

**Live: https://citizencompasstesting.citizencompass-contact.workers.dev**

## The deploy "failed" with exit 1. It had actually succeeded.

`scripts/deploy_testing.ps1` aborted and reported exit 1. **The deploy had
already completed.**

Windows PowerShell 5.1 wraps every stderr line from a native executable in an
ErrorRecord. wrangler wrote an ordinary **WARNING** to stderr — *"Preview URLs
will be enabled for this deployment by default"* — and my script's
`$ErrorActionPreference = 'Stop'` turned that warning into a terminating error,
**after** wrangler had uploaded all 477 files and published the version.

Confirmed against Cloudflare's own deployment list rather than guessed:

```
2026-08-02T04:29:38Z  Source: Upload               <- the pre-existing site
2026-08-02T05:59:39Z  Source: Unknown (deployment) <- this deploy
```

**This is the mirror image of the failure the order warns about.** The order
says do not report success from an exit code; this reported *failure* on a
success. Both come from trusting the wrapper instead of the result. Fixed:
`$ErrorActionPreference` is now `Continue` across the wrangler call, and the
exit code is the authority rather than the presence of stderr output.

## VERIFICATION — from the served site

**1. `index.html` serves.** HTTP **200 OK**, `text/html`, **1,507,473 bytes**.

**2. Byte-identical, three ways.** Raw bytes downloaded and hashed:

```
served sha256 : 62b22b7d1fdf83dfa5caf4045ceb1bd8e9e09d56d9a69e47e5f01e570d9207ea
local  sha256 : 62b22b7d1fdf83dfa5caf4045ceb1bd8e9e09d56d9a69e47e5f01e570d9207ea
your checksum : 62b22b7d1fdf83dfa5caf4045ceb1bd8e9e09d56d9a69e47e5f01e570d9207ea
```

The exact bytes you checksummed are the exact bytes being served. My first
attempt at this compared a *re-encoded* string and produced a mismatch — that
was a flaw in the check, not the deploy, so it was redone on raw bytes.

**3. Markers in the served page:** `id="cc-kb"` **1**, `cc-ship::after` **2**,
`cc-rel` **9**, `CC_EMBED` **5**, `keybinds.html` **0**. Your overlay,
compliance strip and Related-button clearance all shipped.

**4. Models genuinely serve — the silent-drop case is ruled out.**

| file | served | local | identical | header |
|---|---:|---:|---|---|
| `Hammerhead.glb` | 3,608,636 | 3,608,636 | **yes** | `glTF` |
| `Starfarer_Gemini.glb` | 5,478,516 | 5,478,516 | **yes** | `glTF` |

Byte-identical with valid glTF-binary magic headers, not merely a 200 with a
plausible size. `Starfarer_Gemini.glb` matches the order's stated largest file
exactly.

**5. `keybinds.html` → 404.** Correct: nothing references it, so your orphan
removal stands and no unreachable page ships.

**6. Password gate, from a genuinely clean context** — `WebClient`, no cookies,
no localStorage: gate markup present (`cc-gate` 15, `cc-pw` 6, `cc-locked` 5,
"Private preview" 1) and **the password literal appears 0 times** — only its
hash ships.

**But the gate is still not access control, and that is unchanged by the move.**
The same clean fetch returned "Ship Purchase Matrix" and the full inline
content. It hides the page from a browser visitor; it does not stop anyone
retrieving it. True on Netlify before, true here now — reported, not altered.

## A worker-name mismatch caught before it shipped

`wrangler.toml` said `citizen-compass-testing`; the live worker is
`citizencompasstesting`. **The Worker name is the subdomain**, so deploying
that would have published a **second site at a third URL**, left the live
testing site untouched, and reported complete success. Corrected before
deploying.

Same shape as the models case: command succeeds, output looks right, the thing
you cared about did not happen.

## Two URLs now serving — the human action this does not solve

| | |
|---|---|
| **new (Cloudflare)** | `citizencompasstesting.citizencompass-contact.workers.dev` |
| **old (Netlify)** | `citizen-compass-preview.netlify.app` — **still serving**, HTTP 200, frozen at v0.3.9 |

The credit limit blocks *deploys*, not *delivery*. So reviewers holding the old
link sit on a frozen build and will report bugs already fixed.

**Recording the new URL in `CURRENT-STATE.md` helps future sessions and does
nothing for those people.** A notice **cannot** be added to the old site —
Netlify deploys are exactly what is blocked. **Sleven telling them directly is
the only channel.** Stated as an open human action, not implied.

Recommendation, not acted on: leave the old site up until reviewers have moved,
then take it down. Taking it down now turns a stale-build problem into a
dead-link problem for people who have not been told yet.

## Credential

`CLOUDFLARE_API_TOKEN` written to `.env`, which was re-confirmed **untracked and
absent from HEAD at write time**. Verified by key name and length only
(**53**); the value has never been printed by me. `.env` remains gitignored and
unstaged.

**Rotation, as asked:** an earlier value was exposed in a chat transcript and
**rolled before first use**. No Cloudflare credential was ever written or used
here before this one — the two earlier attempts arrived as the literal
placeholder `<TOKEN>` and were refused rather than written. **The exposed value
was never live on this machine.** This replacement also arrived over chat, so it
is in a transcript too; rotate at your convenience, nothing depends on the value.

**The token was genuinely needed.** Before it existed, there was no
`config/default.toml`, no `CLOUDFLARE_*` env var, and only three wrangler
invocations ever logged on this machine — all from this session, two `whoami`,
no login and no deploy. The live site was not deployed from here.

Second defect in my own script, found by running it: it announced *"already
authenticated — no .env token needed"* when wrangler v4 had loaded that very
token from `.env`. The logic was right, the attribution was false. `.env` is now
read first so the script can say which credential is actually in use.

## Limits and headroom

| limit (free) | ceiling | now | headroom |
|---|---|---|---|
| files per version | 20,000 | 477 | **42x** |
| individual file | 25 MiB | 5.22 MiB | **4.8x** |
| static asset requests | *"free and unlimited"* | — | not a constraint |
| asset storage | *"no additional cost"* | 347.2 MB | not a constraint |

## Still open

- `CURRENT-STATE.md` does not exist; creating it with the new URL.
- `build_portable.py` still has 5 `/home/claude` refs and cannot run here.
- `.env` now holds **three** secrets on one machine with no backup (A3), and the
  UEX token remains unrotated after its own screenshot exposure.
