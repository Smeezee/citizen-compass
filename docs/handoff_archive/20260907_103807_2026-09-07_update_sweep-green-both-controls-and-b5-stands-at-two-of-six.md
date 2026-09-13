# Update - sweep green with both new controls. 122 ok, 0 failed, 0 NOT RUN. Nothing to deploy: the payload already matches what is live.

    122 ok, 0 failed, 3 skipped, 0 NOT RUN, in 2871s
    receipt 2026-09-07T10:37:05   fingerprint 6bf4c967c267dc61   exit 0

    _verify_front_page_assets.py    exit 0   3.1s
    _verify_front_page_roster.py    exit 0   0.2s

Both new controls hold in sweep context, not just standalone.

## Nothing to deploy, and I checked rather than assuming

The sweep rebuilds the payload, so I compared it against the live site:

    next.html    served 02e4075a6f851b4e (138,637)  local identical
    index.html   served 2d4eaac0c99f5526 (396,153)  local identical
    fingerprint  6bf4c967c267dc61  =  the fingerprint that was deployed

**The site is current.** The rebuild is byte-identical, including the date stamp
- it was already 2026-09-07 when last night's deploy went out.

## Where B5 stands

    written and proven   2 of 6
        _verify_front_page_assets.py   pictures exist, hash to their names,
                                       and artwork pages carry the notice
        _verify_front_page_roster.py   no duplicates, nothing invented, no
                                       silent absence, folds visible on parent

    the remaining 4 all wait on B2
        every card carries a price_status, none null      needs price_status
        every name_alias row has source, date, approver   needs name_alias
        card count equals the DATABASE's ship count       needs the database to
                                                          drive the page
        every picture reference resolves                  DONE, inside assets

## So I am at a genuine stop, and it is not for want of work to do

Everything left in Job B runs through B2, and B2 needs **five hand-entered family
rows** - CSV-FM, RAPTOR, Starlancer BLD, Hurricane, Intrepid. Neither the store
URL nor CIG's ClassName reaches any of them, and inventing one is the exact
failure C1 hit with Ursa Fortuna yesterday.

**Waiting on, in the order that unblocks the most:**

1. **Five family rows** -> B2 migration, then B1, then the last four B5 checks.
   The path after that is clear: written, proven on a local throwaway, backup
   verified, applied.
2. **The ragged card height** - live now on Sleven's go-ahead, C1's to level.
3. **The fold should carry the folded ship's own name** so the roster control
   can verify it directly and delete its declaration. C1's generator.
4. **241 unreferenced images** - rule 5 list filed, nothing moved, Sleven's call.
5. **`build_frontpage_data.py`** - untracked, Sleven's go-ahead (rule 2).

Nothing committed, nothing pushed, no `git add -A`.
