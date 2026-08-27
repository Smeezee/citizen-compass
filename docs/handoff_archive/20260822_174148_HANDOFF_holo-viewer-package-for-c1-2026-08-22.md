# HANDOFF — the 3D viewer prototype and everything under it, packaged for C1. Plus what is still missing to reach every ship.

    from      C3 (Cowork), 2026-08-22
    for       C1
    why       Sleven asked for the viewer he was shown on 2026-08-09 so C1 can
              see it, and then asked what it would take to do the same for all
              of the ships.
    status    the prototype is HISTORY, not a proposal. The live ship page has
              long since passed it. Read section 4 for what is actually open.

---

## 1. What is in the package

    citizen-compass-holo-viewer.html   13.3 MB, opens offline, nothing to install
    hardpoints_fleet.json              167 ships, 1,798 hardpoints
    place_fleet.py                     the derivation, with its reasoning in comments
    placement_report.json              167 placed, 7 skipped with stated reasons,
                                       17 crowded
    MANIFEST.json                      what the dataset is and is NOT
    before.png / after.png             the two viewer defects, before and after
    full.js                            the runtime proof that measured them

**The HTML file is the thing to open.** Four ships — Cutlass Black, Constellation
Aquila, Sabre, Cyclone — with the models embedded inside the file itself. No
server, no internet, no build step. Double-click it.

## 2. What it proved, and why it mattered at the time

**Code had reported the viewer as not rendering.** It rendered. The failure was
that DRACO-compressed `.glb` needs a worker to decode, and a worker is blocked
over `file://`. Served over `http://` it worked immediately. **That was a
diagnosis, not a fix, and it saved rebuilding something that was not broken.**

**Two real defects were found and measured rather than described:**

    pure white pixels    63.7%  ->  0.0%
    markers on screen      0    ->  8
    lit pixels          48,581  ->  49,544   (ship unchanged in size)

The white-out was `DoubleSide` plus additive blending with no depth pre-pass on a
353,731-vertex mesh — every surface behind every other surface adding light until
the hull saturated. Fixed with a depth-only pre-pass and `FrontSide`.

**The before/after PNGs are in the package** so nobody has to take the numbers on
trust.

## 3. What the underlying dataset is, stated honestly

**These are NOT CIG's coordinates.** All 25,150 ports in `ship_specs.json` carry
`position: null` — re-verified on this dataset. **Nobody has the real numbers.**
The positions are derived from the mount NAME plus the hull's own geometry. They
are close, not exact, and any viewer showing them must say so.

**One naming decision worth carrying forward.** The field is `pos_model`, not
`pos_m`, because the model library uses three different scales — 158 ships in
metres, 8 normalised, 1 in centimetres. **An earlier four-ship file called the
field `pos`, the viewer read it as metres, it was centimetres, and every marker
landed fifty ship-lengths from the hull.** The unit belongs in the name.

## 4. WHAT IS STILL MISSING TO REACH EVERY SHIP — the part Sleven actually asked about

**Current coverage: 167 of 235 models placed.** The 68 without markers were sorted
one at a time on 2026-08-16 (`claude/FINDING_68-ships-without-hardpoints-2026-08-16.md`):

    29   NAME MISMATCH - the data exists on both sides and does not join
    27   no mount data anywhere - mostly concept ships that have never flown
     7   rejected by the placement step
     5   correctly zero - no conventional weapon mounts

**The 29 are the whole opportunity and they need no new data.**

Twelve are the same ship under CIG's longer name — `Aurora_CL` against
`Aurora Mk I CL`, `A2_Hercules` against `A2 Hercules Starlifter`. **That is 213
hardpoints already extracted and sitting on disk**, including every Aurora variant
and all three Hercules at 41 mounts each.

Sixteen are paint and edition variants whose mount data lives under the base ship,
and **Sleven's shared-hull ruling of 2026-08-14 already settles those** — same
hull means the same hardpoint positions.

One is `Khartu-Al.glb` against the key `Khartu-al`. **A capital letter.**

**The fix is a lookup table**, and this project has built one before —
`ship_resolution.json`, the last time four ships were found hiding behind a name.
This is the same job at seven times the scale.

**The 7 rejects are a source-data problem, not a code problem.** Six failed the
proportion guard. **The Defender and the Eclipse are both published at
24.5 x 24.5 x 5** — different ships, identical dimensions. At least one figure is
wrong and the guard is right to refuse. **Do not loosen the guard**; it exists
because it caught the run that mangled 50 ships.

## 5. What the RSI reconnaissance settled, and it matters here

`AMENDS_extracted-textures-scope-2026-08-22.md`, from CIC's holoviewer capture:

**RSI's own models cannot supply hardpoint positions.** They are OpenCTM, and
**OpenCTM cannot express a node hierarchy by format definition** — one mesh, no
named parts, exterior hull only.

**So the derived-marker approach is not a stopgap waiting for better data. It is
the only approach available**, and the community-practice ruling does not change
that. Worth stating plainly because "we will get real coordinates later" is the
assumption somebody will otherwise make.

## 6. What I checked and what I did not

**Checked:** every file in the package opens and carries what this document says;
the current on-disk dataset is unchanged since 2026-08-10; the 68-ship breakdown
against four data files, ship by ship.

**Did NOT check:**
- **What the LIVE ship page currently renders.** Recent orders reference 1,798
  hardpoints and 157 hulls; this package's dataset is 167 ships. **The two numbers
  are not the same and I have not established why.** Somebody should, before
  quoting either.
- **Whether the 29 name-matched ships would PLACE once joined.** Their hardpoints
  exist. That the placement step accepts them is a separate question and the
  proportion guard may still reject some. **Nobody should promise 29 until a run
  proves it.**
- Nothing was built, changed or deployed.
