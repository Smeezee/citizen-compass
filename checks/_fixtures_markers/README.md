# checks/_fixtures_markers

`loadout_marker.baseline.js` is `_verify_child_markers.py`'s BEFORE state.

## Why it lives here now

It used to live in `data-layer/derived/holo-hardpoints/`, which C1 claimed on
2026-08-29. That put a control I own behind an edit somebody else had to make:
every time the ship data moved, keeping the suite green and rule 14 pulled in
opposite directions. **A control's fixture belongs with the control.**

The old file is still in C1's directory, untouched. Rule 1: nothing here deletes.

## What this file IS, and the mistake worth not repeating

It is the output of a **NO-INHERIT build** - `CC_NO_INHERIT=1 build_deploy.py` -
which is the state *before* C1's inheritance pass runs. 1,994 markers on 257
hulls, against 6,019 on 259 in the shipped payload.

**The first re-take got this wrong.** I copied the current payload, which made
before and after identical, and three assertions failed at once: "the Retaliator
gained markers", "median coverage rose", "the population that proves it is the
fleet". The control measures a RISE and a copy of the payload has nowhere to
rise from. It refused in under a second, which is the control working - the
error was mine and it never reached a commit.

Taking it properly means building twice: no-inherit to produce this file, then a
normal build to put the payload back. The payload was checked byte-identical
afterwards.

## Re-taken 2026-08-30, on purpose, after the 4.10 pull

A baseline re-taken quietly and one re-taken on purpose are indistinguishable
six weeks later, so this is the record of which this was.

**The condition was checked first.** Sleven's rule for taking a snapshot at all
is that the four pinned negative controls - the Retaliator's ports 23, 24, 39,
40 - still hold. They do; section 2 of the control passes.

**What moved, measured rather than assumed:**

    RSI Perseus     35 -> 65 markers, 30 removed
                    C1's documented restructure: the port list goes 219 -> 179,
                    exactly -40, being twenty named hardpoint_torpedo_storage_
                    left/right_01..10 plus the twenty unnamed child ports they
                    carried. In 4.9 exactly one ship in the game had a
                    torpedo_storage port; in 4.10 none does.

    RSI Polaris     22 -> 131 markers, 14 removed
                    NOT in C1's documented three. Gained 109 CIG-positioned
                    ports in the pull.

    Drake Corsair   13 -> 39, and 8 ports moved. Three are a pure X mirror -
    (and PYAM Exec) same y and z, sign flipped. Five are a rack re-index: each
                    port's new position is the PREVIOUS port's old position,
                    which is a rack sliding by one slot because an entry
                    appeared at one end. No two ports share a position
                    afterwards - checked.

**Polaris and the Corsair were reported to C1 as undocumented consequences of
the pull.** They are consistent with CIG restructuring hardpoints, which is what
the pull did to the Perseus, and nothing about them reads as a placement fault.
