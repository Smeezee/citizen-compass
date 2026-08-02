# UPDATE — your trademark change verified in source; found and fixed a 404 it would have shipped. Deploy still not run.

## THE HEADLINE: NOTHING IS LIVE. I cannot confirm the change is deployed.

I ran `scripts/deploy_testing.ps1` as asked. **It aborted, exit 1** —
`CLOUDFLARE_API_TOKEN` is still not in `.env`, which holds only `DATABASE_URL`
and `UEX_API_TOKEN`.

So there is no deployed site to check the change against. **I am not reporting
this as done, and the earlier `<TOKEN>` placeholder was never written.**

Also worth stating precisely: `testing/_deploy/` is **gitignored**, so an updated
`index.html` cannot arrive here by `git pull`. The file did change on this
machine (22:27:04), but nothing was pushed to me — I am reading local disk.

## YOUR CHANGE IS REAL AND IT IS IN THE SOURCE

The trademark bar was not lost, it was **reimplemented**: `cc-ship::after` (the
pseudo-element) is gone and `cc-tm` (5 references) replaces it, with `trademark`
10→12, `Trademark` 1→4 and `sticky` 10→12. That matches "the ship page now ends
above the sticky trademark bar instead of running under it."

**And it is reproducible.** Rebuilt from `_layer.src.html` in an isolated
fixture and compared marker-for-marker against your file:

| marker | your file | rebuilt from source |
|---|---:|---:|
| `cc-tm` | 5 | 5 |
| `id="cc-kb"` | 0 | 0 |
| `cc-ship::after` | 0 | 0 |
| `keybinds.html` | 1 | 1 |
| `KEYBINDS` | 1 | 1 |

Exact on all five. The change lives in the layer source, so a rebuild will not
silently undo it — which was the first thing I checked, because that is the
defect this whole order exists around.

## THE PROBLEM I FOUND — and it would have deployed silently

**The design flipped back, and I had removed the file it now needs.**

Correction 1 told me the keybinds tab was a self-contained in-page overlay and
`keybinds.html` was a 25 KB orphan. Verified at the time and true then:
`id="cc-kb"` 1, `keybinds.html` 0. I moved the orphan to `_to_delete/`.

Your update reverses that: `cc-kb` references drop **128 → 6**, the in-page
overlay is gone, and the page **links to `keybinds.html` again**.

Which I had removed. **The KEYBINDS tab would have 404'd on the live site** — and
nothing about a successful `wrangler deploy` would have revealed it. The page
loads, looks correct, and one tab is dead.

## THE FIX — in the build, not by hand

The order's own condition applies: *"if it is still wanted as a directly-linkable
reference, wire a link to it in the layer source so it is reachable, then add the
copy step."* The link is now wired in the source, so the copy step is correct.

I did **not** hand-copy the file back. The order is explicit that nothing should
exist in `_deploy/` because a human put it there. `build_deploy.py` now emits it,
and decides by reading the built page rather than by assumption:

- page **links** `keybinds.html` → build emits it from `testing/_src/keybinds.src.html`
- page **does not link** it → build **removes** any stale copy, so an earlier
  design cannot leave an orphan behind
- linked but **source missing** → build **fails loudly** rather than publishing a
  dead link

The two files are byte-identical (25,106), so the source genuinely regenerates
what I had moved aside.

**Rule 12, all three directions proven in the fixture:**

| case | result |
|---|---|
| linked | `keybinds.html` emitted |
| not linked, stale copy present | stale copy **removed** |
| linked, source missing | **exit 1**, refuses, no page written |

That last one matters most: it converts "dead link ships silently" into "build
stops".

## Current payload

**478 files, 347.2 MB, 235 `.glb`, `index.html` 1,488,997 bytes**, largest asset
`Starfarer_Gemini.glb` at 5.22 MB. Rebuild reports `unmatched: 6` — 85X,
Arrastra, Fury, Mantis, Merchantman, PTV — the same six the auditor layer
reaches independently.

## One discrepancy I could not resolve, stated rather than smoothed over

My rebuild from the current layer is **1,488,997** bytes; the file you left was
**1,480,972** — 8,025 bytes apart, despite every marker matching. So your
`index.html` was probably not produced by `build_deploy.py` from this exact
layer — possibly built elsewhere, or before a later tweak. Functionally
equivalent on every check the order specifies, but not byte-identical, and I
would rather say so than call it a match.

**The deployable artifact is now the rebuilt one**, since that is the one whose
provenance I can demonstrate and whose links resolve.

## Still blocked

The token. `CLOUDFLARE_API_TOKEN=<real value>` straight into `.env` — please not
into chat, since a chat transcript is what burned the previous one. Then say the
word and I will deploy and run the full verification: index serves, `cc-tm`
present, **a real model file returns 200 with a plausible byte count**,
`keybinds.html` resolves, the gate blocks from a clean context, and a second
deploy keeps the same URL.
