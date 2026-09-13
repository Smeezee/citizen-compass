# AUDIT - images, models and dimensions, phase one (local only)

**Build (Code), 2026-09-12, for Owner.** The order is
`correspondence/open/build/2026-09-12_memo_build_the-image-model-and-dimension-audit-is-yours.md`.

**This audit is read-only against the project.** It modified, moved, renamed, downloaded and deleted nothing. **It corrected no finding along the way.** Every "proposed match" below is a proposal only. None has been applied.

The only files it wrote are:

- this report
- the five CSVs beside it
- intermediates under `_needs_review/audit/`

**No browser render check was run, per your ruling.**

**The five CSVs, on disk only and not mirrored:**

    claude/AUDIT-2026-09-12-ship-inventory.csv       254 rows  every data row and what becomes of it
    claude/AUDIT-2026-09-12-missing-pictures.csv       6 rows
    claude/AUDIT-2026-09-12-missing-models.csv        36 rows
    claude/AUDIT-2026-09-12-model-capabilities.csv   256 rows  every model file, not a sample
    claude/AUDIT-2026-09-12-dimension-coverage.csv   253 rows  one per card, sources in separate columns

**To re-derive every figure:** run `_needs_review/audit/write_csvs.py` and `_needs_review/audit/world_bbox.py`. Both read only.

**Labels used throughout, as you asked:**

- **STATED IN FILE** means the model file says it.
- **PROJECT** means another file in this repository says it.
- **MEASURED** means computed off the file.
- **INFERRED** means my reading, marked as such every time it appears.

---

## 1. THE AUTHORITATIVE SHIP LIST

**The rebuilt front page gets its cards from one chain, and that chain is the list:**

    testing/index.html   SHIPS literal (the site's own ship rows)
      -> build_frontpage_data.py
         -> data-layer/derived/main-page-concepts/frontpage_data.json    254 rows
            -> tools/frontpage/build_next_frontpage.py  (+ price_corrections.json, editions.json)
               -> testing/_src/next.src.html   const DATA = {ships: [...]}   253 cards
                  -> served as next.html, proxied at /

### From 254 data rows to 253 cards

**254 data rows become 253 cards, and exactly one record causes the difference.** `Valkyrie Liberator` is folded onto the `Valkyrie` card as an edition by `editions.json`.

- **PROJECT:** the fold records it as "Sleven's call that the two are the same hull. Not yet checked against CIG spec data."
- Your later ruling on editions sends it to research first.

### Duplicates, merges and packages

- **Duplicate names in the 254 rows: none. Duplicate ids: none. No ClassName is shared by two cards.**
- No package record and no other merged record touches the total.
- **The only "duplication" is two images each shared across a family** (section 2). A shared image is not a merged record.

### Two identifiers, not one, and this matters

- **Pictures are matched by the card's NAME.** `build_next_frontpage.py:82` looks the name up in three name-keyed maps.
- **Models, the ship page, markers and game data are matched by the CIG ClassName** (the card's `hull`). `build_frontpage_data.py` gets it through the join `site name -> ship_resolution.matched -> case-folded hull key`, and its own record says that join has 0 collisions.

**219 cards carry a ClassName and 34 do not.** Counting rows instead of cards, it is 35, because Valkyrie Liberator is folded.

**The 34 hull-less cards are, set for set, the 34 careerless cards.** Q63.8A list 3 proved this last night in both directions. It is also the root of most of what follows.

### What I inspected matches what the test site serves

- The served card data was fetched and compared to the local build (`_needs_review/audit/served_next.html`). **All 253 cards are identical.**
- The local tree differs from the served payload only by the T-008 badge and the Q58 CSS, which are built but not deployed. Neither touches card data.

### Unresolved matches

**28 hull-less cards have a model file of the exact same name on disk that nothing references** (section 3).

- These are recorded as **PROPOSED** and are not applied.
- An exact filename is still a filename, not a ClassName join.
- Nothing here was matched loosely. There is no case-folding and no punctuation stripping (rule 17).

---

## 2. EVERY SHIP WITHOUT A PICTURE - 6

**All six fail the same way: NO IMAGE FIELD.** The card carries no image at all.

**The other 247 cards all have an image field, and I checked all 247 files:**

- **247 of 247 exist** in `testing/_deploy/images/`.
- **247 of 247 are WebP by magic bytes.**
- **None is under 1 KiB.**

So "field present but file absent" occurs 0 times. **"File present but unusable" is not proven either way.** I checked magic bytes and size and did not decode the images. That limit is stated here rather than rounded up to "usable".

    CSV-FM                             no sc-ships folder of that exact name
    F7C-M Hornet Heartseeker Mk II     no sc-ships folder of that exact name
    Genesis Starliner                  no sc-ships folder of that exact name
    MOTH                               sc-ships/MOTH exists - holds a model, NO image.webp
    RAPTOR                             no sc-ships folder of that exact name
    Starlancer BLD                     no sc-ships folder of that exact name

**Proposed local matches: none.** No local image is exactly named for any of the six.

**Shared images, recorded and not judged:**

- `images/6501781da9ffdd61.webp` is used by ATLS, ATLS GEO IKTI, ATLS IKTI and ATLS IKTI RAD.
- `images/85237ea19f64cf22.webp` is used by Ballista, Ballista Dunestalker and Ballista Snowblind.

**PROJECT, for RAPTOR only - CORRECTED 2026-09-12, about 01:23 CDT, same day.**

**What I wrote first was wrong:** "your 2026-09-07 ruling refuses it". **That ruling KEEPS the RAPTOR** as a deliberate joke card, labelled as the joke it is. See `correspondence/answered/2026-09-07_memo_the-raptor-stays-as-a-deliberate-joke-entry-slevens-call.md`, order 3.

- **How I went wrong:** I took the line from `CLAUDE.md` rule 26, which uses the RAPTOR as its worked example of a research failure, and from a different 2026-09-07 ruling about `family_id`. **I never opened the memo that actually rules on the card.**
- **The consequence:** Architecture repeated my line to Owner and ordered the card removed. That order has now been withdrawn. **Nothing was removed.**
- **Not missing a picture by accident:** the RAPTOR needs a picture, and under that ruling Owner saves it himself.

---

## 3. EVERY SHIP WITHOUT A 3D MODEL, FROM THE FRONT PAGE'S VIEW - 36

**A link to RSI is counted as no model, as you ordered.**

- **None of the 36 is "unreadable".** All 256 model files parse (section 4).
- **None of the 36 is "deliberately shared".** The deliberately shared files belong to ships that HAVE a model.

**The 36 split into four cases:**

    28   no ClassName on the card, and an UNUSED model file of exactly the card's
         name sits on disk (e.g. Arrastra.glb, Odin.glb, Kraken.glb). PROPOSED, not
         applied. These files are among the 42 that nothing references.

     2   no ClassName on the card, but a model IS mapped on the ship page:
         Javelin (AEGS_Javelin -> Javelin.glb), MOTH (ARGO_MOTH -> MOTH.glb).
         UNREACHABLE FROM THE CARD, NOT ABSENT. Architecture's 2026-09-11 letter
         says the same about both ship pages.

     4   no ClassName and no model anywhere by exact name:
         CSV-FM, Genesis Starliner, RAPTOR, Starlancer BLD.

     2   a ClassName that maps to no model: F7C-M Hornet Heartseeker Mk II
         (ANVL_Hornet_F7CM_Mk2_Heartseeker), Gladius Dunlevy (AEGS_Gladius_Dunlevy).

### Edition, package or true variant

- **Package: none of the 36 is one.**
- **Edition versus true variant is NOT established for these rows.** The CSV flags only a row whose name says "Edition". Your ruling says the edition rule is physical difference, researched first. **Applying that rule is the edition audit you ordered, and it is not this job.**

**Reconciliation with the Adjutant desk's inventory** (`claude/INVENTORY_what-every-ship-has-and-what-it-is-missing-2026-09-12.md`):

- **Its counts agree with this audit:** 36 without a model, 6 without a picture, 34 hull-less, 217 with a model.
- **This audit refines one case:** the Adjutant's "no model" for Javelin and MOTH is, more exactly, "a model is mapped and the card cannot reach it".
- Its width-and-height line was already corrected on its own page.

---

## 4. EVERY MODEL THAT EXISTS - ALL 256, STRUCTURAL

### What the files STATE

- **256 files in `testing/_deploy/models/`.**
  - **MEASURED:** they total 528,659,316 bytes, which is 504.2 MiB or 528.7 MB. That is your "529 MB".
- **All 256 are glTF 2.0 binary (GLB) with KHR_draco_mesh_compression.**
  - Every magic number is `glTF`.
  - Every declared length matches the file.
  - **None is unreadable.**
- **STATED IN FILE, tool:**
  - 255 say "glTF-Transform v4.4.2", which is this project's Draco compressor.
  - One, Asgard, says "Khronos glTF Blender I/O v4.5.49".
  - **No file carries a copyright field.**
- **Textures: 0 in all 256. Images: 0 in all 256, embedded or external.** There are no texture names to report because none exist.
- **Materials:**
  - 237 files have one material, named "Default".
  - 2 have one material, named "Material".
  - 15 have two. Thirteen of those are "Material" plus "Glass.001".
  - **85X has 113 materials, and Fury has 96.**
- **UV mapping is declared on 242 and absent on 14:** Crucible, Dragonfly_Black, Dragonfly_Yellowjacket, Herald, Hull_A to Hull_E, Mantis, Mule, Nox, Nox_Kue and PTV.
- **Animations 0. LOD-named nodes 0. Collision-named nodes 0.** One file is skinned: 85X.
- **Named hardpoint nodes are STATED IN FILE in only two: 85X (199) and Fury (182).**
- **31 files carry node transforms.** That fact changes the dimensions section, below.

### Could the material slots support paint - INFERRED from the counts above

**No file today can take a paint as a texture swap.** None has a texture, and 239 have exactly one material, so there is no slot to put a paint into.

- The 15 two-material files separate glass from everything else, at most.
- **Only 85X and Fury are split finely enough for per-part material work.**
- 14 files would need UVs before any texture could be applied at all.

### What the PROJECT states elsewhere

- **Hardpoint markers:**
  - `loadout_marker.gen.js` holds 6,252 markers on 267 ClassNames.
  - By type:

        from CIG data                 1,852
        inherited from a sibling hull 4,176
        estimated from part names       224

  - Per-file sums are in the model-capabilities CSV. **They are the project's placements, not the files' own.**
- **Sharing:**
  - `LOADOUT_MODEL` maps 295 ClassNames onto 214 distinct files.
  - **51 files serve more than one ClassName, 132 ClassNames in total.**
  - **42 files are referenced by no ClassName at all.** 28 of those are the proposed matches in section 3.
  - Every mapped file exists on disk.
- **Where each file came from:**
  - `sc-ships/index.json` (Fleetyards, dated 2026-07-26) reaches 242 files by the exact rule `folder.replace(' ', '_') + '.glb'`.
  - 23 folders carry a `MODEL_SOURCE.txt`:
    - **19 were fetched from the Fleetyards public API on 2026-08-27.** Each records its URL, sha256 and Fleetyards' own upload time. **Each also says `last_verified_patch: NOT VERIFIED`.**
    - **4 are chassis copies of another ship's model, made 2026-07-30:** Caterpillar Pirate Edition from Caterpillar, P-72 Archimedes Emerald from P-72 Archimedes, Pulse from Pulse LX, and Ursa Fortuna from Ursa.
  - **One file is reached by neither source: `San_tok.y_i.glb`.** The index has `San'tok.yāi`. The deployed filename has lost the apostrophe and the `ā`, so the exact rule cannot reach it. **I did not match it any other way (rule 17).**
    - **Update, 2026-09-12 about 02:25 CDT, on Architecture's instruction:** "the fix is the filename or an explicit mapping, not a looser rule."
    - `write_csvs.py` now carries one explicit, named pair: `San_tok.y_i.glb` to `San'tok.yāi`. It refuses if that name is not a real index record, or if the pair would shadow an exact match.
    - The model-capabilities CSV now records it as index id 174. **No file in the project has been renamed.**

### Units and axes - MEASURED, and the reason no axis is labelled

**What the format says:** the glTF format specifies metres and +Y up. That is the format's claim, not proof about any one file.

**The raw bounds are wrong for 31 files.** Raw accessor bounds ignore node transforms, and on those 31 files that is off by up to 100×. For example, the raw box for 600i Executive Edition is 5,202 × 9,027 × 1,751.

**I therefore recomputed every box in world space, with node transforms applied** (`world_bbox.py`, which reads the JSON chunk only).

**Measured against the game figures for the 217 cards that have both a model and a game dimension**, the ratio of each model's largest world extent to the largest game dimension came out:

- median 0.976
- **72 within 2%, 157 within 10%**

**Orientation is not uniform across the fleet.** The longest world axis is:

- Z on 175 of those 217
- X on 33
- Y on 9

**So no single axis can be called length across 256 files.** Per file, it could only be called length with evidence for that file. **The CSVs label boxes X × Y × Z and nothing else**, as you ordered.

### A size match is not always evidence - PROJECT, and it matters for section 5

Two different project scripts sized these files:

- **The 234 original models:** `rescale_all_ships.py` forced one constant scale (0.01) onto all of them. Its successor's header says it *"MEASURES NOTHING"*. So for these files, the size comes from how they were authored, which makes it roughly independent of the game figures.
- **The 19 Fleetyards imports:** `scripts/fix_model_scale.py` and `_blender_scale_to_spec.py` scaled each one so that its largest dimension equals the ship's largest published Fleetyards dimension. They apply it as a node transform.
  - **All 19 are among the 31 node-transform files.**
  - **For these 19, agreement with a published figure is by construction.**
  - **That agreement proves only that the scaler did its job. It is not evidence that the figure is right (rule 16).**
- **The other 12 node-transform files have a transform whose origin I have not established:** Avenger_Stalker, Crucible, Endeavor, Mule, Nautilus, Orion, Pioneer, Polaris, San_tok.y_i, Starlancer_MAX, Starlancer_TAC and Vulture. None is in the import set.

**Ten node-transform files land exactly on the game maximum (within 0.01 m):**

- **Seven are imports:** 600i Executive Edition 91.5, 85X, Fury, Mantis 30.0, Starlite, Tiburon 121.0 and UTV 4.0.
- **Three are not:** Avenger Stalker, Mule and San'tok.yāi. **I have not established why those three land on the game figure exactly.** The scripts I read do not account for them.

**Model-to-game disagreements beyond 25%, world space, recorded and not resolved:**

    over:   M80 2.78x, Clipper 1.87x, Defender 1.54x, Eclipse 1.51x,
            ROC 1.26x, Basher 1.22x
    under:  STV 0.48x, Cyclone family (6) 0.65x, CSV-SM 0.69x, Hull B 0.69x,
            Hull A 0.72x, Mercury Star Runner 0.74x

---

## 5. DIMENSIONS - WHICH SOURCE, WHETHER THEY AGREE, AND WHY THE FRONT PAGE HAS NONE

### Where each figure comes from - four sources, kept in separate CSV columns

    GAME DATA    LOADOUT_SHIPS.dim, 318 of 318 ClassNames. build_loadout_data.py:1299
                 reads Length, Width, Height from ships.json in the scunpacked snapshot
                 20260827T225641Z - a community extraction of the game files. The
                 axis NAMES are that source's, not proven against a model.
                 Reached by 219 cards.
    FLEETYARDS   sc-ships/index.json length / beam / height, dated 2026-07-26.
                 Reached by 219 cards by exact name.
    PAGE L       the card's length. It IS game-data Length - build_frontpage_data.py:88
                 copies it through the ClassName join. 219 of 219 equal. Same source,
                 not a second one.
    MODEL BOX    CALCULATED, world space, 217 cards. Not independent wherever the
                 project scaled the model to a published figure (section 4).

### Why the front page carries no width or height - and never has

**The card's `d`, `w` and `h` fields were never dimensions.**

- `d` is the SVG path of the ship's outline silhouette.
- `w` and `h` are that drawing's size, in drawing units (`build_next_frontpage.py:70`).
- **The builder nulls all three whenever a picture exists** (`:83`). That is why they are null on the 247 cards with a picture.
- **They are also null on the 6 without one.** None of the six has an outline either.

`build_frontpage_data.py:88` takes only `L` from the game record. **Width and height were simply never carried across.**

### Whether the sources agree - recorded, never resolved

**191 cards carry both a game Length and a Fleetyards length:**

- **50 are exactly equal.**
- 141 differ.
- **91 differ by more than 1 m, and 58 by more than 10%.**

Every one of the 141 is in the dimension CSV's `conflict` column with both numbers. **Not one has been picked.**

### Two findings about the game data itself

**Finding 1 - most dimension triples are shared.** 277 of 318 ClassNames share their exact triple with another ClassName, across 70 distinct triples. For example:

- Drake Cutlass Black and Grey's Shiv are both 37.5 × 26.5 × 11.5.
- 13 ground vehicles are all 8.75 × 6 × 3.5: the Cyclones, Mule, STV, the Ursas and CSV Cargo.
- Eclipse, Defender and the Sabres are all 24.5 × 24.5 × 5.

**INFERRED, not proven:** that looks like a size-class box rather than a measured hull. The model disagreements above fall on exactly these shared triples.

**Finding 2 - three records are zero, and zero is passed through as a size.** AEGS_Javelin, ARGO_MOTH and PowerSuit are 0 × 0 × 0 in the snapshot.

- The builder accepts any value that is not None, so a **zero is carried into `LOADOUT_SHIPS` as a dimension**.
- **Whether the ship page prints "0 m" for Javelin or MOTH was not checked.** That is a render check, which is excluded.
- **Reported, not fixed.** The file is C1's.

### Gaps - 6 cards with no dimension from any source

    CSV-FM, Genesis Starliner, MOTH, Odin, RAPTOR, Starlancer BLD

**These six are phase two's list.** MOTH's only game figure is the zero above.

- **Odin has a model**, a 2026-08-27 Fleetyards fetch that was scaled to a Fleetyards figure at import.
- **That figure is not in `index.json`.** So a published number existed once and is not held anywhere this audit can reach.
- Phase two should look for it first.

---

## WHAT THIS AUDIT DID NOT DO, SAID PLAINLY

- **Decode any image.** Magic bytes and size only.
- **Render any model.** Excluded by your ruling.
- **Decode any Draco geometry.** All boxes come from accessor bounds, which the format requires to be present and which were present on every primitive. A box built that way is exact for the bounds and is never smaller than the geometry.
- **Apply skinning to 85X's box.**
- **Change anything it found.**

**Phase two** (external dimension research: RSI first, wikis last, never picking between conflicting numbers) **does not start until you say phase one is received.**

*Build (Code), 2026-09-12.*
