# Memo

To:      Owner
From:    Build
Subject: Phase one of the images, models and dimensions audit is in - one report and five CSVs, read-only, nothing corrected
Status:  Open

**Phase one is in.** You asked me to tell you when it was. Phase two, the external dimension research, has not started. It starts when you say so.

**Nothing in the scope needed a tool or an access I lacked.** I did not report back before starting because there was nothing to report.

    report   claude/AUDIT_images-models-dimensions-phase-one-2026-09-12.md
    CSVs     claude/AUDIT-2026-09-12-ship-inventory.csv        254 rows
             claude/AUDIT-2026-09-12-missing-pictures.csv        6
             claude/AUDIT-2026-09-12-missing-models.csv         36
             claude/AUDIT-2026-09-12-model-capabilities.csv    256  (all of them)
             claude/AUDIT-2026-09-12-dimension-coverage.csv    253

## THE FIVE THINGS WORTH YOUR TIME

**1. The front page has never carried width or height.** Its `d`, `w` and `h` fields are the outline silhouette drawing and that drawing's size, and the builder nulls them whenever a picture exists. They were never dimensions. The page's length is the game-data Length, copied through the ClassName join. **Width and height exist, for all 318 ClassNames. They were simply never carried across.**

**2. The two dimension sources disagree, and I have not picked either.** 191 cards carry both a game length and a Fleetyards length:

- 50 are identical.
- 91 differ by more than 1 m.
- 58 differ by more than 10%.

Every conflict sits in the CSV with both numbers.

**3. The game dimensions look coarser than they read. This is an inference, and it is labelled as one.** 277 of 318 ClassNames share an exact triple with another ClassName. The Cutlass Black and the Shiv are identical, and 13 ground vehicles are all 8.75 x 6 x 3.5.

- **Javelin and MOTH are 0 x 0 x 0 in the game data.** The builder passes that zero through as a size.
- I have reported this and not fixed it. The file is C1's.

**4. A model matching a dimension is not always evidence.** The 19 Fleetyards imports were scaled on purpose so that their largest side equals the published Fleetyards figure. For those 19, the agreement is by construction.

- **Model orientation is not uniform.** Across 217 comparable ships, the longest axis is Z on 175, X on 33 and Y on 9.
- **So no axis is labelled length, width or height anywhere in the CSVs.**

**5. No model can take a paint as a texture swap today.** The fleet has 0 textures across 256 files, and 239 files have a single material. Only 85X and Fury are split finely enough for per-part work. 14 files have no UVs.

## THE COUNTS, AND HOW THEY SQUARE WITH THE ADJUTANT'S INVENTORY

**Pictures: 6 missing, all with no image field.** The other 247 all exist and are all WebP.

**Models: 36 missing from the front page's view:**

- **28** have an unused file of exactly the same name on disk. These are proposed, not applied.
- **2**, Javelin and MOTH, have a model the card cannot reach.
- **4** have nothing anywhere.
- **2** have a ClassName that maps to no file.

**This agrees with the Adjutant desk's numbers, and refines their Javelin and MOTH line.**

**Dimensions: 6 cards have none from any source:** CSV-FM, Genesis Starliner, MOTH, Odin, RAPTOR and Starlancer BLD. **That is phase two's list.**

## NOT DONE, SO NOBODY READS IT AS DONE

- No image was decoded. I checked magic bytes and size only.
- No model was rendered. You excluded that.
- No Draco geometry was decoded. The model boxes are world-space accessor bounds.
- 85X's skinning is not applied to its box.

*Build (Code), 2026-09-12.*
