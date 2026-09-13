# ORDER — I got the provenance wrong. Reverted. Rebuild, re-sweep, deploy testing.

From: C1 (Cowork), 2026-09-04
For: Code

## What I got wrong
I registered 499 assets as CIG-sourced using the rule "no `MODEL_SOURCE.txt` means
the RSI Fan Kit". **That was an assumption, not a reading**, and the evidence was on
disk the whole time:

    sc-ships/README.md       a Hugging Face dataset card - "Star Citizen Fan
                             Assets (Unofficial)", license: other
    sc-ships/.gitattributes  Hugging Face's standard LFS template
    sc-ships/index.json      245 entries

The whole `sc-ships` pack — models AND images — was downloaded from Hugging Face. It
did not come from the Fan Kit. `docs/workorder-image-provenance-and-renders.md` had
already established this and I did not read it before writing the register.

Worse: it is explicitly **not established** whether any individual image is a CIG
asset, a screenshot, or somebody's render. I registered them as CIG's anyway, which
caused CIG's "Made By The Community" mark to be stamped onto 241 images that may not
be CIG's at all. That is a compliance claim and it was never mine to make.

Your `_verify_community_mark.py` failure is what surfaced it. Sleven asked what the
hold-up was, I went looking, and the control was right.

## What has been reverted, and verified after
**The 241 images are unmarked again.** Restored from
`_to_delete/images_unmarked_20260904T204123Z/`. Re-scored: sampled 10, range
0.000–0.038, all back below the 0.50 threshold. The sources in `sc-ships/` were never
touched at any point.

**The register is corrected.** `scripts/correct_cig_register.py` (C1, new,
report-only by default):

    before   499 assets   258 models + 241 images
    after    258 assets   258 models + 0 images

    images UNREGISTERED   241   provenance not established - returned to unknown,
                                which is what is true. They are NOT being declared
                                non-CIG either; that would be the same error mirrored.
    models RELABELLED     235   'RSI Fan Kit' -> source cig-holoviewer,
                                origin "Hugging Face dataset ... via sc-ships pack"
    models unchanged       23   already carried a real MODEL_SOURCE.txt route

**The models stay registered and that is deliberate.** Their geometry is provably
RSI's holoviewer export — measured, not claimed: the Cutlass Black `.ctm` in this
pack matches the Fan Kit's at 149,983 vertices and 265,504 triangles exactly. Who
uploaded a file does not change whose geometry it is. Only the origin label was wrong.

Previous register preserved at `_to_delete/cig_assets.json.pre_correction_*`.

## Where `_verify_community_mark.py` stands now
Re-run from the Cowork VM: **5 failures before, 3 now.** The two that cleared are the
detector's own fixtures, which my marking had destroyed:

    before   unmarked fixture scored 0.9909 - it had been marked, so the negative
             control could not prove anything and the check correctly refused
    now      unmarked 0.0000, marked 0.9905, threshold 0.50, orientation margin 0.11

**The remaining 3 are "could not look" in MY environment, not proven defects.** All
three run a real build as their control and it dies at `FIND DATA GENERATION FAILED`,
which needs PostgreSQL. There is no PostgreSQL in the Cowork VM. **You have one — so
please re-run it and tell me what it says.** I am not claiming it passes; I am
claiming I fixed the part I could measure and cannot see the rest.

## RUN

```
python testing/_src/build_deploy.py
```

```
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1
```

The build should now report `community mark: 0 CIG-sourced images registered - guard
armed`, which is the correct state again — armed, with nothing to guard.

## VERIFY, rather than assume
- `_verify_community_mark.py` — say what it does on your machine either way
- `cc-src-note` still present on `_inspect.html`, `loadout.html`, `index.html`,
  `holo.html`. **It must be**: 258 models are still registered, so the notice still
  applies. If registering fewer assets has switched it off, that is a finding.
- `node checks/_verify_hull_is_solid.mjs` green
- `python checks/_verify_no_leaked_comments.py` green
- `python testing/_src/check_deploy_clean.py` green

## Then tell Sleven
`https://citizencompasstesting.citizencompass-contact.workers.dev/_inspect.html`

**TESTING ONLY. Live untouched.**

## Next, already decided by Sleven and not yours to start
Part 2 of the image work order: render our own thumbnails from the 258 models. That
removes the provenance question entirely rather than arguing it. C1 has a render
harness that produced 258 images with zero failures this morning. Sleven has been
told ours will look plainer than the current marketing-style shots and that he
compares before any swap.
