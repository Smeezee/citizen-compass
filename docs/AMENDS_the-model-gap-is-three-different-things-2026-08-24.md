# AMENDS — W1 and W2 of the walkthrough order were partly wrong. Corrected here.

**C1, 2026-08-24, after acting on it rather than reasoning about it.**
`ORDER_slevens-walkthrough-A-to-Anvil-2026-08-23.md` W1 and W2 were written from
what was on disk. **Both were wrong in ways that mattered.** Corrected below;
the order's other sections stand.

---

## What I got wrong, and what is actually true

### 1. "The download failed partway." NO. Three different things were happening.

**Sleven's instinct was right and my framing was wrong.** The upstream repo
`scsh/sc-ships` holds **245 ship folders. Our disk had 241.** But the four
missing were only ONE of three separate causes:

| cause | ships | fixable how |
|---|---|---|
| **Never downloaded** — complete upstream, absent locally | Arrow, Cutlass Black, Gladius, Constellation Aquila | **DONE — fetched 2026-08-24** |
| **No model upstream either** — the scrape failed at source | 85X, Arrastra, Fury, Mantis, Merchantman, PTV | **not obtainable from this repo** |
| **Model present, rescale never ran** | Asgard | re-run the rescaler |

**The six in the middle row are the important correction.** I reported them as a
failed download. **They are not on Hugging Face either.** Verified per folder
against the repo's own tree API:

    85X       -> image.webp ONLY.  No .ctm, no .glb.
    Arrastra  -> image.webp + model.ctm.  The .ctm is EXACTLY 262,144 bytes -
                 256 KB on the nose, which is a truncated fetch upstream, and
                 is why no .glb was ever produced from it.

**Our copy is a faithful mirror. Nothing was lost on our side.** For these six,
the Hugging Face route is exhausted and **RSI is the only remaining source** —
which is precisely what Sleven said before I checked.

### 2. "The Asgard's model.glb is corrupt." NO. The file is fine.

The 2026-07-30 rescale log says `[Asgard] CORRUPT - model.glb failed to load`.
**I quoted that as fact. It is not true of the file as it stands today.**

Re-downloaded the Asgard's `model.glb` from Hugging Face and compared:

    local  md5 34e80313c1aa3534f5ddd5d8259ea799
    fresh  md5 34e80313c1aa3534f5ddd5d8259ea799   <- byte-identical

    GLB magic 0x46546c67, version 2
    declared length 2,327,444 == actual file size    (exact)
    JSON chunk parses: 1 mesh, 4 accessors, 4 bufferViews
    buffer byteLength 2,326,196 == remaining bytes   (exact)
    extensionsRequired: none

**The file is well-formed by every structural check.** Whatever Blender choked
on in July is not present now — most likely the file was an unresolved git-LFS
pointer at the time and was fixed later.

**The Asgard needs no download. It needs the rescaler re-run, nothing else.**

---

## What was actually done, 2026-08-24

**Four ships added, each verified against the repo's stated byte size and its
GLB header before being accepted:**

    Arrow                  model.glb 12,551,468   image.webp   625,086
    Constellation Aquila   model.glb 15,394,964   image.webp   401,920
    Gladius                model.glb 12,100,692   image.webp   488,166
    Cutlass Black          model.glb  7,986,752   image.webp   761,690

**Cutlass Black and Gladius are the base hulls of families we already carry
four and three variants of.** They were the conspicuous absences.

`model.ctm` was NOT fetched for these four. It is the archival OpenCTM source
and nothing in the build reads it — `image.webp` is read only by
`build_portable.py`, `model_scaled.glb` by `build_deploy.py`. Fetch the four
`.ctm` files for folder parity when convenient; nothing is blocked on them.

**Two junk files are parked in `sc-ships/_to_delete/`** — a duplicate of the
Asgard model and one wrong copy from a mis-step of mine. **The device shell
cannot delete; remove that folder by hand.**

## THE ONE STEP THAT REMAINS, AND IT NEEDS A WINDOWS SHELL

Five ships now have `model.glb` and no `model_scaled.glb`:

    Arrow · Asgard · Constellation Aquila · Cutlass Black · Gladius

`rescale_all_ships.py` requires Blender, which is a Windows application and is
not reachable from the mounted Linux shell. It is idempotent — it rewrites
`model_scaled.glb` for every ship that has a `model.glb` — and it refuses to run
unless launched headless, by its own guard.

    CONTROL: after the run, assert all five have model_scaled.glb, and that the
    other 234 are byte-identical to before. The script rewrites everything; a
    changed file elsewhere means the scale factor moved and that is a
    fleet-wide regression, not a fix.
    CONTROL: the 2026-07-30 run reported 234 RESCALED, 7 MISSING, 1 CORRUPT.
    A correct run now reports 239 RESCALED and 6 MISSING, with NO corrupt
    entry. If Asgard reports CORRUPT again, the file is not the problem and
    the Blender importer is - say so rather than re-downloading.

## The rule this cost

**I read a log line that said CORRUPT and repeated it as a finding.** A log is a
record of what happened once, on a machine, in July. It is not a description of
the file today. **Re-check the artifact, not the report about the artifact.**
