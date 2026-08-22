# FINDING — static-asset exposure on the deployed sites

**Date:** 2026-08-22
**Status:** MEASUREMENT ONLY. Nothing was changed. A5 of
`docs/ORDER_the-attribution-and-the-off-switch-2026-08-22.md` says the decision
is Sleven's and is a different call from the one he already made.

---

## 1. What was measured, and how

Every figure below came from **fetching the deployed site with `curl`**, not from
reading `wrangler.toml` or the build. Status codes, content types and byte
counts are what the servers actually returned on 2026-08-22.

### Testing site — `citizencompasstesting.citizencompass-contact.workers.dev`

| Path | Status | Content-Type | Bytes |
|---|---|---|---|
| `/` | 200 | `text/html` | 421,413 |
| `/loadout.html` | 307 → `/loadout` | — | — |
| `/loadout`, `/find`, `/keybinds`, `/holo`, `/download`, `/stick-test` | 200 | `text/html` | — |
| `/models/Avenger_Stalker.glb` | **200** | `model/gltf-binary` | 765,808 |
| `/images/100i.webp` | **200** | `image/webp` | 10,292 |
| `/fonts/ChakraPetch-SemiBold.woff2` | **200** | — | — |
| `/fonts/OFL.txt` | **200** | — | — |
| `/loadout_data.gen.js` | **200** | `text/javascript` | 3,636,252 |
| `/loadout_model.gen.js`, `/cc_viewer.js` | **200** | `text/javascript` | — |

**Every asset type on the testing site is directly fetchable: models, images,
fonts, and the generated data files.** No path tested returned 401, 403, or any
challenge.

### The password gate does not gate anything a fetch can see

This is the finding that matters most, and it is worse than
`CURRENT-STATE.md` recorded. That note said the gate "does not cover static
assets". Measured today, **it does not cover the HTML either.**

`GET /` with no password, no cookie and no session returned **421,413 bytes
containing the real site** — the served bytes carry `Avenger` 20 times,
`Hammerhead` 5, `Polaris` 5, `Redeemer` 6, alongside the string `Password`.

The gate is presentation-only. From `build_deploy.py`:

```
html.cc-locked body > *:not(#cc-gate){display:none !important}
...
function unlock(){ try{localStorage.setItem('ccGate','1');}catch(e){} ... }
var already = localStorage.getItem('ccGate')==='1';
```

It is a CSS rule that hides the page and a `localStorage` flag that stops hiding
it. The content is delivered to the browser **before** any password is entered.
`curl` receives all of it. So does View Source, DevTools, or typing
`localStorage.ccGate='1'` in a console.

That is a reasonable thing for a private preview to be — it keeps a casual
visitor out — but it should not be described as protecting anything, and it is
not protecting the models.

### Live site — `citizencompass.netlify.app`

| Path | Status |
|---|---|
| `/` | 200 — 205,362 bytes |
| `/models/Avenger_Stalker.glb` | **404** |
| `/models/Hammerhead.glb` | **404** |
| `/images/100i.webp` | **404** |

**The live site does not have this property.** It is one self-contained HTML
file, hand-deployed by Netlify Drop from `releases/latest.html`. A scan of the
served bytes found **no `src`/`href` reference to any `.glb`, `.webp`, `.png`,
`.jpg`, `.js` or `.css` file at all** — there are no separate assets to fetch
because there are none.

The exposure is a property of the testing site specifically, and it arrived with
the 3D viewer.

### Volume, measured on disk

| | Files | Total | Mean |
|---|---|---|---|
| `models/` | 235 | **341.8 MB** | 1,490 KB |
| `images/` | 241 | 4.0 MB | 17 KB |
| `fonts/` | 6 | 0.1 MB | 13 KB |

---

## 2. What a `Referer` / `Origin` check would take — and how weak it is

**Mechanically:** stop serving `models/` as static assets, add a Worker route
for `/models/*`, and have it compare the request's `Referer` or `Origin` header
against our own hostname before fetching the object and streaming it back. It is
maybe thirty lines. The build and the takedown would not need to change; the
`{file}` path template already goes through one seam.

**Honestly: it is very weak, and everyone who ships it knows that.**

- `Referer` and `Origin` are **client-supplied strings**. `curl -H "Referer:
  https://citizencompasstesting.citizencompass-contact.workers.dev/"` defeats it
  completely. This is one flag, not an exploit.
- The URL is in the page source either way. Anyone who can load the viewer can
  read the model URL, and anyone who can read it can send the header.
- It cannot distinguish our viewer from a script pretending to be our viewer,
  because there is nothing secret in the request to distinguish them by.
- Privacy modes, some proxies and some extensions strip `Referer`, so a strict
  check produces **real failures for real users** while stopping nobody who is
  actually trying.

What it genuinely does: stops **hotlinking** (someone else's page embedding our
model URLs and spending our bandwidth) and stops casual right-click-and-save
discovery. Those are real, but they are not "the files are protected", and the
record should not say they are.

Signed URLs with a short expiry are meaningfully stronger, and still cannot
survive one person opening DevTools. **No scheme that ends with a browser
decoding the mesh can prevent a determined person from keeping the bytes.** The
honest ceiling here is friction, not prevention.

**Note the tension with A4.** Anything that makes assets harder to serve also
adds a moving part between the takedown and the published site. The off switch
is worth more than the friction is.

## 3. What it would cost

**Bandwidth** is unchanged by any of this — the same bytes go out either way.
Measured: a model averages **1.49 MB**, so a visitor who looks at ten ships pulls
about **15 MB**. The full model set is **341.8 MB**.

**The real cost is that the bytes move from the static-asset path onto a
code path.** Today models are served as static assets. Routed through a Worker,
every model becomes a function invocation with CPU time attached, on an account
whose plan and limits I did **not** verify — I am not going to quote a price I
have not checked. What can be said without guessing is the shape: **request
count and CPU time go from zero to one-per-model-load**, and 235 objects at 1.49
MB each is a lot of streaming through a worker rather than past one.

**Complexity:** a new route, a new failure mode (models 403 while pages are
fine), a header-based bug class that will not reproduce in `curl` testing unless
you remember to send the header, and one more thing that has to be right during
a takedown.

---

## 4. Three options

### Option A — Change nothing. Record the property.

Add it to `CURRENT-STATE.md` and the punch list: the testing site serves models,
images, fonts and data openly, and the preview gate is cosmetic.

*For:* zero cost, zero new failure modes, nothing between the takedown and the
site. Matches what the site already is. *Against:* we remain the project in this
space that hands out model files, which is the difference A5 exists to put on
the record. Does nothing about hotlinking.

### Option B — Fix the description, not the exposure.

Leave the assets open, but stop the gate implying a protection it does not
provide: say "private preview" rather than "password", or move the testing site
behind something that actually authenticates (Cloudflare Access), which would
gate **pages and assets together** and needs no per-asset engineering.

*For:* small, honest, removes a false impression. Cloudflare Access is a
configuration change rather than a code path, and it does not stand between the
takedown and the site. *Against:* if Access is used, every previewer needs to be
let in individually — real friction for a site meant to be handed to a few
people. Does nothing for the live site later.

### Option C — Worker route on `/models/*` with a `Referer`/`Origin` check.

*For:* stops hotlinking and casual saving; it is what the rest of the community
does; it can be extended to signed URLs later. *Against:* trivially bypassed and
we would have to say so plainly; breaks for users whose `Referer` is stripped;
moves 341.8 MB onto a metered code path; adds a moving part to the one mechanism
that must work under pressure.

---

## 5. Recommendation

**Option B, and specifically the description half of it — now. Not Option C.**

The measurement says the most wrong thing on this site today is not that models
are fetchable. It is that **a gate is presenting itself as a password while
delivering the entire page to anyone who asks.** That is the same category of
defect this project spends its time hunting: something that reports a protection
it does not provide. It costs nothing to correct and it needs no new
infrastructure.

Option C should wait, for two reasons. First, it buys friction and not
protection, so shipping it would trade a real cost for a benefit we would then
have to describe honestly as small. Second, and more important: **no CIG-sourced
asset is on this site yet.** Every model currently served came from the
scunpacked pipeline. The exposure question gets sharper the moment the first
holoviewer asset lands — and that is exactly when the trade-offs should be
re-weighed, with the reconnaissance back that A4 was written ahead of.

If hotlinking becomes a measured problem rather than a hypothetical one, Option
C is a half-day and this document has the numbers ready.

**Not implemented. Awaiting Sleven's decision.**
