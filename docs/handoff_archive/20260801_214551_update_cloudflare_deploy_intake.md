# UPDATE — Cloudflare testing-site deploy order received; starting

Filed on intake per rule 13, before any work.
`docs/workorder-cloudflare-testing-deploy.md`, read in full **including the
ADDENDUM** — A1–A5 are part of the order, not background.

## What this is, and what it is not

One-command deploys for the **TESTING** site on Cloudflare. The live Netlify
site (`citizencompass.netlify.app`) is **out of scope and stays hand-deployed**.

The Netlify credit limit is the **trigger**, not the reason. The reason is that
**349 MB of ship models is bandwidth-heavy and Cloudflare's free tier does not
meter bandwidth** — so this is the better host for this content even once
Netlify is unblocked.

## Verified before starting

| check | result |
|---|---|
| node | v24.18.0 |
| npm | 11.16.0 |
| wrangler | 4.118.0 (via `npx`) |
| `.env` gitignored | yes — `.gitignore:4` |
| `.env` **tracked** | **no** — `git ls-files` finds nothing |
| `testing/_deploy` | present |

The order asks for `.env` to be confirmed **untracked, not merely ignored**.
Both were checked separately; ignored and untracked are different properties and
a file can be the first without being the second.

## `_layer.src.html` — mtime checked first, as instructed

`testing/_src/_layer.src.html` last modified **2026-08-01 20:59:20**, ~45 minutes
ago, by another session. Not currently in flight, but I will **re-check its mtime
immediately before any edit** rather than trusting this reading — the order
records a near-miss where work was nearly overwritten.

## Order of work

1. Independently verify the `keybinds.html` orphan claim against the built
   `index.html` — confirm rather than accept — then decide its fate.
2. Sweep `_deploy/` for **anything else the build does not generate**. That is
   the general defect: such files vanish on the next full build, silently.
3. Scoped Cloudflare token, starting at **`Account → Workers Scripts → Edit`**
   only, widening solely when a deploy actually fails. **Never a Global API
   Key** — that grants DNS and billing.
4. Check Cloudflare's **current** docs before choosing the command; static
   hosting moved from Pages to Workers static assets. Not from memory.
5. `scripts/deploy_testing.ps1`, one step, with the final permission list in its
   header.
6. Rule 12 verification, and the one that matters most: **confirm a model file
   actually serves.** A deploy that silently dropped the 349 MB models folder
   still loads and still looks right, and would read as a complete success.
7. Password gate verified from a **clean context, no stored state** — my own
   browser may hold the unlock and show me an open site that is closed to
   everyone else.

## Constraints I am holding to

- **No custom domain.** Stay on `.workers.dev` (A2).
- **Do not delete or modify the old Netlify preview** (A4). Recommend only.
- Live site, `static/preview.html`, `releases/latest.html`, the database and all
  source snapshots are untouched.
- Do not commit `.env`, `testing/_deploy/`, or anything under `sc-ships/`.

## One thing I already know I must state plainly, not imply

Recording the new URL in `CURRENT-STATE.md` helps **future sessions only**. It
does nothing for reviewers already holding the Netlify link, and **a notice
cannot be pushed to the old site, because Netlify deploys are exactly what the
credit limit blocks.** The only channel to those people is Sleven telling them
directly. That will appear in my report as an **open human action**, not as a
solved item.
