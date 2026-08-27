# Update — W4's mechanism found, E14 enumerated both directions

**Not committed. Working tree only.**

## W4 — the mechanism, and it is one gate with three symptoms

A ship becomes real to the site by surviving four joins in a row:

    site record (releases/latest.html, by id)
      -> ship_resolution.json   matched[].site == display name  -> game file
      -> LOADOUT_SHIPS          file stem (lowercased) == ClassName
      -> CC_MODELS[id]          folder -> testing/_deploy/models/<folder>.glb
      -> hardpoints_fleet.json  model filename -> placed hardpoints

**Join 1 is the gate.** `build_deploy.py:818` — with no ClassName there is no
`loadout.html#Class` for the name cell, so it writes `pledge_url` instead and
the visitor goes to RSI. The same missing ClassName means no marker set is ever
emitted. **One cause, two symptoms, and it is why Sleven filed them as two
separate complaints.**

**Nautilus, Vulcan, Crucible, Legionnaire and Liberator all fail join 1 the
same way:** `ship_resolution.json` lists all five under `no_game_file`. The
single-cause hypothesis in the order is CONFIRMED for the five.

**Eclipse is a different cause and the order was right to hold it apart.** It
passes join 1 (`aegs_eclipse.json`), has a page, has `Eclipse.glb` shipped, and
does NOT go to RSI. It has no markers because `place_fleet.py` refused it:
published dims 24.5 x 24.5 x 5, model extents 36.92 x 3.97 x 20.5, proportion
error 0.54 against a 0.35 limit.

**And the published dims are wrong at source, not here.** scunpacked's
`ships.json` gives 24.5/24.5/5 to Aegis Eclipse, Aegis Sabre AND Banu Defender.
The Sabre's own model matches that triple (ratios 1.000/0.979/0.181 vs
1.000/1.000/0.204) — **the figures are the Sabre's and two other ships are
carrying them.** Same defect class as Asgard/Valkyrie both reading 48/38/12,
which CIC already found. The guard did its job; the spec sheet is wrong.

**Nothing was patched on any page.** Six pages were not touched.

## Second finding, not in the order: the placement input is derived from the placement output

`build_matched.py` reconstructs `matched.json` by joining `ship_mounts.json`
(278 ships) to `hardpoints_fleet.json` for the model filename. **So only hulls
already in the fleet output can enter the input.** matched.json holds 175 =
169 placed + 6 skipped, all from the 2026-08-10 sandbox run.

**235 hulls have decoded geometry. 175 are ever considered.** A ship that gains
a model can never gain markers. Cutlass Black, fetched on 2026-08-24, is in
`ship_mounts.json` with 17 mounts and cannot reach the placer.

## Third finding — W3's coverage root is the deferred B5 job, not a new one

Retaliator: 20 hardpoints placed, 4 markers survive. The four are its
countermeasure launchers. Its guns are named `hardpoint_class_2` x10,
`turret_left` x5, `turret_right` x5 — **child ports under a turret**. The
placement holds the parent turret mounts (`hardpoint_turret_fronttop` and so
on) and the ship page lists the children, so the names never meet.

**That is exactly the inherited-sibling fix Sleven deferred to after the
hologram work** — spread a sibling around ITS turret. Raising W3 coverage is
that job, not a separate one.

## E14 — the enumeration, both directions, shipped

`scripts/enumerate_ship_gaps.py`, artifact in
`data-layer/derived/ship-gaps/`. No fuzzy matching anywhere; an unresolved row
is reported unresolved.

    254 site rows.  221 have a page.  228 have a model.
     27 fall through to RSI.  6 render as a plain name.
     26 cannot show a model:  16 no CC_MODELS folder
                               6 no game file
                               4 folder mapped, no .glb built (85X, Fury,
                                 Mantis, PTV - the AMENDS' "no model upstream")
     27 have a model built AND shipped and STILL go to RSI
     42 of 201 page-and-model rows have no markers
     14 built .glb that no site row can reach
     18 sc-ships folders with a model that was never built

**Direction B earned its keep immediately.** Three of the four ships fetched on
2026-08-24 are still not reachable:

    Arrow, Constellation Aquila   folder on disk, NO CC_MODELS entry at all
    Cutlass Black                 site row renders `Cutlass Black Best In Show
                                  Edition 2949` - a skin, substituted while the
                                  base hull was missing. Base folder now exists
                                  and nothing points at it.
    Gladius                       site row renders `Gladius Valiant`, a variant.
                                  Same stale substitution.

Also unreachable: `Valkyrie_Liberator_Edition.glb` — item 19 on Sleven's list,
answered by the enumerator rather than by hand.

## Rule 12 control

`checks/_verify_ship_gaps.py` — 33 assertions. Drives `analyse()` on synthetic
input with one ship per branch, so a passing run proves the classifier rather
than proving today's data looks right. **Proven in both directions:**

    normal                exit 0, 33 assertions
    --self-test           exit 1
    --mutate-drop-match   exit 1 - Reclaimer removed from matched[]; the
                          UNCHANGED negative control goes red, page->RSI
    --mutate-no-pledge    exit 1 - Nautilus loses pledge_url; the RSI-bucket
                          assertion goes red

## Next

W3's page-side half: a hull showing 4 of 24 must say so. That changes what the
page looks like, so it deploys under the standing rule.
