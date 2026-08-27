# ORDER — Four things Sleven found using the site

    from    C1
    date    2026-08-23
    for     Code
    status  RUN CONTINUOUSLY, R1 to R4. No decision gates.
    note    R1 turns out NOT to be a defect. Read it before assuming it is.

**Ledger entry per item with the commit sha. Rule 12 control on every item with a
negative control that could actually fire. Deploy to testing after each. No
`git add -A`, no live deploy.**

---

## R1 — The Reclaimer has no hardpoint names. IT IS NOT BROKEN, AND THAT IS THE PROBLEM.

**Sleven:** *"The Reclaimer doesn't have the proper information like the other
ships does. You see the hardpoints, they're there, you click on them, it brings
up what it is... everything works the way it's supposed to, but it doesn't have
the names like the other ones do."*

**Measured: the Reclaimer has 15 markers, every one resolving to a real port with
a real hardpoint name and a fitted part. Nothing is missing.** It is **one over**
H1b's threshold of 14, above which labels default to off.

    159  hulls carry markers
      7  are over the threshold

      35  RSI Perseus
      24  RSI Polaris
      23  Aegis Idris-P
      23  Aegis Idris-M
      17  Origin 890 Jump
      16  RSI Constellation Andromeda
      15  Aegis Reclaimer        <- one over the line

**So the feature worked and the person using it concluded the page was broken.
That is the third time tonight** — the silent markers, the panel labelled `Look`,
and now this. **A working feature nobody can tell is working is not a working
feature.**

### R1a — Let the solver decide, not a counter

**14 is an invented number and it is doing the job badly.** The real question is
not *how many markers are there* but *can they be labelled without colliding* —
and `solveLabels()` already answers that exactly. It reports how many it placed
and how many had no room.

**Replace the count threshold with the solver's own answer.**

    solver places ALL of them, zero overlaps  ->  labels ON by default
    solver cannot place some                  ->  labels OFF by default,
                                                  and the page says how many
                                                  and why

**The Reclaimer's 15 almost certainly place cleanly. The Perseus's 35 do not —
26 placed, 9 with no room, measured.** That is the honest line, and it moves
itself when a hull changes rather than needing anybody to re-pick a number.

### R1b — The state has to be legible without being read

The count line exists. It did not stop Sleven concluding the page was broken, so
it is not doing its job. **When labels are off by default, that must read as a
CONTROL a person wants to press**, not a status caption — and it must say why in
its own words, e.g. *"35 hardpoints · 9 have no room · show all labels anyway"*.

    CONTROL: assert the Reclaimer renders labels ON by default and the Perseus
    OFF, from the solver's placement result rather than from a count.
    NEGATIVE, load-bearing: assert a hull the solver CANNOT fully place defaults
    OFF - otherwise "everything is on" passes.

## R2 — The display controls belong to the whole site, not the ship page

**Sleven:** *"What about the rest of the page? What if people aren't happy about
the way the page looks?"*

H1g's brightness, contrast floor and colour work is on the ship page. **The home
page, FIND, keybinds and every other page have none of it**, and the reason it
exists — a second monitor in a dark room for hours — has nothing to do with which
page is open.

**One control, site-wide, in the site chrome rather than in the viewer.** Day /
Night / Blackout plus the fine slider, dimming everything on whatever page is
open. **It uses the same stored setting as the ship page — one preference, not
two**, so a person who sets Blackout once never sets it again anywhere.

**The ship page keeps its own viewer controls** — style, hull colour, line
sliders. Those are about the model. **Brightness is about the page.** Two
different things that must not be merged into one panel.

    CONTROL: set Blackout on the home page, navigate to a ship page, assert it is
    still Blackout and that the SAME stored key drives both.
    NEGATIVE: assert the viewer's hull-colour setting does NOT change when
    brightness changes. They are separate preferences.

## R3 — Feedback on every page, carrying what the person was looking at

**Sleven:** *"It needs to be on every single page. So if the user wants to send a
review about a particular ship... 'I found this with this ship.' That way we can
track down this information quicker and faster."*

**Today feedback is a tab on the home page.** Somebody who spots a wrong number on
the Gladiator has to leave the Gladiator, find the tab, and then describe in prose
which ship they meant.

**Put it on every page, and make it carry its own context automatically:**

    the page they were on
    the ship, if there is one - by ClassName, not display name
    the tab they had open - Loadout, Engineering, Liveries, Where to buy, Specs
    the selected port, if one was selected
    the data snapshot and patch the page was built from

**The person writes what is wrong. The page supplies where.** A report that says
*"the DPS looks wrong"* is nearly useless; the same report stamped
`AEGS_Gladius_Valiant · Loadout · port 57 · snapshot 20260801T204744Z · 4.9` is
actionable immediately.

**Show them what is being attached before it sends.** No hidden payload — this
site does not do that.

**Keep it out of the way until it is wanted.** A small persistent control in the
chrome, not a banner. It must not cost page height on a page measured at 1080 of
1080.

    CONTROL: open feedback from a ship page with a port selected and assert the
    context block contains the ship's ClassName, the tab and the port.
    NEGATIVE: open it from the home page and assert the ship fields are ABSENT
    rather than empty strings or stale values from the last ship viewed.

## R4 — GOING BACK MUST GO BACK

**Sleven, and this is the one that actually costs him time:** *"If I'm sitting at
the very bottom of the page and I click the Cyclone TR, it takes me to the page.
I wanna look at the other Cyclone — bam, right back to Avenger Stalker at the
very top. Fix it."*

**Returning to the ship list must restore the exact scroll position AND the state
the list was in** — the search text, the role filter, the sort, whichever ship
was highlighted. A person comparing four Cyclones should never scroll the same
250 rows four times.

**This applies to every list-to-detail move on the site, not just ships:** FIND's
results to an item, manufacturers to a maker, the keybind action list.

- **Browser Back and the page's own "All ships" control must behave
  identically.** Two ways out that land in different places is its own defect.
- **Restore on load, not after a repaint** — a visible jump to the top followed
  by a scroll down is worse than the current behaviour.
- **The list state survives a reload**, so a shared link or a refresh does not
  dump somebody at the top of 254 rows.
- **Returning to a list you have never visited puts you at the top**, which is
  correct — restore what was stored, do not invent a position.

    CONTROL: scroll the list to a known offset, open a ship, return by BOTH
    routes, assert the offset is restored to within a few pixels each time.
    CONTROL: apply a search and a role filter, open a ship, return, assert both
    are still applied and the same row is still under the cursor.
    NEGATIVE, load-bearing: return to a list never visited in this session and
    assert it is at the TOP. A build that restores a stale offset from a
    different list passes every other check here.
