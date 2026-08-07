# COLLECTOR — every open question, in one place. Nothing hidden.

    id      WO-COLLECT-01 rev 5 — companion: the unknowns
    from    C2, 2026-08-06
    for     C1 -> Claude Code
    why     Sleven asked for everything not-yet-known to be pushed forward
            rather than left in my head. This is that list.

**The collector's capture half is BUILT and working. The reading half is
entirely unbuilt, and every item below sits between here and there.**

**Ranked by what blocks the most.**

---

## TIER 1 — BLOCKS EVERYTHING. One answer unlocks the build.

**1.1 Is the game's UI font legible in a captured frame at 1920×1080?**

    open since   2026-08-02
    blocks       the glyph atlas, the reader, the vocabulary, all of it
    answered by  Sleven pressing the hotkey at a kiosk. Ten minutes.
    status       the grabber exists solely to answer this

**If the answer is no**, the fallback is capturing at native resolution with no
scaling and re-testing before anything else is designed. **Do not build the
atlas until a real frame has been looked at.**

**1.2 Is the aUEC balance on screen often enough to catch both sides of a
transaction?**

    blocks       the entire event recorder - rev 5 §4.7
    why it       the purchase-delta check is what makes the reader falsifiable.
    matters      Without it the collector has confidence scores and no proof.
    answered by  the same ten minutes. Open a kiosk and look.

**It is a mobiGlas element and may simply not be visible while a shop panel is
up. If it is not, §4.7 does not work and rev 6 has to find another proof.**

---

## TIER 2 — SHAPES THE DESIGN. Answer before building that part.

**2.1 Does the UI anti-alias differently at different UI scales?**
If yes, the atlas is per-resolution **and** per-scale, which multiplies
calibration work for the crew. Unknown. Testable with two screenshots at two
scale settings.

**2.2 Does column detection survive a scrolling list?**
Rows enter and leave mid-frame. **Class C structure detection is the least
tested idea in the whole design**, and getting it wrong pairs a name with the
wrong row's price — worse than no data.

**2.3 Is the chat region at a fixed position across UI scales?**
Rev 5 §4.12 makes chat zones a hard exclusion. **If the position moves, the
exclusion must be drawn by the player at first run** rather than shipped as a
constant. This is a privacy control, so it fails closed or not at all.

**2.4 Is shop stock stable enough for the inventory prior to help?**
The strongest prior in the design assumes a shop's stock list is fairly stable.
**If stock rotates heavily the prior is much weaker than claimed.**

**2.5 Is 6×4 / 150 ms / 4-reads-per-second right?**
All three are C2 guesses. **Config values, tuned on the first real session.
Believe the measurement over the document.**

**2.6 Is `labels.json` matching fast enough at 90,121 entries to sit in the read
path?** If not it moves to the review step, where time is free.

**2.7 Does WGC capture Star Citizen in exclusive fullscreen?**
Generally yes; untested here. DXGI and GDI fallbacks are already built.

---

## TIER 3 — CHANGES WHAT IT IS FOR. Sleven's call, not a technical answer.

**3.1 Does the collector's price role survive the UEX commodity pull?**

    what changed   UEX now gives 2,597 commodity price rows, median age 1 day
    what UEX lacks no game_version / patch / build on any price row
    the trade      screenshotting a price UEX refreshed an hour ago is
                   redundant. But every capture we take is patch-stamped,
                   which UEX structurally cannot do.
    C2's read      the defensible role is PATCH-ATTRIBUTED OBSERVATION,
                   not price coverage. rev 6 waits on this ruling.

**3.2 What is the honest pitch to a crew member now?**
Rev 5 told them they were closing the project's biggest gap. **That is no longer
true and they must not be told it.** The honest version is stock, runtime
payouts, tonight's board, refinery yields, and patch-stamped verification.
**Smaller, still real, and it has to be said plainly before anyone installs it.**

---

## TIER 4 — DATA UNKNOWNS THAT TOUCH THE COLLECTOR

**4.1 Do `SoldAt` / `BoughtAt` in `commodity_trade_locations.json` reflect live
4.9 behaviour or stale design data?** 96,717 pairs, never validated in game.
**The first commodity kiosk capture tests it.**

**4.2 What do the `Negative` arrays in `ProducesTags`/`ConsumesTags` mean?**
670 entries. Most likely "this place refuses X", possibly a demand modifier.
**Testable at a kiosk. Do not publish an interpretation until it is.**

**4.3 Is `FixedReward.Amount` the actual payout or a base before modifiers?**
`BonusEligible`, `Max` and `ReputationBonus` sit beside it. **Publish it as
"listed reward", never as "what you get" — and the collector's payout
observation is what settles it.**

**4.4 Do payouts vary by player?** Reputation, org, insurance, shard state.
**If they do, an observed payout is one player's number and must publish as a
range across observations, never as a fact.** Nobody has checked. **This is the
single biggest threat to the value of crew-collected payout data.**

**4.5 The `FixedReward` / `CalculatedReward` split is a 25% sample**, not a
census. A full scan timed out through the Cowork bridge. **Re-run locally.**

**4.6 Why do 109 commodities have trade locations when 206 exist?** Do not
present the difference as "cannot be traded" until someone checks.

---

## TIER 5 — OPERATIONAL, BEFORE THE CREW GETS IT

**5.1 Antivirus.** A small unsigned binary that reads game files and captures
the screen is exactly the shape Defender flags. **Expect it. Do NOT tell friends
to add exclusions — that is a bad habit to teach.** Plan for signing or accept
the friction. **Unresolved and it will hit on the first crew install.**

**5.2 Has the process-locked window matcher been proven to refuse?**
Code fixed it to match `StarCitizen.exe` only. **The order asked for a proof
against a browser titled to match. Confirm that test actually ran and passed
before any crew build ships.**

**5.3 What happens when two crew members capture the same shop minutes apart?**
The review pen has no dedupe rule specified. **Not urgent, but it will happen on
day one of crew use.**

**5.4 There is no versioning story for `names.dat` and the atlas.**
When a patch changes item names, every crew member's copy is stale. **Nothing in
rev 5 says how they get an updated one.** This is the first real distribution
problem and it is unaddressed.

---

## TIER 6 — KNOWN AND DELIBERATELY PARKED BY SLEVEN

    the RSI legal enquiry on description rights   parked, deliberately
    contacting CmdrQuattro / tool maintainers     parked
    Cornerstone image permission                  raised 2026-08-06, unanswered
    the site-wide design system                   proposal filed, no ruling

**Do not raise these. They are recorded so nobody mistakes them for oversights.**

---

## WHAT C2 IS NOT DOING, AND WHY

**Rev 6 of the collector spec is NOT being written yet**, deliberately.

It depends on 3.1, which is Sleven's ruling, and on 1.1 and 1.2, which are ten
minutes in game. **Writing it now means writing it twice**, and the first version
would be built on a premise — "we need the collector for commodity prices" —
that is already known to be false.

**Everything needed to build the reading half once those three land is already
in `docs/HANDOVER-collector-rev5-COMPLETE.md`.** Nothing is being held back.
