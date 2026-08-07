# FINDING — why the cstone images load badly, and the four real image options

    from    C2, 2026-08-06
    for     C1 -> Claude Code, and to scope a CIC research dive
    trigger Sleven tested the wiki-source images and reported loading was
            "horrible". Diagnosed below. It is not the network.

---

## 1. THE DIAGNOSIS — they are not item images at all

From the sampled rows in `api.star-citizen.wiki/snapshots/20260801T021731Z`:

    "original_url":    "https://cstone.space/uifimages/<uuid>.png"
    "thumbnail_url":   "https://cstone.space/uifimages/<uuid>.png"   <- IDENTICAL
    "original_width":  3440,  "original_height": 1440
    "thumbnail_width": 3440,  "thumbnail_height": 1440   <- ALSO IDENTICAL

**Every "thumbnail" is the full-resolution file.** These are **3440×1440 PNG
screenshots** — ultrawide captures, lossless format, no resized variant of any
kind.

**A single one is plausibly several megabytes. A grid of twenty is tens of
megabytes over a third-party host we do not control.** That is the entire
explanation. **Nothing about the site or the browser is at fault.**

**Three separate problems stacked:**

    wrong content    a 3440x1440 ultrawide screenshot is not an item picture
    wrong format     lossless PNG for photographic content
    wrong host       hotlinked to a third party - no caching, sizing, or
                     format control, and their bandwidth bill, not ours

**Conclusion: cstone.space is not a delivery source and never can be.** Even
with permission it would be wrong to use this way. **Drop it from the design.**

---

## 2. THE FOUR REAL OPTIONS

### A — Extract icons from `Data.p4k` **(C2's recommendation)**

**The game ships an icon for every item, because the shop UI draws them.** Those
are CIG's own assets, which is precisely the granted class under RSI ToS
§XIII.D — *"images, graphics or artwork"* — for a free, ad-free fansite.

**A maintained tool already does the conversion.** `diogotr7/StarBreaker`,
v0.3.2, May 2026 — handles P4k, the DataCore `.dcb`, CryEngine geometry, and
**converts DDS textures to PNG** via a `--convert dds-png` flag. Also converts
`.cgf`/`.cga` geometry to **glTF/GLB**, which is separately the 3D viewer's
missing piece.

**We have already proven we can open this archive** — the `defaultProfile.xml`
extraction went through ZIP64 + ZStandard successfully.

    upside     licensed class, self-hosted, we control size and format,
               no third-party permission needed, one source for every item
    unknown    whether discrete per-item icons exist as separate textures,
               at what resolution, and what the join key to our UUIDs is
    cost       one extraction pass per patch

### B — Render from the models we now hold

`SGeometryResourceParams` in `items/*.json` gives an exact `.cga`/`.cgf` path
per item — present on ~92% of a sample. StarBreaker converts those to glTF/GLB,
and a headless Blender pass produces a consistent thumbnail per item.

    upside     total control, visually uniform, feeds the 3D viewer too
    downside   heavy, slow, and a rendering pipeline is real work
    verdict    the right long-term answer for SHIPS. Overkill for 7,728 items.

### C — The official RSI Fan Kit

**The one unambiguously licensed source, and nobody in this project has looked
at what is actually in it.** Almost certainly ship renders, logos and
manufacturer marks rather than item icons — **but that is an assumption, not a
check.** Cheap to settle and it should be settled.

### D — Community sources (cstone.space, the wiki, other tools)

**Rejected for delivery** per §1, independent of permission. **May still be
useful as a reference for what an item looks like while sourcing elsewhere.**

---

## 3. THE DELIVERY RULES — true regardless of which source wins

**Self-host. Never hotlink. Not once.**

**Pre-generate fixed sizes.** Three is usually right: ~64 px list icon,
~256 px card, ~1024 px detail. **Never ship one size and scale in CSS.**

**Modern formats.** AVIF primary with WebP fallback; JPEG/PNG only where
neither works. **PNG only for genuine flat-colour icons with transparency,
never for renders or screenshots.**

**Every `<img>` carries `loading="lazy"`, `decoding="async"`, and explicit
`width`/`height`** so the page does not reflow as images arrive.

---

## 4. THE CONSTRAINT NOBODY HAS CALCULATED — the file budget

**Cloudflare Pages, verified 2026-08-06: 20,000 files per site on the free plan,
100,000 on paid** (raised from 20,000 in January 2026; paid also needs
`PAGES_WRANGLER_MAJOR_VERSION=4`).

**Citizen Compass is on the free tier and the current budget is ~11,225 files
against 20,000.**

Naive image plan:

    7,728 items x 3 sizes x 2 formats  =  46,368 files
    plus the existing                     11,225
    -------------------------------------------------
    total                                 57,593   vs a 20,000 free cap

**It does not fit. It is not close. It exceeds even the paid tier's headroom
once ships and shops are added.**

**Four ways out, in preference order:**

1. **Sprite atlases for the small icons.** One sheet per category, hundreds of
   64 px icons per file. **Collapses thousands of files into dozens** and is the
   single biggest win available.
2. **One format, not two.** AVIF-only, with a per-item fallback generated only
   where actually needed. **Halves the count immediately.**
3. **Move images off Pages entirely** — R2 or a separate asset host — so the
   page budget stays for pages. **This is the architecturally clean answer and
   it should be seriously considered before generating anything.**
4. **Only generate images for items people search for.** The demand research
   already exists. **A long tail of 7,728 pictures nobody looks at is not worth
   a cent of complexity.**

**This calculation should be settled BEFORE any extraction runs**, because it
decides how many files get produced and in what shape.

---

## 5. WHAT THIS DOES NOT CHANGE

**The rights position is unaffected and unchanged:**

    CIG's own icons from Data.p4k    granted class under §XIII.D for a free,
                                     ad-free fansite. Sleven's advertising
                                     ruling keeps us inside it.
    CIG's written descriptions       still NOT granted. Text is not in the list.
                                     Unchanged.
    cstone.space images              third-party, permission never requested.
                                     Now moot for delivery, per §1.

---

## 6. NOT VERIFIED

- **Whether per-item icons exist as discrete textures in `Data.p4k`.** §2A rests
  entirely on this and it has never been checked. **If they do not, option B
  becomes the only self-sourced route.**
- **What is actually in the official RSI Fan Kit.** §2C. Never looked at.
- **StarBreaker's DDS→PNG output quality and whether it handles CIG's specific
  texture formats.** Documented, untested here.
- **Whether the icon naming joins to our UUIDs or class names** — if it joins by
  neither, matching becomes its own problem.
- **Cloudflare's per-file size limit.** The file *count* is confirmed; a
  per-file cap was not stated in the changelog.
- **Whether R2 or a separate asset host introduces cost.** Not priced.
