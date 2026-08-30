# Update — pushed `b9de329`. And the live-site header now claims 4.10 while the data still says 4.9.

**2026-08-30 08:35 UTC / 2026-08-30 03:35 local · Code (background session)**

    b9de329   35 files changed, 3,075 insertions, 488 deletions
    6b1837f..b9de329      local == remote      tree clean
    no _to_delete, no node_modules, no .exe, no editability_patches

## THE ONE THING TO READ IF YOU READ NOTHING ELSE

    releases/latest.html   Live 4.10.0 "Siege of Orison"   <- C1, today
    static/preview.html    same
    loadout_data.gen.js    last_verified_patch "4.9"       <- unchanged

**The header claim is ahead of the numbers.** Q46's DONE-WHEN is
`build_loadout_data.py` pinned to `20260827T225641Z` / `last_verified_patch
4.10`, it is **BLOCKED-BY Sleven's go-ahead**, and C1 records that they have not
flipped it.

**Committing published nothing** - the live site goes out by manual Netlify
Drop from `releases/latest.html`, not from git. **But that file is the live
payload's source**, and if it were dropped as it stands the site would tell a
visitor its numbers are verified against 4.10 when every one of them was checked
against 4.9.

**I have not touched it.** It is C1's file, the version flip is Q46, and Q46 is
Sleven's call. Recording it here because a mismatch that lives quietly in a
tracked file is exactly the kind of thing that gets discovered after a drop
rather than before one.

## WHAT WENT IN

    Q45 first slice   pairstore.go + pairstore_selftest.go, //go:build master,
                      proven absent from the crew binary by symbol and string
    Q42               answered, nothing changed - 299 transactions found
    the checksum fix  the find page now publishes the hash of what it SERVES
    the sixth copy    _verify_picker_deployed.mjs, found after shipping

## STILL OPEN

**The website needs one clean sweep and a redeploy.** The last sweep measured a
moving tree - eight `_src` files changed under it - and C1 has since changed more
of them plus the two live-site files. **Nothing is wrong with the served site**;
it is the local payload that has moved ahead of the last clean measurement.

**Q45's next slice** needs a caller. Today the only thing that feeds `StorePair`
is the selftest, which is what the order asked for.
