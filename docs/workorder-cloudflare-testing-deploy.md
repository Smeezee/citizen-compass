# WORK ORDER — one-command deploys for the TESTING site, on Cloudflare

Supersedes the earlier draft of this order. Three corrections are folded in and marked. Verified against the machine 2026-08-02.

Hard rule 13 applies: file an `inbox/` update on intake, on completion, and on any stop.

---

## SCOPE — read this first

Set up one-command deployment for the **testing/preview** site to Cloudflare.

**Do not touch the live site.** `citizencompass.netlify.app` stays exactly as it is, on Netlify, deployed by hand. Netlify deploys are currently blocked by an account credit limit; that is being waited out deliberately and is not part of this job.

## Why Cloudflare, beyond the credit block

**349 MB of ship models is bandwidth-heavy and Cloudflare's free tier does not meter bandwidth. Netlify's does.** Even with Netlify unblocked, this is the better host for this specific content. The credit limit is the trigger, not the reason.

Today the testing site is a manual drag of a 478-file, 349 MB folder into a browser tab. Slow, prone to stalling, and a single point of failure.

---

## WHAT TO BUILD

**1. Install and configure `wrangler`.**

```
Cloudflare account : Citizencompass.contact@gmail.com
Account ID         : ad974500ce73c9694e94213c4d762f3e
Project name       : citizen-compass-testing
```

**2. Deploy `C:\Users\david\citizen-compass\testing\_deploy` as a static site.**

Verified shape: **478 files, 349 MB, largest single file 5,478,516 bytes (`models/Starfarer_Gemini.glb`).** Entry point `index.html`.

**Check Cloudflare's current documentation before choosing the command.** They have moved static hosting from Pages to Workers static assets and the dashboard now presents it as "Create a Worker." Do not assume syntax from memory.

**3. Wrap the command in a script** — `scripts/deploy_testing.ps1` or an npm script, whatever fits the repo. One step.

---

## CORRECTION 1 — the keybinds requirement was written against a superseded design

The earlier draft required `keybinds.html` to be reachable at `/keybinds.html`, and asked for a build step to copy it into `_deploy/`. **Both are wrong now.**

Verified in the current `testing/_deploy/index.html` — the file that would actually ship:

```
id="cc-kb"          1   overlay present
id="cc-kb-tab"      1   tab present
cc-ship::after      1   compliance strip present
keybinds.html       0   nothing references it
```

There is also **no `fetch()` or any other runtime reference** to that filename anywhere in the built page. The keybinds tab is now a **self-contained in-page overlay**. `testing/_deploy/keybinds.html` is a 25 KB orphan.

**So:**

- **Do not add a copy step for it.** Copying an unreachable file into a deploy is not a fix.
- **Decide its fate and say which you chose:** if the standalone page has no remaining purpose, remove it from `_deploy/` and from `testing/`; if it is still wanted as a directly-linkable reference, wire a link to it in the layer source so it is reachable, then add the copy step.
- Either way, `build_full.py` currently emits only `index.html`. Whatever you decide, the build must produce it — nothing should exist in `_deploy/` because a human once put it there.

**The general defect the original order was right about still stands:** a file present in `_deploy/` that the build does not generate will vanish on the next full build with no error. Sweep `_deploy/` for anything else in that category and report what you find.

---

## CORRECTION 2 — the URL migration is the thing that will actually bite

The earlier draft verified the URL is stable *across redeploys*. It did not address that **Cloudflare issues a completely new URL, and everyone who has the Netlify preview link is still pointed at the old one.**

That is worse than a dead link. **If the Netlify site keeps serving, reviewers sit on a frozen build indefinitely and report bugs that are already fixed** — and neither they nor you would have any signal that is what is happening.

**Required, before reporting done:**

- Report both URLs: the old Netlify preview and the new Cloudflare one.
- Establish whether the old preview is still serving. **A credit limit that blocks deploys may or may not block delivery — find out rather than assume.**
- **Do not take the old site down or change it.** That is Sleven's call, and it involves people he has to notify.
- Recommend one of: take it down, or leave it with a visible notice pointing at the new URL. State the trade-off. Do not act on it.

---

## CORRECTION 3 — verify the password gate survives the move

Not mentioned in the earlier draft. The preview sits behind a browser-side gate (`apples`).

Nothing about changing hosts should break it — but nothing has confirmed it either, and **the failure mode of that gate is that a stranger discovers it, not you.** Your own browser may hold the unlock in local storage and show you an open site that is closed to everyone else, or vice versa.

**Fetch the deployed page in a clean context** — no stored state — and confirm the gate blocks. Then confirm the password lets you through.

---

## CREDENTIALS

The Cloudflare API token goes in `.env`, already gitignored, already holding `UEX_API_TOKEN` and `DATABASE_URL`.

**Confirm `.env` is still untracked, not merely ignored, before writing to it.** The token must never reach the repo, a log, a manifest, or a console echo.

---

## VERIFY — HARD RULE 12

Do not report this working from a successful command exit.

1. **Fetch the deployed URL** and assert `index.html` serves — not a 404, not a Cloudflare placeholder.
2. **Assert the served page contains `id="cc-kb"` and `cc-ship::after`.** Both verified present in the current build. If either is missing, the wrong build shipped.
3. **Confirm a model serves** — e.g. `/models/Hammerhead.glb` returns 200 with a plausible byte count. **A deploy that silently dropped the models folder would otherwise look like a complete success**, because the page still loads and still looks right.
4. **Confirm the password gate**, per Correction 3, from a clean context.
5. **Deploy a second time and confirm the URL is unchanged.** A URL that moves on every deploy defeats the entire purpose.
6. If you kept `keybinds.html`, fetch it and assert it serves and is linked from the page. If you removed it, assert it 404s and that nothing links to it.

---

## ALSO — commit `testing/_src/`

It holds the master layer source and all three build scripts, is not gitignored, and **is currently the only copy.** Until today it existed nowhere but an ephemeral cloud session.

**Note for whoever picks this up:** `testing/_src/_layer.src.html` is actively edited by more than one session. Check its modification time before assuming your copy is current — this has already caused one near-miss where work was nearly overwritten.

---

## REPORT BACK

- The deployed URL, and the old Netlify one for comparison.
- The exact redeploy command.
- Whether the second deploy reused the same URL.
- What you decided about `keybinds.html` and why.
- Whether the old Netlify preview is still serving.
- **Cloudflare limits that will bite later** — file count ceiling, per-file size, request limits, and anything about the free tier that changes as the models folder grows. 478 files and 5.2 MB max are comfortable today; say how much headroom there is.

## BOUNDARIES

Live site, `static/preview.html`, `releases/latest.html`, the database and all source snapshots are out of scope and must not be touched.

**Commit:** the wrangler config, the deploy script, the `build_full.py` fix, `testing/_src/`.
**Do not commit:** `.env`, `testing/_deploy/`, anything under `sc-ships/`.

---

# ADDENDUM — credentials, domain, and the two-URL problem

## A1. Scope the API token. Do not use a Global API Key.

A Global API Key in `.env` grants **full account access, including DNS and billing.** Create a scoped token instead.

**Start from the minimum — `Account → Workers Scripts → Edit`, on this one account — and add a permission only when a deploy actually fails without it.** Do not grant a broader set preemptively on the theory that it will probably be needed.

Record the exact final permission list in the deploy script's header, so the token can be rotated later without rediscovering what it needed.

## A2. No custom domain on this project.

A domain purchase (`citizencompass.net`) is being considered separately. If it happens, **the testing site belongs on `testing.<domain>` and the apex stays reserved for the real site.**

Stay on the `.workers.dev` address. Configure no custom domain.

## A3. Flag, do not solve — `.env` will hold three secrets and has no backup

After this it carries `DATABASE_URL`, `UEX_API_TOKEN` and a Cloudflare token. It is gitignored, which is correct, and therefore **exists in exactly one place on one machine.**

Note it in your report and move on. Two constraints for whoever does solve it:

- **It must be an encrypted store or a password manager.** Do not copy `.env` anywhere in plaintext, and make sure no future backup job sweeps it up — a secrets file inside an unencrypted backup is worse than no backup, because it feels solved.
- **It compounds with the still-open offsite backup gap.** If that machine dies today, the secrets and the data go together.

Separately outstanding and not part of this order: **the UEX token was exposed in a screenshot and still has not been rotated.**

## A4. The Netlify preview stays — and marking it only solves half the problem

`citizen-compass-preview` on Netlify is superseded for testing. **Do not delete it.**

Record in `CURRENT-STATE.md` which URL is the live testing site, so two addresses do not end up circulating.

**Be explicit in your report about what that does and does not fix.** Marking `CURRENT-STATE.md` tells future *sessions* which URL is current. It does nothing for the people already holding the old link. And **a notice cannot be added to the old Netlify site, because Netlify deploys are precisely what the credit limit is blocking.**

So the only channel to those reviewers is Sleven telling them directly. Say that plainly rather than leaving it implied — an unstated dependency on a human action is how a task gets marked done while nothing actually happened.

## A5. Noted, no action needed

The password gate stores its unlock in local storage, which is **per-origin**. Every reviewer re-enters the password once on the new URL. **Expected, not a bug. Do not "fix" it.**
