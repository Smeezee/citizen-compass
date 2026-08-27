# FINDING — 42 of the 68 unmarkered ships can be reached with data already on this machine. Not 29. The extra 13 came from a dataset nobody had checked against them.

    from      C3 (Cowork), 2026-08-22
    for       C1 + Sleven
    ask       Sleven: "see if you can find any more information to do this type
              of thing on all of the ships that we have"
    method    re-ran all 68 against the star-citizen.wiki vehicles snapshot
              (20260801T021731Z, 278 named vehicles with a `ports` array) rather
              than against ship_specs.json alone, which is what the 2026-08-16
              pass used.
    scope     research only. Nothing built, nothing changed, nothing deployed.

---

## 1. The headline, and it moved

    2026-08-16 pass    29 of 68 recoverable
    today              42 of 68 recoverable

**Thirteen more ships are reachable, and no new data had to be acquired.** The
wiki vehicles snapshot has been on disk since 1 August with a `ports` array on
every record. **The August pass never joined against it.** That is the finding.

    NOW RECOVERABLE      42
    genuinely absent     26

## 2. The thirteen that moved, and why they were missed

**Two matching failures, both mine.**

**Ares Inferno and Ares Ion.** CIG's full name is `Ares Star Fighter Inferno`. The
August pass used substring containment — `aresinferno` is not a substring of
`aresstarfighterinferno` and vice versa, so it found nothing. **Token containment
finds it immediately.** Both are flyable, both are heavily armed, and both were
filed as "real gap, no data exists." **They had 19 ports and 4 weapon mounts each,
sitting on disk.**

**The Auroras were missed the same way** in this dataset — `Aurora Mk I CL`
against `Aurora_CL`. They were caught in August against `ship_specs.json`, so the
conclusion held; the method was still wrong and would have missed them if that
file had been the only source.

**The rest came from the wiki snapshot simply carrying ships `ship_specs.json`
does not**, or carrying ports where the other file had none:

    Clipper       25 ports, 12 weapon        Javelin    59 ports, 21 weapon
    Defender      20 ports,  7 weapon        Nova       14 ports,  2 weapon
    Eclipse       16 ports,  2 weapon        Pulse       9 ports,  1 weapon
    Pulse LX       8 ports,  0 weapon        Khartu-al  15 ports,  2 weapon
    ATLS / GEO   2-3 ports,  1 weapon each   MDC         7 ports,  0 weapon
    ROC / ROC-DS 7-8 ports, 0-1 weapon

**CORRECTION, same day.** An earlier version of this table omitted **Pulse LX**
while claiming all seven rejects were listed. Six were. Sleven caught it.
The full reject list is: **Clipper, Defender, Eclipse, Javelin, Nova, Pulse,
Pulse LX.**

**And Pulse LX is a different case from the other six.** It resolves, but it has
**8 ports and ZERO weapon mounts.** Correcting its dimensions would let it through
the guard and still produce no markers, because there are none to place. **It
belongs with the correctly-empty group, not with the fixable six** — and the
viewer already handles a zero-mount ship. Counting it as recoverable would be
counting a ship that will look identical afterwards.

    fixable by a dimension fix    6   Clipper, Defender, Eclipse, Javelin, Nova, Pulse
    correctly empty               1   Pulse LX

**The other six were never a data problem at all.** They were — they were rejected on PROPORTIONS, and their mount
data was available the whole time. Fixing the dimensions unblocks them; the ports
are ready.

## 3. What this changes about the seven rejects

**The Defender and the Eclipse are still both published at 24.5 x 24.5 x 5** — and
now that is confirmed from a **second independent source**, not one. Different
ships, identical published dimensions, in two datasets.

**So it is an upstream error, not a copy mistake in this project.** The guard is
right to refuse and must not be loosened.

**And the Javelin's dimensions are not missing — they are ZERO.** `L=0 W=0 H=0`
against a mass of 111,080,494. A 345-metre capital ship published as a point.
"No published dimensions" in the August report was the guard reporting a zero
correctly.

**Fixing these needs a real length, width and height per ship**, from CIG's own
ship pages. CIC's 2026-08-22 recon established that **the full spec text is on
those pages and is on a permitted path** — that is where these six numbers come
from, and it is a small, bounded job.

## 4. The 26 that are genuinely absent, and they sort cleanly

**Nineteen are concept ships that have never flown:** Crucible, Endeavor, Expanse,
G12 / G12a / G12r, Galaxy, Genesis, Hull D, Hull E, Legionnaire, Nautilus and its
Solstice edition, Odyssey, Orion, Pioneer, Ranger CV / RC / TR, Vulcan.

**Nobody can fit a weapon to a ship that does not exist in game.** The absence is
correct and no source will fix it. **These will resolve when CIG builds them, and
not before.**

**Four are flyable and are real gaps:**

    E1 Spirit                  absent from both datasets
    Zeus Mk II MR              CL and ES are present, MR is not
    Kraken                     absent from both, no dimensions either
    Kraken Privateer           same

**The Zeus is the clean diagnostic.** Its sibling variants are present with full
port arrays, so the pipeline works for that hull — the MR row is simply missing
upstream. That is a source gap of exactly one record.

**Three are edition variants** whose base ship IS present and which
`DECISION_shared-hulls-are-fine-unless-the-shape-differs-2026-08-14.md` already
covers: the Super Hornet Heartseeker, and the two Nautilus entries.

## 5. What it would actually take to reach every ship

    42  a name-mapping table               no new data, largest single win
     6  correct dimensions from CIG pages   small bounded job, permitted path
     1  one missing Zeus Mk II MR record    source gap
     3  apply the shared-hull ruling        already decided
    19  wait for CIG to build the ship      not actionable

**The mapping table is the whole job.** This project has built one before —
`ship_resolution.json`, when four ships were found hiding behind a name. **This is
the same thing at ten times the scale, and today's pass says the scale was
understated by thirteen.**

**One rule for whoever builds it: do not use fuzzy matching.** The August pass
tried it and produced four confident, wrong pairs — Dragonfly Black to
Yellowjacket, E1 Spirit to C1 Spirit, G12a to 125a, Zeus MR to Zeus ES. **A fuzzy
matcher in the real pipeline would bolt the wrong hardpoints onto four ships and
nothing would catch it.** Exact and token-containment matching only, with every
pair reviewed once by a person.

## 6. And the reason none of this is waiting on better data

`AMENDS_extracted-textures-scope-2026-08-22.md`, from CIC's live capture of RSI's
own holoviewer: the models are **OpenCTM, one mesh, exterior hull only, and
OpenCTM cannot express a node hierarchy by format definition.**

**So RSI's own files cannot supply hardpoint positions.** Derived markers are not
a stopgap waiting for something better — **they are the only approach available**,
and the community-practice ruling does not change that. Worth stating because
"real coordinates will turn up eventually" is the assumption that would otherwise
sit under this work.

## 7. What I checked and what I did not

**Checked:** all 68 models against 278 named wiki vehicles, by exact match, then
substring, then token containment; the port and weapon-mount counts quoted are
read from the records, not estimated; the Defender/Eclipse collision and the
Javelin zero confirmed in a second dataset.

**Did NOT check:**
- **Whether any of the 42 would PLACE once joined.** Their ports exist. The
  placement step must still accept the geometry, and the proportion guard may
  reject some. **Nobody should promise 42 until a run proves it** — the same
  caution given on 2026-08-16, and it still stands.
- **Whether the wiki snapshot's port names match the vocabulary `place_fleet.py`
  reads.** It derives position from the mount NAME. If this source names ports
  differently from `ship_mounts.json`, the mapping is a second job, not a free
  one. **This is the single biggest unknown in the plan above and it is checkable
  in an hour.**
- **The live site's current coverage.** Recent orders cite 157 hulls; this dataset
  is 167. Not reconciled.
- Nothing was built, changed or deployed.
