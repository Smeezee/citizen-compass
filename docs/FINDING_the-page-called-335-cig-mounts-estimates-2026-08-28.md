# FINDING — the page called 335 CIG-published mounts "estimates", and the field that was added to stop it hedging is what got it wrong

    from      C1 (Cowork), 2026-08-28 04:48 UTC
    status    FIXED in `build_hardpoint_overlay.py`, rebuilt by Code, verified
              green by a new control
    control   `checks/_verify_marker_provenance.py` — INDEPENDENT, both
              directions, self-test decisive
    touches   `build_hardpoint_overlay.py` (C1's). **No change to
              `build_deploy.py`** — the field it already reads is the field this
              now writes.

---

## 1. WHAT WAS WRONG

`build_deploy.py` decides a marker's provenance with one expression:

    'cig' if _hp.get('placed_from') == 'client' else 'est'

and `placed_from` was stamped in exactly one place — the loop that walks
`alignment_overlay_client.json` and **moves an existing marker** onto a CIG
position.

**41 hulls never enter that loop.** They have no marker record at all, so there
is no marker to move; they arrive as whole records through
`fleet_records_client.json`, already on CIG's decoded coordinates, and the stamp
never touches them. Every top-level dot on those 41 hulls — and on the variants
sharing their models, 57 page classes in all — was labelled `est`.

**The positions were never wrong. The page was wrong about them**, in the one
field that exists to tell a decoded mount from a guess. That is worse than
saying nothing, because `placed_from` was added on 2026-08-27 (Q9) specifically
so the page could stop hedging about all 1,693 mounts at once. It stopped
hedging and started mislabelling.

---

## 2. HOW IT WAS CAUGHT, AND WHY NOT SOONER

Not by a check. By re-measuring a number in `CURRENT-STATE.md` instead of
quoting it. The document said **"245 classes with every marker on CIG
coordinates, 20 with none."** Counting the deployed marker file gave **205 and
45**. The gap was the whole of this defect.

**The lesson is the cheap one and it keeps being cheap:** the headline number in
the authoritative document had never been recomputed from the artifact a visitor
actually loads. It was carried forward from the pipeline's own manifests, which
were right — the ports were placed, the acceptance passed, the records were
written — about every step except the last one.

---

## 3. THE FIX, AND WHY IT IS IN THIS FILE AND NOT IN CODE'S

`build_hardpoint_overlay.py` now stamps `"placed_from": "client"` on every
hardpoint in the records it emits. That is the field `build_deploy.py` already
reads, so:

- the fix lands entirely inside a file C1 owns;
- **Code's file is untouched**, and rule 14 stays intact;
- the provenance is written by the program that actually knows it, rather than
  inferred a thousand lines away by a program that cannot.

---

## 4. THE MEASUREMENT, BEFORE AND AFTER

Counted from `testing/_deploy/loadout_marker.gen.js` — the file the browser
loads — not from a manifest.

    mounts                       before        after
      cig                         1,691        2,026     +335
      est                           448          113     -335
      anc  (child ports)          4,261        4,261     unchanged

    page classes                 before        after
      every top-level mount from CIG   205        244
      mixed cig + est                   21         21   (88 est mounts)
      no CIG mount at all               45          6

**The six with none are the six that should have none:** `VNCL_Glaive` and
`VNCL_Scythe` (asymmetric hulls, placement correctly refuses them), `GRIN_MTC`,
`MISC_Starfarer_Gemini`, `TMBL_Cyclone_MT`, `TMBL_Cyclone_TR`.

**`CURRENT-STATE.md`'s "20 with none" was wrong in a third way**: it counted
*hulls* the hardpoint rule could not reach, several of which — the ARGO ATLS
family, the MOTH — have no model on the ship page at all and therefore no
markers to be missing. Corrected there in place.

---

## 5. THE CONTROL, AND THE FALSE POSITIVES IT PRODUCED FIRST

`checks/_verify_marker_provenance.py` compares two files written by two
different programs and asserts, both ways:

    A. NO UNDER-CLAIM   a dot on its own hull's CIG coordinate must say `cig`
    B. NO OVER-CLAIM    a dot labelled `cig` must be on one

**The first draft used one fleet-wide set of coordinates and was wrong.** It
reported 38 markers across 19 hulls — Prowler, Starlancer TAC, every Apollo and
Zeus variant — as mislabelled. Every one was an `anc` child port whose ring
offset happened to land on a number that is a CIG coordinate **on a different
ship**. Normalised coordinates are small and mirrored pairs are symmetric;
collisions across 271 hulls are expected.

Two corrections, both stated in the source:

- **A coordinate is only evidence inside the hull it belongs to.** The set is
  keyed by model file — the same join `build_deploy.py` uses — so the check and
  the emitter agree on "the same hull" without either importing from the other.
- **`anc` is excluded from A by definition**, not for convenience. A child port
  is its ancestor's mount plus an offset and is not CIG's coordinate for that
  port even when the ancestor's was.

### Rule 12, and the mutator that would have been worthless

The obvious control — mutate a label, require the check to go red — **proves
nothing here**, because when this check was written it was already red. It would
have reported a decisive control while doing nothing. That is the same inert
mutator that nearly shipped in `_verify_stage_still.mjs` the day before.

So `--self-test` asserts a **delta**, not a verdict, and is decisive either way:

    clean      under-claims     0   over-claims     0   labelled cig  2026
    relabel    under-claims  2026   (must be EXACTLY 0 + 2026)
    forge      over-claims     20   (must be EXACTLY 0 + 20)

Not "more" — exactly. **The relabel control is the strong result in this
document:** rewriting every `cig` label to `est` produces exactly 2,026
under-claims, which means every one of the 2,026 mounts the page calls CIG's is
on its own hull's CIG coordinate. Nothing is over-claimed.

Its exit code is inverted per the suite's convention (`run_all_controls.py
--self-test` requires a non-zero exit from every control), and the banner says so
in words, because an inverted exit code read at a glance is a defect waiting to
be filed.

---

## 6. WHAT THIS DOES NOT PROVE

**That the dots are in the right place on screen.** This check proves a label
matches its coordinate's provenance. It says nothing about whether the
coordinate renders where the mount is, and it cannot — there is no browser in the
Cowork VM. `_verify_marker_positions.mjs` covers that for the overlay hulls; the
41 client-record hulls have never been through it.

**That is the next control, not a caveat to be filed and forgotten.** It is on
the queue as Q12.

— C1
