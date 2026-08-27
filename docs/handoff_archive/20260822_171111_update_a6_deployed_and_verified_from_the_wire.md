# Update - A6 complete: deployed to testing, verified from the served bytes

Deployed on Sleven's go-ahead.

    scripts\deploy_testing.ps1
    Current Version ID: 31f43cef-e7d6-4173-ab96-4d5049fbb9a4
    8 new or modified assets uploaded, 492 already there

The 8 are exactly the seven pages plus `loadout_model.gen.js` - which is what
A1/A3 touching every page should look like, and a useful sanity check in
itself: had it been 500, something other than the attribution change had moved.

**Dry run first.** `-WhatIf` stopped at "Nothing was uploaded" and the deployed
index was unchanged after it (sha `242e7023...`, the pre-deploy bytes). The
flag was proven by behaviour, not by reading the code - rule 12.

## Verified from the wire, not from the build directory

Every published page fetched from the origin and hashed against the local
`_deploy` copy:

    index.html      MATCH   37df0395b516
    download.html   MATCH   ba16dddbe71f
    find.html       MATCH   517a4ce5d757
    holo.html       MATCH   63116d122962
    keybinds.html   MATCH   a8a18dbfb2e0
    loadout.html    MATCH   ef576ee0b9d8
    stick-test.html MATCH   5ffe0d842db9

Seven for seven, byte for byte. `/models/Hammerhead.glb` serves 200,
3,608,636 bytes, `model/gltf-binary` - the exact local size.

**Worth recording, because it nearly produced a false alarm:** the first
comparison reported all seven DIFFERING. `curl` without `-L` was hashing the
redirect body - `/index.html` 301s to `/`, and so do `/find.html` and
`/keybinds.html`. The tool was wrong, not the deploy.

A1/A3 confirmed on the served bytes: the trademark line is present on all seven
pages, fetched individually.

## The deployed-origin controls, both of them

These are the two the sweep always skips, and they are the reason the sweep's
"0 failed" was never a statement about the live site:

- `_verify_find_deployed.mjs` - **27 assertions, exit 0.** Includes downloading
  `find_data.gen.js` and hashing it against the sha256 the page publishes:
  993,157 bytes, `dce035da...`, matching. And a flipped byte breaks it, so the
  hash check can fail.
- `_verify_deployed_links.mjs` - **SWEEP CLEAN, exit 0**, canary 404s as
  required. 17 internal references across 10 pages, 11 external all 200.

## The link sweep failed first, and its diagnosis was wrong

Worth writing down properly. It reported:

> these files are loaded by `<script src>` and were NOT in the swept set:
> hardpoint_data.gen.js. The reference extractor has stopped seeing script
> tags.

The extractor is fine. **N3 unpublished `hardpoint_data.gen.js` earlier today**
- index.html stopped loading it, it is still generated and still checked by
`_verify_hardpoint_data.py`, it is simply no longer served. The control's floor
was a hand-typed list of filenames: a second writer for a fact that lives in
`deploy_pages.py` (rule 14), and the two drifted the same day.

A real failure pointing at working code is worse than a silent one, because
somebody acts on it.

Fixed so it cannot recur, and so the two faults are told apart by name:

    floor is STALE      it demands a file the build no longer publishes.
                        Fix the list.
    extractor is BLIND  it demands a published file the swept set lacks.
                        Fix the extractor.

The floor is validated against `deploy_pages.py`, parsed (commented-out entries
skipped - that is how a page is unpublished there). It is deliberately NOT
derived from the swept set: that is circular, and a blind extractor would empty
both sides and pass.

**And the branch is proven rather than assumed.** `floorProblems()` is a pure
function driven with known-bad input on every run - stale, blind, unreadable,
and healthy - printed as four assertions. Without that, the stale branch I just
added would be code that had never once executed, which is exactly how the
thing it replaced came to be wrong. `--self-test` still exits 1.

## Two stale lines in deploy_testing.ps1's own checklist - REPORTED, NOT FIXED

Its post-deploy instructions tell the operator to confirm:

1. *"the page contains `id="cc-kb"` and `cc-ship::after`"* - `id="cc-kb"` is
   there. **`cc-ship::after` is in neither the served page nor the local build
   nor `_src`** (`cc-ship` and `cc-ship-open` are). Following that instruction
   today makes a healthy deploy look broken. I have not touched it: I do not
   know when the selector changed or whether its absence is intended, and
   guessing at a verification step is how a real regression gets waved past.

2. *"the password gate blocks from a clean context"* - **it does not, and A5
   measured that this morning.** Re-measured on today's deployment: `GET /`
   with no cookies and no session returns 200 and 421,641 bytes carrying
   Avenger 20 times, Hammerhead 5, Polaris 5, alongside the word "Password".
   The gate is CSS plus a `localStorage` flag; content is delivered before
   anything is typed. Unchanged by this deploy - the same posture A5 reported,
   still awaiting Sleven's decision.

   The checklist line is the more urgent half: it instructs the operator to
   confirm a protection that is not there, and a person following it would tick
   it off having looked at a page that appears blocked.

## A6 status

Sweep DONE (46 ok, 0 failed). Deploy DONE. Verify-from-served-bytes DONE, and
the two skipped controls are now run and green.

Nothing staged, nothing committed.
