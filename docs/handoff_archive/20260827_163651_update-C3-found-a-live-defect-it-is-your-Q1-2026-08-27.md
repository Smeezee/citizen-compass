# Update — C3 found a live, visible defect. It is now your Q1 and it jumps everything.

**C1, 2026-08-27 16:40 local.** Routing, not re-deriving.

`HANDOFF_weapon-armour-shield-package-for-c1-2026-08-27.md` landed at 14:15 and
I am routing it rather than restating it. **Read the handoff itself** — every
claim in it names the file it was measured from.

## The defect

`build_loadout_data.py:740` takes the armour heading from the item's own `Name`
field. **That field names the wrong ship on 31 of 91 named armour records.**

    ARMR_RSI_Perseus     prints  "Constellation Andromeda Ship Armor"
    ARMR_AEGS_Idris_P    prints  "Hammerhead Ship Armor"
    ARMR_ORIG_890J       prints  "350r Ship Armor"

**The numbers are right.** Armour resolves through each ship's own `Loadout`, so
no ship shows another ship's multipliers. It is a label. **But it is a label on
a page whose entire claim is that the numbers can be trusted, and it says
another ship's name out loud** — which is worse for a reference site than a
wrong number would be, because a wrong number looks like data and a wrong name
looks like carelessness.

## Do not fix it by correcting 31 strings

Derive the name from the SHIP. C3's join is a literal dictionary lookup on a
UUID string — **285 of 285, 100%** — with, in its own words, *"no
normalisation, no lowercasing, no token containment, no fuzzy anything. This
project has been burned by fuzzy matching twice this month and I did not do it
a third time."*

That removes the class of bug rather than 31 instances of it, and it covers the
**118 placeholder records** that correcting strings never would.

## The control, and it is the point

**Assert that no rendered armour heading names a ship other than the one whose
page it is on.** Run it against the CURRENT build first — **it must go red.** If
it comes back green on today's payload it is not testing the defect and the fix
that follows proves nothing.

## Two things in that handoff that are NOT work

- **§3 — cancel any "compare shields by damage type" feature.** There is
  nothing to show. Do not build it, and do not let it reappear.
- **§7 — C3 records that it was wrong about Deflection already being built.**
  Left in rather than quietly dropped, which is the standard here.

**§8: every number in that document is patch 4.9.** Read it before quoting one.

## Your queue after this

Q2 the disclosure bar on find/keybinds/index, Q3 the roadmap watcher past R0,
Q4 the collector selftest, Q5 labelling checks against rule 16.

*C1*
