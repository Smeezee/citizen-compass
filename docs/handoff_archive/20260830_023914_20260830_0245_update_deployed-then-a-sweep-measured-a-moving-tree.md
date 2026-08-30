# Update — deployed and verified, then found a defect I had shipped. And the sweep after it measured a moving tree, so its nine failures are void.

**2026-08-30 07:45 UTC / 2026-08-30 02:45 local · Code (background session)**

## THE DEPLOY WENT OUT AND IS VERIFIED ON SERVED BYTES

    109 ok, 0 NOT RUN     GATE EXIT 0     20 files uploaded
    Version 8a200ac3-096e-4c6c-9a70-8bb04d40fbcf

    /                      HTTP 200    392,871 bytes
    /models/Hammerhead.glb HTTP 200  3,608,636 bytes
    PLACEHOLDER              0
    Unknown Manufacturer - 1 0
    4.99-CONTROL             0
    Torrent                  3   <- was truncated to 'MRX \'

C1's 107 corrected names, the US spelling, the countermeasure summary and the
1,450-part manufacturer fix are all live.

## THEN THE DEPLOYED-SITE CONTROL CAUGHT SOMETHING I SHIPPED

**The find page was publishing a checksum for a file it does not serve.**
`build_find_data.py` hashes the `_src` data file; **Q31's comment strip removes
1,169 bytes on the way into `_deploy`**, so the page told a visitor their
correct download was corrupt.

    the downloaded file hashes to exactly what the page claims   FAIL
    and its byte count matches too    991988 vs 993157

**That is mine, from yesterday, on the one page whose claim is that its numbers
can be trusted.** Not fixed by exempting the file from the strip - its header
names `build_find_data.py` on a public URL, which is the trace Q31 removes. **The
checksum moved instead**, because it is a promise about the bytes a person
downloads:

    find checksum: recomputed over the SERVED bytes (991988, ac431efc)

The drift control then flagged it as an undeclared transform, correctly, so it
is **declared by VERIFICATION rather than exemption**: it re-derives the hash
from what `_deploy` actually serves and requires the published figures to match.
A stale or hand-edited checksum still fails. 14 passed, 0 failed.

**And the sixth copy of the row-counting rule was where I said it would be.**
`_verify_picker_deployed.mjs`, found by the DEPLOYED control after shipping
rather than by the sweep. I wrote *"the sixth copy is the one that will be
missed"* and then missed it.

## THE SWEEP AFTER THAT IS NOT A MEASUREMENT

    101 ok, 9 failed          <- do not act on this

**C1 edited eight `_src` files during the run** - `device_engine.js`,
`download.src.html`, `kb_overlay.inc.html`, `keybinds.src.html`,
`stick-test.src.html`, `_layer.src.html`, `find.src.html`, `loadout.src.html` -
and added `checks/_verify_us_spelling.py` at **02:30:19**, eight minutes before
the receipt at 02:38:17.

**So the sweep read a `_deploy` built from a `_src` that no longer existed**, and
one of its nine failures is simply the new control having no RULE16 label yet:

    _verify_us_spelling.py: a NEW check with no RULE16 label

**I am not chasing the other eight.** Three controls disagreed with themselves in
both directions on 2026-08-28 for exactly this reason, and the lesson recorded
then was that it is one measurement taken during a write, not several defects.

**THIS IS THE THIRD TIME.** 08-28: C1 regenerated `data-layer/` mid-sweep. 08-29:
I edited `checks/` mid-sweep. Today: C1 edited `_src/` mid-sweep. **The sweep has
no lock and rule 14's own words apply - a rule that depends on everyone
remembering it is a convention, not a guard.** I closed the one perturbation I
owned, the drift control's rebuild. **The other two are still open by design.**

## WHAT I AM DOING

Rebuilding from the `_src` that exists now, sweeping once, and deploying only if
that sweep is clean. **If C1 is still editing, this will happen again**, and the
next honest step is not a fourth sweep - it is a way for a sweep to refuse to
start, or to declare itself void, when its inputs move underneath it.
