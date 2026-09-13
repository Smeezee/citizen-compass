# Update - B2 CANNOT BE MIGRATED YET, and it is not the 22. FIVE ships ALREADY IN the database cannot get a `family_id`, and it is NOT NULL.

Checked before writing a migration, not after. **No schema was changed, no
backup was run, the production database was not written to.**

## Ground established first

    production database is LOCAL   localhost:5432, PostgreSQL 17.10
    alembic                        at head, 71d65b7b4026, 16 migrations

Local matters: the e2e harness's guard permits a throwaway here, so the migration
CAN be proven before it is applied - without `CC_E2E_ALLOW_REMOTE`, which rule 3
forbids. That route is open when the blocker below clears.

**And B2's price half is sound.** I checked whether the database actually holds
the prices the front page shows, because "price_status on every price field"
needs the fields to exist:

    ship_dealer_listings.in_game_price_auec   252 rows
    pledge_links.price_usd                    229 rows
    item_prices.price_buy / price_sell     26,657 rows

They exist. `price_status` has real columns to attach to. That premise holds.

## THE BLOCKER

`family_id` is to be **NOT NULL**. Of the **232 ships already in the database**:

    family from source 1 (store URL, exact split)   227
    CANNOT be filled from source 1                    5

        CSV-FM              no store url at all
        RAPTOR              no store url at all
        Starlancer BLD      no store url at all
        Hurricane           url is /pledge/Standalone-Ships/Hurricane
        Intrepid            url is /pledge/Standalone-Ships/Intrepid

**Source 2 does not reach them either.** Searched
`docs/FINDING_model-resolution-2026-08-23.json` - the `editions`/`resolved`/
`missing`/`orphans`/`unreleased` lists, 93 edition pairs among them - by exact
string equality:

    CSV-FM, Hurricane, Intrepid, RAPTOR, Starlancer BLD
        NOT PRESENT ANYWHERE in that file

So all five fall through to **source 3, the hand-entered mapping, which does not
exist yet.** A NOT NULL column cannot be added to a table where five rows have no
value and no source can supply one.

**This is a different gap from the one I filed at 14:0x.** That one was the 22
ships not yet in the database. This is five ships that are already there and
already shipping on the site.

## One design note, because Hurricane and Intrepid are not the same case as the other three

They **do** have store URLs. The URL simply carries no family:
`/pledge/Standalone-Ships/<name>` is a **store category, not a family.** Treating
that segment as one would put Hurricane and Intrepid - and anything else RSI
files there - into a single "family" of unrelated ships, which is worse than
having none.

So they need a hand-entered family with a reason recorded, exactly like the three
that have no URL, and **source 1 must be defined as "the family segment of a
`/pledge/ships/<family>/<ship>` URL" rather than "the store URL"** - otherwise the
precedence rule reads as though it covers them.

## What I did NOT do

- **No migration written or run.** No `alembic upgrade`, no DDL of any kind.
- **No backup run.** Rule 4 bites at the point of migrating and I did not reach
  it. Running a full mirror to D: and E: for a migration I then could not apply
  would have been noise.
- **No throwaway database created.** Nothing to test yet.
- I did not invent families for the five. `CSV-FM` is not `misc-starlancer`
  because it looks like one - that is rule 17 and it is how C1 got Ursa Fortuna
  wrong this afternoon.

## What unblocks it

**Five hand-entered family rows**, each with where the family came from, the date
and who approved it - the same shape C1 specified for the 22. Five is a small
list and it is a hand call, not a derivation.

Once they exist: migration written, proven on a local throwaway, backup verified,
then applied. That path is clear and nothing else in B2 is in doubt.
