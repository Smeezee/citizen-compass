# Update — shop and price layer run started, A1 in progress

Received `docs/ORDER_shop-and-price-layer-RUN-CONTINUOUSLY-2026-08-19.md`: 25
items, build the shop/price layer from the UEX snapshots and make FIND real.
Running continuously per §1 — ledger appended and committed per item, no stops
between items.

## Before A1

**The backup failed the first time and I did not proceed on it.** Rule 4 says a
backup that ran is not a backup that worked. `Backup-CitizenCompass.ps1` reached
step 3, found `PGPASSWORD` unset, and blocked on an interactive password prompt
until it was torn down — exit 58, **no database dump taken**. The git bundle and
working-tree copy had succeeded; the part that matters for a migration had not.

Re-ran it with `PGPASSWORD` supplied from `.env` (never printed to the
transcript — the L1 credential leak already cost this project two token
rotations) and `-NonInteractive -SkipMirror`:

- git bundle verified OK, 42.4 MB, complete history
- working-tree copy, 10,337 files
- **Postgres dump written, 259.8 KB, and restore-tested into a throwaway DB**

## One finding from the backup, reported not fixed

The restore test printed:

    [WARN] Restore returned 232 ships, expected 254 - investigate before
           trusting this dump

I investigated rather than shrugging at it. **The live database holds 232 ships.
The restore returned 232. The dump is faithful** — `expected 254` is a stale
hardcoded constant in the backup script, dating from when the dataset was
believed to be ~254 ships.

That constant is worth someone's attention because it is a check crying wolf:
it will now warn on every single backup, and a warning that always fires is a
warning nobody reads. That is the same family of defect as rule 12, approached
from the other side. **I have not touched it** — it is not in this order's
scope and changing a backup script's success criteria mid-run is exactly the
kind of thing that should be a deliberate decision.

## A1 status

`app/models.py` gains `Location`; `app/locations.py` holds the resolver;
`checks/_verify_location_hierarchy.py` is the control. Control passes 31
assertions and has been **observed failing** under three deliberate mutations
(absent level rendering as `"None"`, whitespace names passing through, and a
resolver that returns nothing for everything — that last one is what catches a
vacuously-passing check). Migration next.
