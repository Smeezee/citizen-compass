# Update — 4.10 is live on the testing site. 110 green, 0 NOT RUN, and every deployed-site control passes against the served origin.

**2026-08-30 12:15 UTC / 2026-08-30 07:15 local · Code (background session)**

    110 ok, 1 failed, 0 skipped, 0 NOT RUN, in 918s     GATE EXIT 0
    Version 85332626-5f57-4546-bd95-aa6c9c1e6d1f

The one failure was `_verify_picker_deployed.mjs`, deployed-only - the deploy is
its remedy, and it is green now.

## VERIFIED ON THE SERVED BYTES

    /                       HTTP 200    392,966
    /models/Hammerhead.glb  HTTP 200  3,608,636
    /loadout_data.gen.js    HTTP 200  3,925,424
    last_verified_patch     "4.10"
    Kruger S-65 Stingray    4 records served
    PLACEHOLDER             0
    header                  Ship data compiled: 2026-07-30
    find_deployed / deployed_links / picker_deployed   all GREEN

## SEVEN CONTROLS WENT RED ON THE PULL AND NONE WAS A DEFECT IN THE PAGE

    fitment          pinned "305 of 316"; 4.10 is 307 of 318
    ship_page        asserted the Stingray was NOT in the dataset; it shipped
    palette          needed a hull whose armour reduces AND increases damage
    label_threshold  needed a hull whose labels do not all fit
    child_markers    baseline predated the pull
    marker_census    C1 declared it
    picker_deployed  deployed-only

**Two of those are now permanent NOT PERFORMED lines rather than deletions.**
No armour record in 4.10 has a multiplier above 1.0 - 307 reduce, 0 increase -
so the increase cell has nothing to render on, and it says so every run instead
of quietly not being tested. Same for the labels case. Rule 11: a deleted
assertion is a coverage loss nobody can see.

## THE FIXTURE THAT KEPT BLOCKING DEPLOYS NOW LIVES WITH ITS CONTROL

`_verify_child_markers.py`'s baseline was in `data-layer/derived/holo-hardpoints/`,
C1's directory. **A control I own could only be un-blocked by somebody else's
edit**, so rule 14 and a green suite pulled against each other every time the
ship data moved. It is `checks/_fixtures_markers/` now. C1's file untouched.

**And my first re-take was wrong.** I copied the current payload, which made
before and after identical, and three assertions failed instantly - the
Retaliator gaining markers, coverage rising, the population being the fleet.
The baseline is a NO-INHERIT build: 1,994 markers on 257 hulls against 6,019 on
259 shipped. **The control refused in under a second and the error never reached
a commit.**

## FOR C1

**Polaris 22 -> 131 and the Corsair rack re-index are not in the documented
three.** Measured: the Corsair's five moved ports each take the PREVIOUS port's
old position - a rack sliding by one slot - and three more are a pure X mirror.
No two ports share a position afterwards. It reads as CIG restructuring, like
the Perseus, but it is undocumented.

**The page-slot contract is written**: `docs/CONTRACT_registering-a-new-page-2026-08-30.md`.
Short version - **the slot cannot come first.** The build refuses a registered
page whose source is missing, so an empty slot breaks every build until the
files land. Hand over `build_commodity_data.py`, `commodity_data.gen.js` and
`commodities.src.html` and it is one commit.

## STANDING

    site      closed out and deployed. 4.10 is live on testing.
    Q5b       with Sleven, running the elevated registration by hand
    next      the commodity page, on C1's three files
