# ORDER — The placer's input is built from its own output, and the ships we just added cannot be seen.

**C1, 2026-08-26.** Both items below were found by Code while executing the
walkthrough order. **Neither was ordered.** He reported them rather than
patching around them, and the second one explains a defect Sleven filed on
2026-08-23 without either of us understanding it.

---

## P1 — THE CLOSED LOOP. Every ship added from here on is locked out of hardpoints.

**`build_matched.py` reconstructs `matched.json` by joining `ship_mounts.json`
to `hardpoints_fleet.json` for the model filename.** `hardpoints_fleet.json` is
the placer's OUTPUT.

**So only a hull already in the output can enter the input.**

    hulls with decoded geometry            235
    hulls the placer ever considers        175   (169 placed + 6 skipped)
    provenance of all 175        the 2026-08-10 sandbox run

**Cutlass Black has 17 mounts in `ship_mounts.json` and cannot reach the
placer.** It was fetched on 2026-08-24. It will never gain a marker while this
join stands, and neither will any ship added after it.

**This is not a bug in a run. It is a data-flow defect that makes the pipeline
monotonically closed** — the set can only ever shrink or stay the same, and
nothing in the system reports that a candidate was silently excluded.

**Fix the direction of the join.** The placer's candidate set must be derived
from what has geometry and mounts — the model manifest and `ship_mounts.json` —
**never from a previous placement result.** A prior run is a cache, not a
source.

    CONTROL, load-bearing: after the change, report the candidate count. It must
    rise from 175 toward 235. If it stays at 175 the join was not inverted, it
    was re-dressed - say so and stop.
    CONTROL: Cutlass Black must appear in the candidate set with its 17 mounts.
    It is the specific ship that proved the defect and it is the specific ship
    that proves the fix.
    NEGATIVE CONTROL, load-bearing: the 169 hulls already placed must keep the
    markers they have, positioned as they are. Widening the input must not move
    a single existing marker. Report how many of the 169 changed; the answer
    must be zero.
    CONTROL: report every candidate the placer REJECTS and why. Silent exclusion
    is how this went unnoticed for sixteen days.

## P2 — Four ships are substituted by skins and variants that were stand-ins for their own absence

**Sleven's walkthrough asked why some ships link to RSI. This is the other half
of the answer and it is worse, because these ships look fine.**

    Arrow                 folder on disk, NO CC_MODELS entry at all
    Constellation Aquila  folder on disk, NO CC_MODELS entry at all
    Cutlass Black         the site row renders `Cutlass Black Best In Show
                          Edition 2949` - a SKIN, substituted while the base
                          hull was missing
    Gladius               the site row renders `Gladius Valiant` - a VARIANT,
                          same stale substitution

**Those substitutions were reasonable when the base hulls did not exist.** They
exist now, fetched 2026-08-24 and rescaled, and **nothing points at them.** A
visitor asking for a Cutlass Black is shown a limited-edition paint job of it
and told nothing.

**Also unreachable: `Valkyrie_Liberator_Edition.glb`** — item 19 on Sleven's
walkthrough, answered by E14's enumerator rather than by hand.

**Point the four site rows at their own hulls, and re-point the skins and
variants at theirs.**

    CONTROL: assert every one of the 14 built-but-unreachable .glb files is
    either reachable afterwards or NAMED with the reason it is not. "Built and
    orphaned" must not remain a silent state.
    CONTROL, load-bearing: assert no site row renders a model whose name differs
    from the row's own ship, unless a substitution is declared and visible to
    the reader. A silent substitution is a wrong answer delivered confidently,
    which is the thing this project exists not to do.
    NEGATIVE CONTROL: the Best In Show and Valiant rows must keep their own
    models. Fixing the base hull must not steal the variant's.

## Why these two are one order

**Both are the same failure shape: the system cannot see a ship that arrived
after it last looked.** P1 locks new hulls out of hardpoints; P2 leaves them
invisible to their own page while a stand-in wears their name.

**Adding a model is not currently sufficient to add a ship**, and nothing
reports the shortfall. E14's enumerator now does — `scripts/enumerate_ship_gaps.py`
found all of this on its first run, in both directions, which is precisely what
it was built for.
