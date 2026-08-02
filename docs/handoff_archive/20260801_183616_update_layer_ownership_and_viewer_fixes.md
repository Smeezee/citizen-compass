# CORRECTION + two viewer fixes — `testing/_layer.html` is a build output, and I was writing the wrong file into it — 2026-08-02

Cowork session (Claude-03). This **supersedes the "restore three lost fixes" work order** filed by Claude-02. Do not execute that order. Read this first.

---

## 1. The three fixes were never lost. Nothing was rolled back.

Claude-02 read `testing/_layer.html`, found no `CC_NORM`, no `CC_LOOKUP`, no `CC_RSI`, and found `apply()` at line 628 above `let renderer,…` at 631, and concluded three recorded fixes had been reverted.

**Every one of those observations about the file was accurate. The conclusion drawn from them was wrong.**

Those three fixes do not live in the layer source. They are applied **at build time** by `build_machine_layer.py`, which:

- replaces the `let renderer,…` declaration with a comment and re-emits it in a header inserted near the top of the script — so in the built output the declaration is at line 477 and `apply()` at 660, in that order
- injects `CC_NORM`, `CC_LOOKUP`, `CC_RSI` and `CC_HAS3D`
- rewrites `decorate()` to match on the normalised name, capture the row's RSI anchor into `CC_RSI` before discarding it, and bind the click to the whole cell

Each substitution is guarded by an `assert` that the target text is present, so a drifted source fails the build loudly rather than silently emitting an unpatched page.

Verified in the built file: `CC_NORM` ×3, `CC_LOOKUP` ×2, `CC_RSI` ×5, `s.name===label` ×0.

**Nothing rolled back. Nothing needs restoring.**

## 2. The real defect, and it was mine

**I was pushing the layer *source* into `testing/_layer.html` instead of the layer *build output*.**

- Master source: `cc-testing-layer.html` — raw, unpatched by design
- Build output: `cc-testing-layer-fixed.html` — what `testing/_layer.html` must contain

Every push this session sent the first file. Confirmed by hash: `testing/_layer.html` on disk read `bb74ee72…`, byte-identical to my raw source, with `grep -c CC_NORM` returning 0.

### What that broke, and what it did not

- **`testing/_deploy/index.html` was always correct.** It is produced by `build_full.py`, which applies its own equivalents. This is why the shared preview link has worked throughout.
- **`testing/index.html` — the localhost page — was broken.** `build.py` injected the unpatched source, so `apply()` threw a TDZ ReferenceError at load and every statement after it never ran: no 3D viewer, no clickable rows, original RSI links live in the matrix.

**Claude-02's labelled inference was correct.** It reasoned from code, without running the page, that the symptom would be "old links to the RSI url" and no clickable ships. That is exactly right, and it is exactly what was reported.

### Fixed and verified on the machine

`testing/_layer.html` replaced with the build output, then `build.py` re-run on the machine itself:

```
layer  : testing/_layer.html   92,258 chars   CC_NORM=3 CC_RSI=5 openTok=8
output : testing/index.html   296,803 chars   CC_NORM=3 openTok=8
```

## 3. Two sessions were writing the same file

Claude-02 applied a blurred-backdrop change to `testing/_layer.html` at 01:10 UTC. I pushed over that path at 01:15. **That change is gone.**

It could never have survived regardless: on the machine `_layer.html` is a generated artifact, and every push from this session overwrites it wholesale.

**This is the same failure class as the double handoff writer** — two writers, one path, the later one silently discarding the earlier one's work. It cost ~37,000 characters per regeneration there. Here it cost a feature and a day of confusion.

### Ownership rule — adopt this

- **`testing/_layer.html` is a BUILD OUTPUT. Nobody hand-edits it.** Any edit is destroyed by the next push and cannot reach the deploy build.
- **`testing/_deploy/index.html` is a BUILD OUTPUT.** Same rule.
- **`testing/index.html` is a BUILD OUTPUT** of `build.py`. Already documented as "do not hand-edit."
- The source of truth is `testing/_src/_layer.src.html`, and changes to it go through the Cowork session that owns the build scripts.

## 4. A real risk this exposed — now closed

**The master source and all three build scripts existed only inside an ephemeral cloud session.** The machine had only compiled artifacts. If that session had ended, the layer source would have been unrecoverable and the project would have held nothing but built output.

Now on disk at `testing/_src/`:

```
_layer.src.html            the master source
build_machine_layer.py     -> testing/_layer.html
build_full.py              -> testing/_deploy/index.html  (models as separate files)
build_portable.py          -> single-file offline build   (models base64-embedded)
```

`testing/_src/` is not currently covered by the `testing/` gitignore rules. **It should be committed** — it is source, not artifact, and it is the only copy.

## 5. Two viewer bugs fixed this session (reported by Sleven)

### The previous ship's photo flashing on the new ship's page

Opening a ship set `still.style.opacity=1` **before** assigning the new `src`. An `<img>` keeps painting its previous frame until the new source decodes, so the element was forced to full visibility while still showing the last ship. Most obvious in the related-ships strip, where the "last ship" is the one you were just looking at.

Now: the still is blanked to a transparent 1×1 with the transition suppressed, and only fades in once the new image can actually paint (`decode()`, falling back to `onload`).

### A worse latent bug found alongside it — stale models

three.js has **no way to cancel an in-flight load**. A GLB requested for ship A completed seconds later and called `scene.add()` regardless of what page was open — so clicking through related ships faster than models download could render **ship A's model on ship B's page**, with B's name and B's price beside it. Never reported, but reachable today on any slow connection.

Every `open()` now takes a token; every async callback — model success, progress, error, image show, image error — checks it and does nothing if superseded. `close()` bumps the token so a late arrival cannot land on a closed page.

### Verification, hard rule 12

The bug does not reproduce on a local disk: the whole race window is under 10 ms. First attempt therefore "passed" on both the fixed and the broken build — a green result that proved nothing.

Redone properly: served over HTTP with route interception adding 700 ms to every thumbnail and 3 s to every model, and synthetic image/model fixtures created because the deploy assets are not present in the cloud workspace. A known-bad fixture was generated by reverting the two changed lines in the *built* page, with an assertion that the reversion actually applied.

Detector: frames where the still is visible **and** `img.complete` is false or `naturalWidth` is 0 — i.e. something is on screen that cannot be the current ship.

```
KNOWN-BAD : 457 frames (~3.7 s) of the previous ship on screen
FIXED     : 0 frames
```

**A first attempt that passes on both builds is not a passing test.** Recording that as its own lesson.

### Manufacturer tab dead on ship pages

`#cc-mtab` sits at z-index 100000 and stays visible over the ship overlay, but `#cc-mdraw` is at 99998 — *below* it. So the tab was visible, clickable, and opened a drawer behind the page: indistinguishable from a dead button.

Both are now hidden under `body.cc-ship-open`, and opening a ship force-closes the drawer so its offset state cannot persist. Verified: `getComputedStyle(#cc-mtab).display === 'none'` on a ship page.

## 6. Carried forward from Claude-02's report — still open, still valid

**Image provenance.** 241 `image.webp` files in `sc-ships/`, duplicated into `testing/_deploy/images/`, **with no record of where any of them came from** — no licence, no attribution, no manifest, no per-image metadata. The Fan Kit Agreement prohibits recoloring, distorting or outlining CIG assets, which bears directly on the blurred-backdrop idea. That question cannot be answered until the origin is established. Good catch; it stands regardless of what happens to the backdrop.

**Phase 1 / source 6.** Independently reported as still `blocked_missing_credentials`. Note that `scripts/external_sources/uex_corp.py` and `_verify_uex_corp.py` now exist on disk and `.env` was written after that report — so the state may have moved. **Verify before quoting either version.**

## 7. What Claude Code should NOT do

**Do not execute the "restore three lost fixes" order.** There is nothing to restore, and applying those fixes to the source would collide with the build scripts' `assert` guards and break all three builds.
