# Update: item 3 done - the loadout bench is reachable, verified off the live URL

## What was built

A **Loadout** panel on the ship page with "Open in the loadout bench", passing
the ship's own class id: `loadout.html#ORIG_100i`.

**The floating LOADOUT tab is still gone.** Sleven removed it twice and both
reasons stand; the comment now records that reason 2 - "a floating tab has no
idea which ship you are looking at" - has been *satisfied*, not overruled.

## The id join happens once, at build time

The site's ship records carry a record number and a display name. The bench is
keyed on the game's class id. **Joining those on the name at runtime is the exact
failure `ship_resolution.json` exists to have closed**, so the join is done once
in `build_deploy.py` against that artifact and what ships is an **id -> id
table**. Runtime does `LOADOUT_LINK[ship.id]` and nothing else.

Built from the page that was just assembled, so the record ids are the ones the
page actually holds rather than from a second source that could disagree.

The build **refuses** if the two counts do not sum to the ship total, or if no
ship resolves at all - a dead entry point would otherwise ship silently.

## Every ship accounted for, as the SERVER returns it

    ships in the ship view   : 254
    offer the bench          : 221
    correctly offer none     :  33
    sums to the total        : True

The 33 with no bench data, first few: **Arrastra, Crucible, CSV-FM, E1 Spirit,
Endeavor, Expanse, G12, G12a** - pledge-only and concept ships with no game
files. Real absences, not lookup failures. They show **no link** and say why;
they never open an empty bench.

## And the links actually resolve

Checked against the **deployed** `loadout_data.gen.js`, not the local copy -
which would only prove the build machine agrees with itself:

    deployed bench knows        : 316 ships
    links the bench cannot open : 0
    every one of the 221 links resolves to a ship the deployed bench holds

## The deploy is not the acceptance

Fetched `index.html` back over the network from
`citizencompasstesting.citizencompass-contact.workers.dev` - HTTP 200, 1.6 MB:

    cc-lolink element        : yes
    the label a person sees  : yes
    the absence message      : yes
    LOADOUT_LINK table       : 221 ships mapped
    stale 'knows one ship'   : gone
    tab-removal ruling kept  : yes

**The page a person opens now has a way in.** Before today it was deployed and
unreachable, which is not shipped.
