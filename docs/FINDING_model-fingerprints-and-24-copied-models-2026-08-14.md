# FINDING — the rework tripwire is now real data: 235 models fingerprinted. It also caught something else: 235 files, 211 distinct hulls, and six of the copies are DIFFERENT SHIPS sharing one model.

    from      C3 (Cowork), 2026-08-14
    dataset   data-layer/derived/model-fingerprints/
    prompted  the claim-register work order, §3: "we hold the geometry. A rework
              changes the hull." That was a design. This is the data.
    status    baseline recorded. The comparison job is NOT written.

---

## 1. Why this exists, in one paragraph

CIC closed the Constellation question three independent ways today and the answer
is **CIG has said nothing**. That answer is correct and it has a hole in it: it
only ever watches CIG *talking*. **A rework changes the hull whether anyone
announces it or not**, and we hold 235 hulls. This is the one tripwire that fires
on the thing itself instead of on the announcement — and it is the only one of the
four in the work order that nobody outside this project can run.

So: every model now has a recorded fingerprint. If a Constellation `.glb` ever
stops matching it, that is evidence, and it does not depend on CIG saying a word.

**The Constellation baselines, for the record:**

    Constellation_Andromeda        551,174 verts   26.271 x 13.258 x 60.807
    Constellation_Phoenix          494,725 verts   26.626 x 13.258 x 60.756
    Constellation_Phoenix_Emerald  494,739 verts   26.626 x 13.258 x 60.756
    Constellation_Taurus           404,814 verts   26.273 x 13.255 x 58.913
    Constellation_Aquila           NO MODEL - still the known gap

## 2. What was measured, and the one honest weakness in it

Per model: **sha256, byte size, vertex count, bounding box**, plus the placement
frame and measured scale where the ship was placed.

Two methods, because one could not reach everything:

    renderer         174 models. Decoded in a real GL context, verts and bbox
                     read off the decoded mesh.
    gltf-accessor     61 models. Read from the glTF JSON chunk alone - the
                     POSITION accessor's count and min/max - with no DRACO
                     decode at all. 8 KB of JSON per model instead of 2 MB.

**Mixing two measurement methods in one table is a real risk and I only have one
calibration point.** The four Carrack files happen to split two-and-two across the
methods, and they agree to **0.002 units on a 125-unit hull**. That is the whole
basis for treating the two methods as comparable. It is one data point. The
geometry-match tolerance is set at 0.1% relative because of it, and that number
should be revisited if a second overlap ever appears.

**Not checked:** whether a DRACO re-compression at a different quality setting
would change the vertex count without changing the hull. If CIG's exporter changed
settings, that would read as a rework and it is not one. **The bounding box is the
defence against that** — a recompression should not move the extents. A change in
*both* verts and bbox is the signal; verts alone is a question, not an answer.

## 3. What it caught on the way past

    235 files
    213 distinct sha256
    211 distinct geometries

**24 of the 235 files are a copy of another ship's model.** The earlier pass found
four suspicious pairs by eye. Hashing found sixteen byte-identical groups, and
geometry matching found two more that hashing missed (`Reclaimer` /
`Reclaimer BIS` and `Valkyrie` / `Valkyrie Liberator Edition` differ in bytes but
are the same hull).

**Most of that is correct and expected.** A paint variant *should* share a hull.
Ballista Dunestalker and Snowblind, the Caterpillar BIS and Pirate editions, Mole
Carbon and Talus, Titan Renegade, F8C Executive, Alpha Vindicator, Nox Kue, Pulse
LX, Ursa Fortuna, Super Hornet Heartseeker — all liveries, all correctly sharing
one model. **Those are not defects and should not be "fixed".**

**Six are different ships wearing one model, and those are defects:**

    C8_Pisces  =  C8R_Pisces          byte identical. The C8R is the medical
                                      variant with a different interior bay.
    F7C_Hornet_Mk_I = F7A_Hornet_Mk_I byte identical. The F7A is the military
                                      airframe, not a paint on the civilian one.
    Cutlass_Black_BIS = Cutlass_Steel byte identical. The Steel is a troop
                                      transport - a visibly different ship.
    Mustang_Gamma = Mustang_Omega     byte identical. The Gamma is the racer.
    Carrack = Carrack_w_C8X           all four Carrack files are one model. The
            = Carrack_Expedition      "_w_C8X" files exist specifically to show
            = Carrack_Expedition_w_C8X the docked snub. They do not contain it.
    Kraken = Kraken_Privateer         2 vertices apart, bounding box identical
                                      to 3 decimal places.

**The Kraken pair is the one to care about**, because both are on the upcoming-ships
list Sleven is tracking. The Privateer is Drake's only announced-but-unreleased
ship and it is a *different* vessel — the trading variant with a market deck. Our
"Kraken Privateer" is the Kraken hull with a 2-vertex difference. It is a paint
file pretending to be a ship.

**And one that is not a duplicate but is worse in its own way:**

    Aurora_LX     28,153 verts     168 KB
    Aurora CL/ES/LN/MR (one shared model)  267,000 verts   1.18 MB

Same ship, and the LX is a **9.5x cruder model** than its own siblings. It is not
wrong, it is just far below the library's standard, and a viewer showing them
side by side would make that obvious.

**Also worth a look:** `Asgard`, at 57,684 verts across a 4,856-unit hull, is both
the only centimetre-scale model in the library and by a wide margin the least
detailed thing in it.

**None of this is fixed and none of it should be by me.** Which of these are worth
sourcing better models for is Sleven's call — they cost download budget and Fan Kit
scope, and four of them are cosmetic.

## 4. The legitimate paint variants, as a control

The six defects above sit alongside ten pairs that share a bounding box exactly and
differ by **1 to 14 vertices** — a decal mesh on an unchanged hull:

    Nautilus / Solstice        1     Sabre / Comet                12
    Kraken / Privateer         2     P-72 / Emerald               12
    X1 / X1 Force              2     Phoenix / Phoenix Emerald    14
    Scorpius / Antares         8     Ironclad / Ironclad Assault  11

**That is what a paint looks like in this data, and it is why the Kraken pair is
damning rather than ambiguous** — it sits in the middle of the paint distribution,
not the ship distribution. For contrast, two genuinely different variants:
`Talon` / `Talon_Shrike` differ by **12,734** vertices, `Freelancer_DUR` / `MIS` by
**3,847**.

**`Ironclad` / `Ironclad_Assault` at 11 vertices is flagged, not concluded.** CIC
reports both shipped as separate 2026 releases. Whether CIG built the Assault as a
livery-level change or our two files are a packaging error is a question for
someone who can look at both in game.

## 5. What I checked and what I did not

**Checked:** all 235 files, on Sleven's machine, hashed in place rather than copied
— the library is 243 MB and staging it once already timed out. The 61 JSON chunks
came back as 8 KB compressed. Both raw inputs are kept beside the dataset so the
numbers can be re-derived rather than trusted.

**Did NOT check:**
- **The comparison job does not exist.** This is a baseline and nothing reads it
  yet. Until an auditor re-fingerprints and diffs, this catches nothing.
- **Whether any of the six duplicates is upstream or ours.** The models came from
  a third-party library. If the C8R and C8 are the same file *there*, that is a
  different problem from our copy step losing one.
- **Whether the 0.1% tolerance is right.** One calibration point, stated above.
- Nothing was deleted, renamed or re-fetched. This is a report.
