# Update - ORDER rev 2 received, B0 through B9, starting now

`docs/ORDER_the-picker-redesign-2026-08-22.md`, rev 2, consolidated. It replaces
rev 1 at that same path - nothing from rev 1 survives except by being restated,
and there is no timestamped second copy to go looking for.

Ten items, run continuously, no decision gates.

## What B0 actually is

Not "some ships have not been done". Every ship has been done, the markers are
drawn for the right ports in the right places, and **they are not clickable and
do not say so.**

    1,200 hull markers on 157 hulls
      418 clickable        34.8%
      782 SILENT           65.2%
       61 hulls where EVERY marker is silent

`selectPort()` opens with `if(!swappable(slot)){ sel=null; renderPicker();
return false; }` - a fixed port clears the selection and re-renders the same
empty prompt, which from the outside is indistinguishable from a broken button.
`renderMarkers()` draws a marker for every `LOADOUT_MARK` entry without asking
whether it can be selected.

Origin 400i: 10 markers, 2 clickable, 8 silent - and the silent ones are
`hardpoint_missile_left/right` and `hardpoint_remote_turret_top/bottom`, the
four things anybody would click first.

The order names the defect class, and it is one this project already knows:
**the previous control asserted that a click reached `selectPort`, which it did
- on a port that then refused it.** The mechanism was asserted; the experience
was not.

## The run rules I am holding myself to

- Rule 12 control on every item, driven through behaviour. If an item's control
  could be satisfied by a string being present in a file, it is the wrong
  control.
- Ledger entry per item with the commit sha, as I go.
- No `git add -A`. No live deploy. No release. No RSI-sourced asset touched.
- Testing deploys are automatic per
  `RULING_testing-deploys-are-automatic-2026-08-22.md`.

## Order of work

B0 first and alone - it is the one that matters, and B8's acceptance test is
the Origin 400i with all 10 markers responding. B1-B7 after it, in order, then
B8 sweep-deploy-verify and B9 the census.

Starting with reconnaissance of `loadout.src.html`'s selection path so B0's
control drives the real thing rather than a reimplementation of it.
