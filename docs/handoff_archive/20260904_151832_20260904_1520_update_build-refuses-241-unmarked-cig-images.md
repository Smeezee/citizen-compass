# Update — the build now REFUSES to ship. 241 registered CIG images carry no mark.

**2026-09-04 · Code**

**Stopped. Nothing deployed. This one is hard rule 8 and I am not touching it.**

## What changed under me, and it closed my own finding

At 12:15 I reported that `data-layer/cig_assets.json` did not exist, so
`tagged_count()` was 0, so `_SRC_BLOCK` was `None`, so **no page on the site
carried the source and takedown notice** - and that my `_SHIP_CONTENT_PAGES`
line was correct but inert until something registered assets.

**Something registered them.** That file was created at **14:25:20**:

    499 assets   258 models + 241 images
    sources      cig-fankit-restricted 466, cig-holoviewer 33

The source notice now renders. `_inspect.html` came out at **1,155,664 bytes**,
against 1,154,730 before - and C1's own simulation predicted 1,155,581 for "with
source notice". My line works. That gap is closed.

## And registering them opened a real one, which the build caught

    CIG require their mark in the corner of any image built from their
    assets, at no less than 50% opacity and a legible size. These are
    registered as CIG-sourced and do not carry it.

    Apply it with scripts/community_mark.py apply_mark(). Nothing was
    uploaded.

**241 images, every one scoring below the 0.50 threshold** - most at 0.000.
Talon_Shrike, Terrapin, Ursa, Valkyrie, Vanguard_Harbinger, Vulture, X1,
Zeus_Mk_II and 233 more.

The guard measures **the built pixels, not a flag**, so it also fires if the
compositing step stops running. It exits 1 and refuses the whole build. That is
correct behaviour and I am not going around it.

## Why I am not running `apply_mark()`

**Hard rule 8.** Fan Kit compliance is Sleven's alone: *"If you find a gap or an
error in one, report it - do not fix it."* Stamping CIG's mark onto 241 images
at a chosen opacity and size is a Fan Kit compliance act, not a build step,
however mechanical the command looks.

**Hard rule 5.** It is also a bulk mutation of 241 files. That needs a
report-only pass whose output Sleven has actually seen before anything is
written - and a 234-file in-place mutation has already happened in this repo
without one.

Either rule alone stops me. Both apply.

**What I am NOT saying:** anything about whether the mark is required, what it
should look like, or whether these images should be registered as CIG-sourced at
all. That is not a call I get to make and I am not making it sideways by acting.

## State, so nobody trusts a half-built payload

- **Nothing deployed.** The site still serves the payload from this morning.
- **`testing/_deploy` is mid-build.** The build wrote some outputs and then
  aborted at the guard, so the payload directory is neither the old state nor a
  complete new one. It must not be deployed until a clean build runs, and the
  sweep receipt will refuse it anyway - its fingerprint will not match.
- The inspector page itself is fine and now carries BOTH notices.

## What I cleared before hitting this

Both blockers I reported at 12:35 are resolved and green:

- **`_verify_holo_render.mjs`** asserted no style may be DoubleSide;
  `_verify_hull_is_solid.mjs` asserts every style must be. I inverted section 4
  to require it, on Sleven's go-ahead, with the measurement as the reason -
  3,287,114 of 139,487,571 triangles wound backwards across 258 models. **The
  guarantees that make it honest were kept, not traded:** every style still must
  draw an opaque surface or a depth pre-pass, and the saturation thresholds
  still hold at 0.00%-1.63% against 5%. All four mutators still exit non-zero.
- **`_verify_hull_is_solid.mjs`** had no machine-readable RULE16 label. Its
  author had already given the reasoning in prose, so I formatted it as
  `RULE16: INDEPENDENT` and signed the formatting as mine. Rule 16 gate: GREEN,
  0 gaps.

## What Sleven needs to decide

Whether to apply the community mark to those 241 images, and at what opacity and
size. Nothing ships until that is answered - not the inspector, not the
see-through fix, not anything else in the payload.
