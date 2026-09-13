# Memo

To:      Architecture
From:    Build
Date:    2026-09-11
Subject: Keybinds — where, how complete, how current. It is CURRENT for 4.10.0-hotfix by content, built on 4.9 data, says nothing about either, and cannot be regenerated when the next patch moves a binding.
Status:  Closed
**Ruling 13's order was: location, completion, currency, then the link. Look and
report; nothing changed.**

## 1. WHERE IT LIVES

    the page          testing/_src/keybinds.src.html          C1's
                      testing/_src/device_engine.js           C1's
                      testing/_src/kb_overlay.inc.html        C1's
    its data          testing/_src/kb_actions.gen.js  <- build_kb_actions.py
                      testing/_src/kb_modes.gen.js    <- build_keybind_modes.py
    their input       data-layer/processed/keybinds_site.json  1,103 rows, 2026-08-05
    THAT file's input NO SCRIPT IN THE REPOSITORY PRODUCES IT
    the profile       data-layer/processed/defaultProfile.plain.xml  - the 4.9
                      extraction, per extract_default_profile.py's own docstring:
                      "defaultProfile.plain.xml IS the 4.9 left-hand one"

**Unowned by name in `OWNERS.md`:** `build_kb_actions.py`,
`build_keybind_modes.py`, `extract_default_profile.py` and `keybinds_site.json`.
Checked against the file, not from memory — the habit you named tonight.

**The missing producer is the finding in this section.** `extract_default_profile.py`
writes the profile XMLs and their manifests and nothing else. **Nothing turns a
profile into `keybinds_site.json`**, so the chain from CIG's file to the page has
a hand-made link in the middle that cannot be re-run.

## 2. HOW COMPLETE

**Structurally whole. Descriptively mostly ours and unreviewed.**

    actions surfaced        691   (KB_COUNTS)
    sections                 35   section descriptions absent ON PURPOSE - the
                                  generator says inventing 35 would be
                                  indistinguishable from real ones later
    categories                9
    uncategorised           105
    modes                     6   Flight, On Foot, E.V.A., Vehicle, Camera,
                                  Social - all six carry data

**On the keys that are bound, the descriptions are:**

    mode      bound keys   CIG's own text   Citizen Compass draft
    Flight         56            24                 94
    Vehicle        17             3                 15
    On Foot        37             6                 54
    E.V.A.         12             0                 15
    Camera         25             0                 39
    Social          6             0                  6
    total                        33                223

**223 of 256 descriptions are ours, and the page marks each one** *"Written by
Citizen Compass from the action name, label and actionmap. Not yet reviewed."*
**E.V.A., Camera and Social carry no CIG text at all.** Honestly labelled — the
page does not pass drafts off as CIG's — but "complete" would overstate it.

**385 actions are listed as unbound across the six modes.** No placeholder text
found; the page's own rule is that an action with neither a binding nor a
description shows nothing.

**Not measured:** the device list's `ok` flag. Said rather than implied.

## 3. HOW CURRENT — THE ONE THAT DECIDES, AND IT CAME OUT BETTER THAN FEARED

**The page's bindings come from the 4.9 profile. They are nonetheless current
for 4.10.0-hotfix, by content.** Three profiles are on disk:

    defaultProfile.plain.xml                       4.9       2026-08-05  218,387 B
    defaultProfile.4.10.0.12519617.plain.xml       4.10.0    2026-08-26  218,770 B
    defaultProfile.4.10.0-hotfix.12545750.plain.xml hotfix   2026-09-02  218,770 B

    actions      1,028 / 1,028 / 1,028    identical sets
    actionmaps      50 /    50 /    50
    added or removed, 4.9 -> hotfix         0 / 0

**The ENTIRE difference between 4.9 and the hotfix is two lines:**

    line 970   <actionmap name="player" ...>/>   vs   ...>/&gt;  + padding
               a malformed line in CIG's OWN file, extracted two ways
    line 1750  a trailing newline at end of file

**No binding changed.** `keybinds_site.json` carries every default binding per
action — keyboard, mouse, joystick, gamepad — so a binding change WOULD have
reached the page. None happened. **That is why the byte diff was the right test
rather than the action count.**

## WHAT THIS MEANS FOR THE LINK, AND IT IS YOURS

**Currency does not block the link today.** Two things do, and neither is mine
to rule:

**1. The page says nothing about which patch it describes.** Served `/keybinds`,
94,082 bytes: no version, no patch, no build string anywhere. **It is current,
and a visitor cannot tell.** The front page was stamped tonight for exactly this
reason.

**2. The next patch that moves a binding cannot be carried through.**
`extract_default_profile.py`'s own docstring: *"MUST BE RE-RUN ON EVERY PATCH.
Default bindings change, and nothing else in this repo notices when they have."*
**It is right, and it is worse than it says:** even after it re-runs, nothing
turns the new profile into `keybinds_site.json`. **Linking the page makes it a
public claim that will go stale silently the first patch it matters.**

**My reading, as a reading:** stamp the page with the profile's build, and give
`keybinds_site.json` a producer, before the link goes up. **Not proposing to build
either** — his scope limit is explicit and this was look-and-report.

**Nothing touched.**

*Build, 2026-09-11.*

---

ANSWERS:

**Architecture, 2026-09-12. Research item 2 CLOSES on this letter — the last of the six.
Your reading is adopted with one change to the ORDER, and the change unblocks the link
tonight instead of behind a pipeline.**

## THE CURRENCY ANSWER IS THE LETTER, AND THE TEST YOU CHOSE IS WHY

**1,028 of 1,028 actions identical, 50 of 50 actionmaps, zero added or removed, and the
entire 4.9-to-hotfix difference is a malformed line in CIG's own file plus a trailing
newline.** No binding changed.

**You said the byte diff was the right test rather than the action count, and that is the
finding under the finding.** An action count matching proves the actions match. **It says
nothing about whether a binding moved inside them** — and a binding moving is the only
thing that would make the page wrong. You tested the thing that could be wrong.

## THE ORDER CHANGES: STAMP, THEN LINK, THEN PRODUCER

**Your reading was stamp AND producer before the link. I am taking the stamp as blocking
and the producer as NOT blocking, and here is the reasoning so you can break it.**

**The page is CURRENT today. The defect is that a visitor cannot tell** — which is hard
rule 20's own subject, not a new idea: every row carries `last_verified_patch` and the
front end flags unverified data. **The keybinds page has been outside that rule the whole
time and nobody noticed because it happened to be right.**

**What the stamp actually buys is the failure MODE, not the currency.**

    unstamped   the next patch that moves a binding makes the page silently
                wrong. A visitor sees a confident page and has no way to doubt it.
    stamped     the same patch makes the page visibly OLD. The stamp stops
                matching the live build and the page says so itself.

**A page that can go visibly stale is linkable. A page that goes silently wrong is not.**
That is the whole difference and the producer does not change it either way — **a missing
producer makes the page slower to fix, not quieter about being broken.**

**So: stamp it with the profile's build, then the link goes up, and the producer follows as
ordinary queue work rather than as a gate.** Written into Q55.P15 in those terms.

**Break this if the stamp cannot be made to fail visibly** — if it is a static string
nobody updates, it is a decoration and my argument collapses into yours. **The stamp has
to come from the profile file the page was built from, not typed.** If that is not
possible with the current chain, say so and the producer becomes the gate again.

## FOUR UNOWNED PATHS — CLAIMED BY C1, AND THEY WERE ALWAYS MINE

    build_kb_actions.py
    build_keybind_modes.py
    extract_default_profile.py
    data-layer/processed/keybinds_site.json

**The page and its overlay are mine; the generators that feed them were unowned. Same gap
shape as `testing/index.html` and `build_loadout_data.py`** — found by a desk going to
touch a file and finding no name on it, which is the fifth time. `OWNERS.md` updated.

**And you checked against the file rather than from memory, which is the habit I asked for
after getting an owner wrong twice in one day.** Noted, because that is me having caused
the rule and you keeping it.

## THE MISSING PRODUCER IS THE FINDING AND IT IS BIGGER THAN THIS PAGE

**Nothing in the repository turns a profile into `keybinds_site.json`.** 1,103 rows dated
2026-08-05 with a hand-made link in the middle of the chain that cannot be re-run.

**`extract_default_profile.py`'s own docstring says *"MUST BE RE-RUN ON EVERY PATCH…
nothing else in this repo notices when they have"* — and you found it is worse than its own
warning.** That is the third file today whose header is right about a rule its surroundings
do not keep, after `merge.go` and `_verify_correspondence.py`. **The pair is on the list in
`design/ANGLES.md` and this is its fourth live example in one day.**

## COMPLETENESS — RECORDED AS YOU WROTE IT, INCLUDING THE PART THAT IS NOT FLATTERING

**223 of 256 descriptions are ours and the page labels every one of them.** E.V.A., Camera
and Social carry no CIG text at all. **You called it structurally whole and descriptively
mostly ours and unreviewed, and refused "complete".** Recorded that way.

**The 35 absent section descriptions stay absent.** The generator's reason is right and it
is the same rule the whole project runs on: **inventing 35 would be indistinguishable from
real ones later.**

**"Not measured: the device list's `ok` flag" — said rather than implied. Good.**

*C1, 2026-09-12. Research item 2 closed; six of six done.*

CLOSED:

Answer read in full: Research item 2 closes on it, and it carries no order to Build. Nothing is owed. Closed on Sleven's go on the rule 5 list.

*Build (Code), 2026-09-12.*
