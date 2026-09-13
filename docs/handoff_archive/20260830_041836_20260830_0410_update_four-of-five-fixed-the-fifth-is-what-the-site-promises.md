# Update — four of the five sweep failures were my controls asserting house style. The fifth is missing attribution text and is not mine to write.

**2026-08-30 09:10 UTC / 2026-08-30 04:10 local · Code (background session)**

New operating mode read and taken: keep going, four stops only, everything else
is a DEFERRED line.

## FIRST, A CORRECTION I OWE

I called seven failures "void" during the moving-tree sweep. **Five of them
survived onto a stable tree, so waving away the whole set was wrong.** The
concurrency was real and so were the failures; one did not cancel the other.

## FOUR WERE CONTROLS PINNING WORDS INSTEAD OF BEHAVIOUR

    _verify_ship_name_route.mjs   forbade any function NAMED decorate(
    _verify_shared_viewer.mjs     same check, same false red
    _verify_label_threshold.mjs   asserted "all labelled" - British spelling
    _verify_damage_readout.mjs    asserted the literal "one shot, not per second"

**The decorate() pair is the interesting one.** The old defect was a rewriter
that edited every name cell after render. C1 added a GLOSSARY decorator that
shares the name and does the opposite - opt-in per root, skips anything already
marked, and its own comment says a glossary that rewrites the whole document
*"is how you end up with PDC underlined inside somebody's ship name"*.

**A name is not a behaviour.** `gamelog_mine.go` records the same lesson from
the other side: *"matched on the PAYLOAD SHAPE, never on the emitting class
name"*, because CIG renamed a class and a name-keyed parser went silent. Here
the name collided instead and a correct page went red. Both now assert that no
decorate is HANDED THE NAME-CELL CONTAINER, which is what was actually wrong.

The other two are the same shape as `_verify_panel_findable.mjs`'s `colour`:
Sleven's US-spelling instruction reached the copy and C1 rephrased a caveat.
**A control that asserts house style fails the day house style changes.** The
damage row still says the figure is a single volley - *"fired once. Not per
second"* - which is the claim; the sentence changed and the claim did not.

All four green.

## THE FIFTH IS A STOP, AND IT IS STOP #2

    _verify_find_wording.mjs
      "says UEX rates the submissions"    x3, on item / terminal / home

The page no longer contains *"UEX rates how much it trusts each submission"*.
It still says UEX reported the price and when the row was updated, but the
sentence about how much UEX trusts a submission is gone.

**That is what the site promises a visitor about where its prices come from and
how much to trust them**, on a page whose entire claim is that it does not
overstate. `find.src.html` is C1's, and the wording is Sleven's territory by
rule. **I am not restoring it from memory and I am not relaxing the control to
match a page that says less** - the control's own comment says pushing the page
toward saying less is the opposite of what it is for.

**The deploy stays blocked on this one control.**

## DEFERRED - and one conflict worth naming once

The new instruction says to write DEFERRED lines at the bottom of `NEXT.md`.
**`OWNERS.md` says Code never edits `NEXT.md`.** I am putting them here instead,
where C1 reads them, rather than breaking rule 14 to follow a rule about not
stopping. **One line to resolve: either Code gets a DEFERRED section of its own,
or C1 transcribes these.**

    D1  _verify_find_deployed.mjs and _verify_picker_deployed.mjs are
        deployed-only and stay red until the redeploy - expected, not a defect.
    D2  the "represented, not drawn" rule is now written out in four files.
        One shared helper would stop the seventh copy being missed.
    D3  consent text is 2838 chars against a 2600 dialog limit - Sleven's call,
        recorded in d66dfbb.
    D4  loadout_data.gen.js still says last_verified_patch 4.9 while the header
        says 4.10 was checked separately. Q46, Sleven's go-ahead.
    D5  gamelog_mine.go's header records 240s for the archive dig; measured
        35.1s. Stale by 7x for anyone planning against it.
