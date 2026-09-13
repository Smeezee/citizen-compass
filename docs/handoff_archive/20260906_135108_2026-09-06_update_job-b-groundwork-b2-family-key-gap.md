# Update - JOB B groundwork, read-only. B2's family-key premise does not hold for the 22 ships that actually need adding. Nothing migrated.

Job A is deployed and closed. Started Job B in dependency order. **This is a
survey - no schema was changed, no row was written, no backup was needed because
nothing destructive was attempted.**

## What the database actually is today

    ships          232 rows, 18 columns
    NONE of ship_family / family_id / price_status / name_alias exists,
    as either a column or a table.

## The database is a STRICT SUBSET of the front page, and the join is perfect

    front page ships                 254
    database ships                   232
    EXACT name match                 232 of 232
    in the database, not on the page   0
    on the page, not in the database  22

**232 of 232 match on exact equality** - no folding, no substring, no closest
match (rule 17). The database contains nothing the page does not.

## THE FINDING, and it changes B2

B2 says:

> The family key is already exact and already collected. The store URL is
> `/pledge/ships/<family>/<ship>`... CIC recorded the URL for all 253. String
> split, no inference, no matching. The 80 singletons each get a family of one.

Measured against `frontpage_data.json`:

    two-segment pledge url, family by exact split   227 of 254
    a DIFFERENT url shape                             2   Hurricane, Intrepid
                                                          /pledge/Standalone-Ships/<name>
    NO url at all                                    25

    families found                                  133
    singleton families                               86   (the order says 80)

**And here is the part that matters:**

    ships missing from the database                  22
    ships with no store url                          25
    OVERLAP                                          22 of 22
    missing ships that DO have a family url           0

**Every single ship absent from the database is a ship with no store URL.** So
the family key - the thing B2 says is already exact and already collected - is
derivable for all 227 ships that are ALREADY in the database and for **none** of
the 22 that have to be added.

The 22: 600i Executive Edition, the three ATLS, both Ballistas, Carrack
Expedition, Constellation Phoenix Emerald, five F7A/F7C Hornet variants, F8C
Lightning Executive Edition, Gladius Dunlevy, Gladius Pirate, Mustang Alpha
Vindicator, Mustang Omega, P-72 Archimedes Emerald, Sabre Raven, Ursa Fortuna,
Valkyrie Liberator.

Most read as editions of hulls that ARE present - but **"reads as an edition of"
is inference, and rule 19 says ambiguity is refused rather than resolved by
picking.** I am not deriving `aegis-gladius` for "Gladius Pirate" because it
starts with the word Gladius. That is exactly the fuzzy matching rule 17 forbids,
and B2's own wording - "string split, no inference, no matching" - rules it out.

## So I have stopped before writing the migration

Writing `family_id` now would mean either leaving 22 ships without a family, or
inventing one for them. **The first makes the column nullable on exactly the rows
the front page needs; the second is inference wearing a schema.** Neither is mine
to choose - B2 is Architecture's design and this is a hole in its input data, not
in its shape.

**Two things are needed before B2 can be built:**

1. **Where does the family key for a ship with no store page come from?** If CIC's
   sweep has per-ship URLs that `frontpage_data.json` lacks, that source should be
   named. If no source exists, then `family_id` has to be nullable-with-a-reason
   and that is a design decision.
2. **Confirm the singleton count.** I measure 86, the order says 80. Small, but
   B2 sizes a schema on it.

## Not touched

- No migration written or run. No `alembic` command of any kind.
- No backup taken, because nothing destructive was attempted (rule 4 applies at
  the point of migrating, and I did not reach it).
- B1 (the three override files), B3, B4, B5 unstarted.
- `build_frontpage_data.py` still untracked - C1's, and committing needs Sleven.
