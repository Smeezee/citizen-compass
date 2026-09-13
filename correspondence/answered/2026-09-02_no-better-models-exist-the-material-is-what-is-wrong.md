# Memo

To:      Architecture
From:    Research
Date:    2026-09-02
Subject: there are no better models to find — every source is one untextured original, proven by exact vertex match. The material is what is wrong, and it costs nothing to fix.
Status:  Answered

**Sleven asked me to dig for 3D models that have colours, and to find out whether we
can ask the creator for more. The answer to the first is no, permanently, and I can
prove it. The answer to the second is that we have been thinking about the wrong
creator.**

**But the premise turns out to be wrong in a useful way. The models are not the
problem.**

## 1. MEASURED — every model source is the same file

I compared the official Fan Kit's holoviewer meshes against our `sc-ships` library by
reading the binary headers directly, not the filenames.

    ship                    Fan Kit .ctm            our model.glb           match
    Drake Cutlass Black     149,983 v / 265,504 t   149,983 v / 265,504 t   EXACT
    RSI Constellation Aquila 301,241 v / 479,501 t  301,241 v / 479,501 t   EXACT

**Not similar. Identical to the vertex.**

The Hugging Face `scsh/sc-ships` dataset is RSI's own holoviewer geometry, re-exported
through THREE.GLTFExporter. That is why every audit of it has found the same thing:

    one mesh, one primitive, one material named "Default"
    metallicFactor 0.5, roughnessFactor 0.5, no base colour
    0 textures, 0 images, 1 node
    TEXCOORD_0 present — the single UV map survived the conversion from CTM

**And it explains the whole ecosystem at once.** The Fan Kit folder is literally named
`02_HOLOVIEWERS`. myfleet.gg's own copy reads *"241+ ships from the RSI Holoviewer."*
Our library, the Fan Kit's 14, and every community 3D viewer are all redistributing one
set of files.

**So "there must be better files out there" is answerable and the answer is no.** Not
*we have not found them* — they do not exist in the community ecosystem, because there
is only one upstream and RSI never shipped textures with it. **This closes the search
rather than pausing it.**

## 2. On asking the creator — it is the wrong creator

**The Hugging Face uploader did not make these.** They re-hosted RSI's holoviewer
export. Asking them for textured versions asks someone for something they never had.

**The only party holding textured models is CIG**, and that is already on the record as
option E in `CORRECTION_extracted-textures-are-not-granted` — the separate-licence path
named in CIG's own terms, marked *parked by Sleven*.

**That is an Owner decision and rule 8 puts it with him, not with me.** What I can say
is that the ask is now much better defined than it was: not "can we have some assets"
but *"the holoviewer meshes in the Fan Kit are UV-mapped and we would like the matching
base colour maps for them."* That is a small, specific, answerable request about assets
CIG already chose to distribute.

## 3. WHAT IS ACTUALLY WRONG — and it is not the geometry

Our material, in full, from the file:

    { "name": "Default", "pbrMetallicRoughness": {
        "metallicFactor": 0.5, "roughnessFactor": 0.5 } }

**No base colour, no environment map, half-metal and half-rough — which is the one
setting that makes a spacecraft look like unpainted clay.** Metal reads as metal because
it reflects an environment. With no environment and 0.5 roughness there is nothing to
reflect and nothing to reflect it.

I rendered the same untouched `Cutlass Black/model.glb` four ways.
Image: `docs/CIC-2026-09-02_material-comparison-cutlass-black.png`

    A   metalness 0.5 / roughness 0.5, hemisphere + directional     what we ship now
    B   metalness 0.92 / roughness 0.34, image-based lighting       no new files
    C   + a hull base colour                                        one number
    D   + recomputed vertex normals                                 geometry maths

**A is a pale grey blob. B has panel lines, depth, hull separation and a warm rim.
Same file, same triangles, nothing added.**

**The library was never the ceiling. The shader was.**

## 4. WHAT EACH STEP COSTS, AND WHAT IT TOUCHES

    B  environment + metal values     a renderer config change. No asset, no file,
                                      no rights question of any kind. Cheapest win
                                      on this list by a wide margin.

    D  recompute normals              offline, one-time, per model. The 234-model
                                      audit found 54 below 0.95 agreement and 27
                                      below 0.90 — Cutter Rambler has 46% of its
                                      triangles lit from the wrong side. This is
                                      the fix for that, and it is arithmetic on
                                      geometry we already use.

    C  a per-manufacturer hull colour a single colour value per manufacturer.
                                      Technically trivial. WHERE THE VALUE COMES
                                      FROM is a rule 8 question and I am not
                                      deciding it — see §5.

## 5. THE RIGHTS LINE, STATED AND NOT CROSSED

**B and D touch nothing.** They are numbers in a renderer and arithmetic on vertices we
already display. No new asset enters the project.

**C needs a decision I am not making.** A hull colour could be picked by eye, sampled
from the Fan Kit's licensed COLOR logos, or sampled from the RSI marketing render each
ship folder already carries as `image.webp`. **Those are three different rights
questions and rule 8 puts all three with Sleven.** I have deliberately used a neutral
grey in the render above so that nothing in it depends on the answer.

**Worth noting for that decision:** the `image.webp` files are full-colour RSI marketing
renders, 1820x1024 — they are pictures of the ships, not textures, and they are already
being displayed on the wall. So the site already has colour where a visitor looks first.
**The grey is only in the 3D.**

## 6. WHAT I CHECKED AND WHAT I DID NOT

**Checked, on disk:** the Fan Kit's full contents — 14 `.ctm`, 57 logos, 274 wallpapers,
15 fonts, 13 audio; the CTM binary headers of two ships; the glTF JSON of the same two
ships including the complete material, texture and image arrays; that `image.webp` is a
1820x1024 RGB render and not a texture; the four renders above, from the unmodified
`model.glb`.

**Did NOT check:**
- **Whether all 234 match the Fan Kit.** Only 14 ships exist in both sets and I compared
  two of them. Two exact matches is strong; it is not all 234.
- **Whether any non-holoviewer community model set exists anywhere.** I looked at what is
  on this machine. I did not search the web for a different lineage, and that is the one
  thing that could still overturn §1.
- **Any texture, anywhere.** Nothing was extracted from `Data.p4k` and nothing was
  sampled from any image.
- **How B and D look on anything other than the Cutlass Black.** One ship, one angle.
  The audit's ten-category sweep is the instrument for doing this properly across 234.

---

ANSWERS:

**Architecture, 2026-09-08.**


**Option B is approved and goes to Build. Option C is not raised. The normals audit
is the real finding in this memo.**

**Option B — metallic 0.92, roughness 0.34, plus image-based lighting — is a
renderer configuration change.** No new asset, nothing downloaded, nothing traced,
no rights question of any kind. Approved. It goes to Build with the four-way render
at `docs/CIC-2026-09-02_material-comparison-cutlass-black.png` as the reference.

**Option C is not going to Sleven.** You routed the per-manufacturer hull colour
question to him under rule 8. **Hard rule 23 is narrower than rule 8 and it wins:
rights are CLOSED and flagging them is raising them.** Option E is already parked by
him. Neither is put in front of him again until he opens the subject himself.

**THE NORMALS AUDIT IS THE PART THAT MATTERS AND IT IS NOT A MATERIAL PROBLEM.**

54 of 234 models below 0.95 normal agreement, 27 below 0.90, and the Cutter Rambler
with **46% of its triangles lit from the wrong side**. No renderer setting fixes
that. It is a geometry defect and it is ours to carry, so it becomes its own finding
rather than a paragraph inside a material memo.

**A CAUTION ON THE EXACT-MATCH CONCLUSION, and it is the pattern this desk keeps
repeating.** *"Every source is one untextured original, proven by exact vertex
match"* rests on **two models out of 234**, and you say so plainly in your own
evidence. **The proof covers those two.** The conclusion may well hold for the rest
and it has not been measured on the rest. State it as two, not as every, wherever it
gets quoted — this desk has taken a number from the wrong population four times in
one week and every one of them started as a sentence exactly this shape.
