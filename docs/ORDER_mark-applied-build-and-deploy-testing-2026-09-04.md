# ORDER — the community mark is on all 241. Build and deploy TESTING.

From: C1 (Cowork), 2026-09-04
For: Code

## Your block is cleared
You refused the build because 241 registered CIG images carried no mark, scoring
mostly 0.000 against the 0.50 threshold. **That refusal was correct and it is the
third time today stopping rather than acting caught something real.** You were right
not to run `apply_mark()` yourself — hard rule 8 and hard rule 5 both applied.

Sleven made the call and saw the report before anything was written.

## What was done
`scripts/mark_ship_images.py` (C1, new). Report-only is its default; `--write` is one
flag. Sleven saw the report and a before/after render of the Vulture plus the corner
at 4x before authorising.

    mark      MadeByTheCommunity_White.png
    opacity   0.70   against CIG's 0.50 floor
    size      22% of the short side, 64px floor -> 69px on every image
    placement bottom-right corner, 8px margin

Nothing about opacity, size or placement was chosen here. All of it comes from
`scripts/community_mark.py`, which follows
`docs/FINDING_hologram-display-concept-2026-08-08.md`. No recolour, no flip, no
distortion, nothing drawn on top — those are structural in `apply_mark()`, not
comments.

## Result, re-scored independently afterwards rather than trusted

    marked                     241
    below the 0.50 threshold   0
    min 0.940   median 0.997   max 0.999

    all 241 readable, all still 560x315, 6.4 MB total
    241 unmarked originals preserved in _to_delete/images_unmarked_<TS>/
    sc-ships/*/image.webp UNTOUCHED - 245 still there, so any image can be
    re-derived from source at any time

Every image is the same 560x315, so the mark is identical on all of them. There were
no oversized or odd cases to judge.

## RUN

```
python testing/_src/build_deploy.py
```

```
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1
```

The build should now print `community mark: 241 CIG-sourced image(s), all carry it`.

## VERIFY AFTER, rather than assume
- `community mark` line reports 241 and all carrying it
- `cc-src-note` present in `_inspect.html`, `loadout.html`, `index.html`, `holo.html`
  — it reached 4 of 4 on your last build; confirm it held
- `node checks/_verify_hull_is_solid.mjs` green
- `python checks/_verify_no_leaked_comments.py` green
- `python testing/_src/check_deploy_clean.py` green

If anything still refuses, stop and say so. Three gates have fired today and each one
was real.

## Then tell Sleven
`https://citizencompasstesting.citizencompass-contact.workers.dev/_inspect.html`

**TESTING ONLY. Live is untouched.**

## One thing for later, not now
`build_ship_thumbs.py` derives 340px thumbnails from these images for the front-page
CONCEPT pages. Those are not shipped, so nothing is blocked — but a thumbnail shrinks
the mark with it, and if a concept page ever becomes the real front page the mark's
legibility at that size is a question for Sleven. Noted so it is not discovered late.
