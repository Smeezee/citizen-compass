# Update — the drift control is fixed and proven. The deploy is now blocked by two controls that are both C1's, and one of them is finding a real, visible defect.

**2026-08-30 07:10 UTC / 2026-08-30 02:10 local · Code (background session)**

## THE FIX, AND WHY THE SECOND ATTEMPT WORKED

I measured instead of guessing, and there were two causes, not one:

    keybinds.html / loadout.html   diverged exactly at /* CC_DISC_CSS */
    find.src.html                  is CRLF; its output is LF

**The injection markers are themselves comments.** `<!-- CC_VENDOR_THREE -->`
and `/* CC_DISC_CSS */` - so stripping the source deletes the anchors the
segmentation is built on, and every page diverges at the first one. Stripping
the SEGMENTS instead fails differently: a segment can begin inside a `<script>`
block and the stripper then reads JavaScript as markup, which is why
`loadout.html` and its 437 template literals was the page that broke last night.

**Protect the markers, strip the whole document exactly as the build does, put
the markers back.** Plus the disclosure gap now compares against
`strip_css(_disc.css)`, because the CSS is substituted in and the page stripped
after.

    14 passed, 0 failed        --self-test exit 1

## IT IS A RECONCILIATION, NOT AN EXEMPTION, AND I PROVED THAT

Only the `_src` side is stripped, so a comment HAND-ADDED to `_deploy` still
has nothing to match against:

    planted a comment at the end of _deploy/download.html
      FAIL every copied file in _deploy is its _src source byte for byte
      FAIL and so is every copied file (moved: download.html)

Two independent assertions. `download.html` restored byte-identical. Section 5's
existing plants still pass through the new comparison, so the detection path is
whole.

**Declared honestly:** the control now imports the build's own stripper, so a
change to the STRIPPER passes here unremarked - the same trade
`attribution.TRADEMARK_HTML` already makes. `_verify_comment_strip.py` is what
closes it, by proving the stripper against node rather than against itself.

## THE SWEEP

    107 ok, 2 failed, 0 skipped, 1 NOT RUN, in 782s

    _verify_display_names.py        FAILED     C1's, OWNERS.md line 55
    _verify_marker_mesh_distance.py NOT RUN    C1's, line 57, needs draco3d
    _verify_picker_deployed.mjs     deployed-only, expected until this ships

**Everything of mine is green**, including the two guards I repaired and the
drift control.

## AND C1'S CONTROL IS FINDING SOMETHING REAL

    19 parts show a name that disagrees with the game's

    AEGS_Avenger_CML_Chaff   shows "Aegis Gladius - Noise Launcher"
                             game  "Aegis Avenger - Noise Launcher"
    ANVL_F7A_CML_Chaff       shows "Anvil Noise Launcher"
                             game  "Anvil Hornet F7A - Noise Launcher"

**An Avenger part is printing GLADIUS on the page.** That is the same shape as
Q1 - 31 ships printing another ship's name on their armour - on a page whose
whole claim is that the numbers can be trusted. It is C1's control and C1's
pipeline, and I am reporting it rather than touching it.

## THE DEPLOY IS STILL BLOCKED AND I HAVE NOT DEPLOYED

    GATE EXIT 1

Both blockers are C1's. **Nothing of mine stands between the payload and the
site any more**, and I am not weakening the gate to get past somebody else's
finding - least of all one that is right.

Uncommitted: `checks/_verify_deploy_drift.py`.
