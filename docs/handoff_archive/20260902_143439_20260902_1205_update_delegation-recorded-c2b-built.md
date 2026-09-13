# Update — delegation recorded per OWNERS.md, and C2b is built

**Code**

## Ruling received

Sleven ruled on the ownership question, and C1 has written it into `OWNERS.md`
as a **DELEGATION** section, 2026-09-02. Stopping to ask was correct; the answer
is that **an order naming the FILE and stating the CHANGE is the owner
delegating that write.** Code is the owner's hands, not a second writer, so rule
14's actual failure mode - two writers unaware of each other - does not arise.

The condition is narrow and I am holding to it: the order must name the path and
state the change. Not "fix the viewer", not a second file noticed on the way,
not a better fix I thought of. If a named change turns out to be wrong, stop and
say so rather than substituting my own.

**Nothing is being undone.** F1, F2, V1 and V3 are correct and deployed.

## The record, as required — which order, which owner, which file

    testing/_src/cc_viewer.js       owner C1
      F1, F2  ORDER_the-camera-never-looked-at-the-ship-2026-08-26
              names the path, gives both changes as paste-in blocks.   DELEGATED
      V1      ORDER_the-ship-faces-away-2026-08-26
              names the path, gives the exact line.                    DELEGATED

    build_loadout_data.py           owner C1
      C2b     ORDER_catching-up-to-4-10-2026-08-26
              names `build_loadout_data.py:136` and states the change. DELEGATED

    testing/_src/loadout.src.html   owner C1
      V3      ORDER_the-ship-faces-away-2026-08-26
              states the change precisely - "default it closed" - but
              NAMES NO PATH. It says "the settings panel", not a file.
              NOT delegation under the clause as written.
              Written on Sleven's direct instruction ("Do V1 and V3
              first and deploy"), and he has confirmed it stands.

Flagging that last row rather than rounding it up to delegation, because it is
exactly the edge the clause is drawn around: the change was unambiguous, the
file was not named, and the two are not the same test. If C1 wants prose-only
orders to count, that is a change to the clause and not a reading of it.

## C2b built into the payload

`loadout_data.gen.js` now carries `"game_build": "4.10.0-LIVE.12519617"` beside
`"last_verified_patch": "4.10"`, both derived from the snapshot manifest rather
than typed.

## Deploy refused, correctly

`deploy_testing.ps1` **aborted before uploading**: the control sweep does not
vouch for this payload. That gate did its job - it is the only thing standing
between a bad payload and the site for 94 of the 98 controls, and it declined
rather than shipping on my say-so.

`-IgnoreSweep` exists and I am not using it. Running
`checks/run_all_controls.py` against what is actually about to go out, and will
report what it finds before anything is deployed.
