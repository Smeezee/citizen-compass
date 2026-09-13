# Memo

To:      Build
From:    Owner
Subject: The images, models and dimensions audit is yours — you have the shell and the database, and nobody moves 529 MB to do it
Status:  Open

**Read-only. Nothing is modified, created, moved, renamed, downloaded or deleted. This is an
audit, not a fix, and no finding in it gets corrected as you go.**

## WHY YOU AND NOT THE ADJUTANT DESK

**My ruling: the complete local audit belongs to Code because Code has local shell and
database access.** The alternative was copying 256 model files, 529 MB, into a cloud
workspace one batch at a time. **That is not happening.** You read them where they sit.

## PHASE ONE — LOCAL ONLY

**1. The authoritative ship list.** Which data source actually generates the rebuilt front
page's cards. Total records, every duplicate, cosmetic edition, package or merged record
that affects the total, the stable identifier used to match a ship to its images and models,
and whether what you inspected matches what the test site serves. **Do not silently merge
two differently named records — record an uncertain match as unresolved.**

**2. Every ship without a picture.** Alphabetical. Name, manufacturer, identifier, expected
path, and WHICH failure it is: no image field, field present but file absent, or file
present but unusable. **Check the actual files.** Note where another local image looks like
it belongs to that ship, as a proposed match, never as a silent fix.

**3. Every ship without a 3D model.** Same shape, plus whether the model is missing,
unreadable, or deliberately shared with another ship, and whether the row is an edition, a
package or a true variant. **A link to RSI counts as no local model.**

**4. Every model that exists — structural validation on ALL 256, not a sample.** Filename
and project-relative path, format, size, whether other ships share the same file, recorded
source and extraction date if any, tool if recorded, units and coordinate system if
determinable, mesh count, material count, textures embedded or external and their names,
whether UV mapping exists, whether material slots could support paint, whether hardpoint
markers exist and how many of what type, and any animations, collision geometry, levels of
detail or named nodes. **Separate what the file states, what the project states elsewhere,
what you measured off the geometry, and what you inferred.**

**Skip browser render checks entirely.** My ruling: ten samples would not establish the
condition of 256 models, so visual verification is a separate job and not part of this one.

**5. Dimensions — and read this before you start, because it changes the job.**
`LOADOUT_SHIPS` in `loadout_data.gen.js` already carries `dim` as three numbers for **all
318 ships** (Cutlass Black 37.5 x 26.5 x 11.5), while the front page's own `d`, `w` and `h`
are null on all 253 rows. **So the question is not whether we have dimensions. It is which
source each figure came from, whether they agree, and why the front page does not carry
them.** Report sourced dimensions and calculated bounding boxes as separate things, and do
not label an axis length, width or height until the model's units and orientation are
proven.

## PHASE TWO — ONLY AFTER PHASE ONE

**External research for dimensions still missing once phase one is in.** Official RSI
sources first, then CIG publications, then current game-file data, then maintained community
datasets, and wikis last. Record source, URL, date, the name that source uses, the values,
the patch if stated, and any conflict. **Never resolve a conflict by picking the
better-looking number.**

## DELIVERABLES

One Markdown report and five CSVs: complete ship inventory, missing pictures, missing
models, model capabilities, dimension coverage. **Report goes in `claude/`; the CSVs beside
it, on disk only — they are not mirrored.**

**Report before you work if anything in this scope needs a tool or an access you do not
have. Otherwise start, and tell me when phase one is in.**
