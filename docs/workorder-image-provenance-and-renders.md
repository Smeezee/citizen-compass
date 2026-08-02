# WORK ORDER — image provenance record, own renders, then re-notify CIG

**Approved by Sleven 2026-08-02:** do steps 1 and 2, then submit under clause 2(k).

Hard rule 13 applies: file an `inbox/` update on intake, on completion, and on any stop.

---

## Background — the provenance is not missing, it was not looked for

A prior report concluded the 241 ship images have no record of origin. **That was wrong.** `sc-ships/README.md` is a Hugging Face dataset card and it states:

- Title: **"Star Citizen Fan Assets (Unofficial)"**, `license: other`
- The exact non-affiliation disclaimer RSI requires
- All IP attributed to Cloud Imperium Rights LLC and Cloud Imperium Rights Limited
- Governed by RSI's **Fandom FAQ**: non-commercial, attribution, "Made by the Community"
- A takedown policy offering immediate removal on request

`sc-ships/.gitattributes` is Hugging Face's standard LFS template, corroborating the source. `sc-ships/index.json` carries 245 entries with per-ship `id`, `name`, `slug`, dimensions and asset paths.

**What that establishes:** where the pack came from and what its author claims about it.

**What it does not establish:** whether that author had the right to redistribute, or how the images were produced — screenshots, extracted assets, or renders. **Do not overstate this in any record.** It is provenance for the pack, not for the pictures.

---

## PART 1 — write the provenance record

Create `docs/ASSET_PROVENANCE.md`. It is a factual record, not an argument that everything is fine.

Must contain, separated so a reader can tell them apart:

**Established.** Source repository and platform. The README's licence declaration, disclaimers and takedown policy, quoted rather than paraphrased. `.gitattributes` corroboration. Date acquired. File counts: 241 `image.webp` in `sc-ships/`, a second copy in `testing/_deploy/images/`. The four `MODEL_SOURCE.txt` notes recording shared-chassis model copies.

**Not established.** Whether the upstream author had redistribution rights. How the images were produced. Whether any individual image is an official CIG asset, a screenshot, or a render.

**What we do about it.** Non-commercial, no monetisation. Disclaimers carried on the site. Takedown honoured immediately on request from CIG or RSI. Own renders replacing third-party images (Part 2).

Also record the **7 open `fan_kit_compliance` WARNINGs** already sitting in `logs/pipeline_check_results_fallback.jsonl` from 2026-07-31. Read them first — they may name specific problems this document should answer.

Carry the same disclaimer text on the site itself if it is not already there. The upstream repo does it; a fan project claiming the same protections should not do less.

---

## PART 2 — render our own thumbnails

**This is the move that removes the biggest unknown.** 243 ship models are already on disk. Rendering our own images makes provenance complete and self-documented: rendered by this project, from model X, on date Y.

It also adds no new exposure — those same models are already displayed in the 3D viewer.

### Requirements

Write `render_ship_thumbnails.py`, headless Blender, following the pattern already established by `rescale_all_ships.py` and `mk_thumbs.py`:

- **Resumable. Takes a start index and a count.** 243 models at 12.8 MB median will not finish in one unattended pass, and the device bridge times out at 45 seconds. Every long job in this project is built in slices; this is no exception.
- Skip outputs newer than their source.
- **Identical camera, lighting and framing for every ship**, derived from the model's own bounding box — the same `frame()` logic the viewer already uses. Consistency is a visible quality win over the current mixed-source images.
- Transparent background. The page composites its own backdrop; a baked-in background forecloses the star-map idea.
- Output 560px wide WebP quality 78 to match the current pipeline — **118 MB → 4.5 MB was the measured result last time**, so expect the same order.
- Write a sidecar manifest: for each image, the source model path, its SHA-256, render settings, and timestamp. **That manifest is the provenance** — without it this part achieves nothing that matters.

### Do not modify the models

Render them as they are. No recoloring, no outlining, no stylising. The Fan Kit language about not distorting assets is the reason the blurred-backdrop idea is parked; do not reintroduce the same question through the render pass.

### Rule 12

Before trusting a full run: point it at a model that does not exist, at a corrupt GLB, and at a ship whose folder has no model at all. Each must fail cleanly and be recorded, not skipped silently. **11 ships already have no model** — 85X, Arrastra, Fury, Mantis, Merchantman, PTV, Pulse, Ursa Fortuna, P-72 Archimedes Emerald, Caterpillar Pirate Edition — so that path will execute on the first real run whether it was tested or not.

### Then

Compare a sample of own-renders against the third-party images side by side and show Sleven before swapping. If the renders are worse, that is worth knowing before 241 files are replaced.

**Keep the originals.** Do not delete the third-party images until the renders are accepted, and even then move rather than delete — the bridge cannot delete, and a decision this size should be reversible.

---

## PART 3 — re-notify CIG under clause 2(k)

**Do not send anything until Parts 1 and 2 are done and Sleven has approved the wording. Claude Code does not send this email.**

### Why it is due

On 2026-07-25 Sleven submitted the site under clause 2(k). On 2026-07-28 RSI legal replied confirming the site adheres to fan site and Fankit policies.

**That confirmation describes a ship price table as it existed on 2026-07-28.** It is not a licence and it does not extend to what was not there to review. Since then the project has added a 3D model viewer, ship detail pages, ship images and a preview build. **That is a material change**, and a fresh notification is due on a domain change anyway.

### Draft, for Sleven to review and send himself

Prepare a draft — do not send — covering: the URL, what the site is, what has been added since the July review, the non-commercial position, that ship images are now the project's own renders with a provenance record, that no CIG asset is modified, and that any takedown request will be honoured immediately.

Short and factual. This is a notification, not a pitch.

**Frame the submission honestly.** The strength of it is being able to say "these are our own renders from unmodified models, and here is our provenance record." That is why Parts 1 and 2 come first.

---

## Standing note

Nobody in this chain is a lawyer and none of this is legal advice. CIG legal is the only party who can actually answer the question. Parts 1 and 2 exist to make the thing being asked about clean and describable before the question is asked.

## Boundaries

- No image is deleted in this order. Replaced images are moved, not removed.
- Live site untouched. `sc-ships/` stays gitignored.
- `docs/ASSET_PROVENANCE.md`, the render script and its manifest get committed.
- No email is sent by Claude Code under any circumstances.
