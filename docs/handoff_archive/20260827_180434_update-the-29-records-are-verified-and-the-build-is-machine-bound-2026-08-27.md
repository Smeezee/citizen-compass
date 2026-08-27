# Update — the 29 marker records are verified. The build is the only thing left, and it cannot run anywhere but your machine.

**2026-08-27 18:05 local · C1**

## Two things you need from me before you next build

### 1. I left a FAILED build receipt and it is mine, not yours

`testing/_src/.last_build.json` currently reads:

    "status": "failed", "detail": "FIND DATA GENERATION FAILED", "at": "2026-08-27T23:01:07"

**That was me, from the cloud bridge, and it is not a defect on your machine.**
I tried to run `build_deploy.py` myself so Sleven would not be waiting on a
session that is mid-clone. It died where it should have:

    build_find_data.py -> app/database.py -> ModuleNotFoundError: No module named 'sqlalchemy'

The build reads PostgreSQL. **PostgreSQL is on your machine and nowhere else.**
So the build is machine-bound by design, and I cannot route around you on it —
worth writing down, because I have now proven it rather than assumed it.

Nothing was written. Every `.gen.js` still carries its 22:25 timestamp; the
build refused before the first output. Rebuild normally and the receipt is
replaced.

### 2. I verified the merge WITHOUT a build, against the page's own data

I could not run the build, so I checked the thing the build would have told us,
from a source I do not write: `loadout_data.gen.js` and `loadout_model.gen.js`,
which YOUR build emitted at 22:25. Rule 16 — the truth came from somewhere
other than the thing under test.

    hulls in hardpoints_fleet.json                              178
    hulls in fleet_records_client.json                           29
    collisions between them                                       0   <- the merge cannot overwrite
    client model files the ship page actually references      29/29
    client model files already claimed by an existing record      0   <- nothing silently shadowed
    alignment-overlay entries matching nothing                    0   <- the build's match-or-die passes
    ports the overlay moves onto CIG positions                  952

And the decisive one — **simulating the marker emitter's own join**, port name
by port name, against the page's `LOADOUT_HP`:

    classes fed by the 29 records          32
    classes that would emit ZERO markers    0
    ambiguous ports                         0
    direct markers emitted                294

Per hull, top and bottom:

    CRUS_Starlifter_A2   18      RSI_Mantis        6
    AEGS_Tiburon         17      AEGS_Eclipse      5
    GAMA_Tyilui          15      ORIG_85X          5
    DRAK_Clipper         14      DRAK_Dragonfly    4
    DRAK_Pitbull         14      MRAI_Pulse        3

**The Mantis gets 6.** That is the ship Sleven opened at random this morning and
found completely empty.

## So the only remaining step is yours

Build and deploy testing. Everything below is written, verified and sitting
unbuilt:

- 29 marker records for hulls the dataset had none for (2,486 ports)
- 93 hulls / 952 ports moved onto CIG's own decoded hardpoint transforms
- the Undo button and the swap ledger on the loadout page
- compare-on-what-the-part-is-for (the lead stat is now the port's own)
- the camera no longer zooms out — and no longer discards Sleven's zoom
- the see-through panel, with an opaque fallback where blur is unsupported
- the picker dismiss fix, both states

**Check the build's own line first:** `client marker records added for 29
hull(s) the dataset had none for`. If it prints 0 the file is not being read,
and that is worth catching before the upload rather than after.

The 4.10 clone does not block this and this does not block the clone. Sleven's
standing instruction is that everything from today reaches the test page now.

— C1
