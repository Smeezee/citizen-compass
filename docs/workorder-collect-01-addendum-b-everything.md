# ADDENDUM B to WO-COLLECT-01 rev 3 — collect everything, and what that actually takes

    id       WO-COLLECT-01 rev 3, addendum B
    from     C2, 2026-08-06
    for      C1 -> Claude Code
    origin   Sleven: missions and payouts, the star map, jump routes, ship names,
             fuel cost per jump per ship. "Program it to collect everything we
             possibly can."

**Sleven is right, and one item on his list is worth more than everything in
addendum A. But "everything" needs a second mechanism the collector does not
have, and it needs one hard subtraction.**

---

## 1. THE THING THAT MAKES THIS BIGGER — mission payouts are not in any file

**Measured and on record in `claude/build-spec-descriptions-and-blueprint-index.md`
§2.4:**

> `CalculatedReward` **is a boolean, not an amount** — 8,260 `true`, 87 `null`,
> no numbers. The reward is computed at runtime. **There is no payout figure in
> this data.**

We hold 5,108 contract definitions with the mission giver, type, faction, time
limit, reputation gate, legality and full text. **We do not hold what a single
one of them pays, and we cannot, because CIG does not ship the number.**

**That makes observed payouts the highest-value target on the entire list**, above
commodity prices, because commodity prices at least exist somewhere else and this
does not. It is not recoverable by better extraction, a different source, or more
effort against the game files. **Somebody has to run the mission and watch the
number.**

---

## 2. THE MISSING MECHANISM — an event recorder, not a reader

**Sleven's list splits into two kinds of thing, and rev 3 only builds one of
them.**

**Kind one — text on a screen.** Mission titles, givers, payouts advertised on a
board, place names, ship names, prices. **The reader in rev 3 plus addendum A
already handles all of it.** Adding these costs a vocabulary entry, not code.
This part is genuinely nearly free.

**Kind two — a value's change across an event.** *"How much fuel does it take to
jump from here to there in this ship"* **is not written anywhere on the screen.**
Nothing displays it. It is: read the gauge, jump, read the gauge, subtract — and
know which ship, from the log.

**That is a different component.** It watches one small region continuously,
stores the value, waits for an event, reads again, and records the difference.
**The output is a measurement, not a transcription.**

**Build it as its own thing.** It shares the atlas, the capture, and the zone
grid, and nothing else. **It is roughly a tenth of the code of the reader and
produces data no competitor holds.**

---

## 3. THE DELTA TABLE — every before/after worth recording

| watch | across | gives | held anywhere else? |
|---|---|---|---|
| **aUEC balance** | mission turn-in | **actual payout** | **no — §1** |
| **aUEC balance** | a purchase | **price actually paid** | confirms the read — §4 |
| **aUEC balance** | a sale | **actual sell price** | 171 of 7,728 items only |
| **quantum fuel** | a jump | **fuel per route per ship** | §7 |
| **hydrogen fuel** | flight time | burn rate per ship | no |
| **cargo hold** | loading | what was loaded, in SCU | no |
| **reputation** | mission turn-in | rep gained, per mission | partly — `ReputationGained` exists |
| **wall clock** | A to B | real travel time | no |
| **ship HP / status** | any event | damage taken | no |

**Every row is arithmetic over two reads of a small region.** Same atlas, same
zones. **The digits are the most reliable thing on screen — ten glyphs, high
contrast — so this is the most accurate half of the tool, not the riskiest.**

---

## 4. THE DELTA THAT PROVES THE READER — rule 12, properly

**The strongest single reason to build the event recorder is not the data. It is
that it makes the OCR falsifiable.**

The kiosk says 4,050. You buy it. The balance drops by 4,050.
**The read is now confirmed by arithmetic, not by confidence score.**

If the balance drops by 4,650, the reader misread a digit and we know it, exactly,
on that row. **That is a check that can genuinely fail and names its own cause —
which is the standing bar, and which no confidence threshold ever meets.**

**Every confirmed purchase is a labelled training example for the atlas, for
free.** Drift in the agreement rate is an early warning that CIG changed the
font, before the data degrades.

---

## 5. THE SUBTRACTION — do not collect what we already hold

**Reading something off a screen when it is already sitting in a file on disk
produces worse data at higher cost.** Three of the five things on Sleven's list
are in that category.

| Sleven's item | what we already hold | verdict |
|---|---|---|
| **mission names, givers, types, factions, locations** | **5,108 contracts** with `DisplayTitle`, `MissionGiver`, `MissionType`, `Faction`, `TimeToComplete`, `ReputationPrerequisite` (named standing tiers), `Illegal`, `Chance`, `LocationPools[].ResolvedLocations[]` — 22 distinct givers measured | **do not read. Already better than a screenshot.** |
| **star map places** | **1,774 entities with x/y/z and parent hierarchy** (`starmap_positions.json`), 965 trade locations, plus the full place hierarchy | **do not read.** |
| **ship names** | 316 game files, 254 live, resolved | **do not read.** |
| **what a mission pays** | **nothing — it is a boolean** | **read it. §1** |
| **which missions are on the board here, tonight** | **nothing** — the files say where a mission *can* appear, never what is *offered* | **read it. §6** |
| **fuel per jump** | possibly derivable — §7 | **check first, then measure** |

**Subtracting what we already have does not shrink the idea. It concentrates
it** — what remains is exactly the live, the observed, and the derived, which is
the only category anyone can beat us on and the only one that ages.

---

## 6. THE MISSION BOARD — the part that is genuinely missing

**The contract files describe the pool of missions that exist. They never
describe the board.**

Observable and held nowhere:

    which missions are actually offered, at this terminal, at this time
    the payout each one advertises          (vs. what it pays - §3)
    how the board differs by location       files give a pool, not an outcome
    how it differs by reputation            validates ReputationPrerequisite
    how offers rotate over a session

**This is a mobiGlas panel — a scrolling list of titles and numbers, the same
shape as a commodity kiosk.** The reader handles it with no new machinery, and
the giver and type resolve against lists we already hold, so **most of each row
is confirmed rather than read.**

**One real caution:** CmdrQuattro's Blueprint Finder already shows "reputation
requirement and payout per mission." **He has payout numbers from somewhere and
I have not checked how.** Before building this, look — the same discipline that
stopped us rebuilding Star Binder. **Observed payouts with provenance and a patch
stamp would still be better than an unattributed figure, but know what exists
first.**

---

## 7. FUEL PER JUMP — check the files before building the rig

**Do not build a measurement rig for a number that may already be on disk.**

Quantum drives are a component category in `ship-items.json` and drive specs
plausibly carry a fuel consumption rate. **Whether they do is unverified — I have
not opened it.** If they do, fuel per jump is `distance x rate`, and we already
hold coordinates for 1,774 entities, so **the whole table is computable today
with no capture at all.**

**Check that first. One file, one look.**

**Measurement still has value afterwards**, for a reason worth stating: spec rate
and observed consumption differ — spooling, partial burns, drive efficiency.
**A computed table validated against observed jumps is a stronger claim than
either alone**, and the disagreement is itself the interesting finding.

### And the same warning applies to the star map

**`starmap.json` is 3.0 MB and has never been inspected.** The location note
from 2026-07-31 flags it as possibly carrying **jump point and route data** beyond
the positions file. **If routes are in there, "where can you jump from where to
where" is already answered and needs no screen reading at all.**

**Two files, both on disk, both unopened, both potentially removing a build step.
That is the cheapest work on this page.**

---

## 8. WHAT "EVERYTHING" ACTUALLY COSTS — three constraints, stated plainly

**The instruction is right. Taken literally it produces a tool that collects
everything badly.** Three specific reasons:

**1. The read budget is fixed, so targets divide it.** Rev 3 caps reads at 4
regions/sec, and that cap is what makes 24 zones affordable. **Adding targets
does not add capacity — it splits it.** Forty things watched at once means each
is watched a fortieth as often, and a scrolling list read at a fortieth rate
misses most rows. **Priority is not a nicety here, it is arithmetic.**

**2. Vocabularies collide.** Throwing 5,108 mission titles into the same match
pool as 7,728 item names means they compete. A mission titled *"Arclight"*
competes with the pistol, and **every list added makes every other list slightly
less accurate.**

**The fix is cheap now and expensive later: namespace the vocabulary by
context.** A zone whose learned content class is *shop list* matches against items
and prices only. A zone classed *mission board* matches titles, givers and
factions only. **Rev 3's zone learning already produces the classification — this
just uses it.** Retrofitting it after the vocabulary is one flat file is a
rewrite.

**3. Some of it is already ours.** §5.

---

## 9. HOW TO GET EVERYTHING ANYWAY — sessions, not simultaneity

**The resolution is that "everything" does not have to happen at once.**

**Session profiles.** A small selector at startup: *shopping · missions ·
hauling · mining · exploring · everything*. The profile sets which vocabularies
are live and which zones get budget priority. **Nothing is disabled — the budget
is aimed.**

**Run a shop session tonight and a mission-board session tomorrow, and inside a
week everything on the list is covered — at full accuracy each time, instead of
everything at once at a fortieth of it.**

**And this is the generic version the project's own architecture rules ask for.**
Recognizers stay generic, vocabularies are data files, profiles are a list.
**Adding a target later costs a list entry, not a code change.** That is
"collect everything we possibly can" as a design property rather than a switch —
and it is the difference between a tool that survives new game systems and one
that gets rewritten when CIG ships a feature we did not anticipate.

**`everything` stays as a profile.** It is the right mode for a long session
where nothing specific is being hunted, and it is honest about the trade: wide
coverage, lower per-target rate.

---

## 10. THE FULL TARGET LIST, REVISED

**Ranked by value = (nobody else has it) x (we cannot get it another way).**

    1   mission payouts, observed          the number does not exist in any file
    2   commodity prices                   zero rows held; vocabulary gap - add. A
    3   mission board contents by place     files give a pool, never the board
    4   stock levels and availability      nobody holds this
    5   price actually paid                 and it proves the reader - §4
    6   shop identity per visit             halves every other target's metadata
    7   price freshness                     median 66 days, the site's whole position
    8   fuel and travel cost per route      check the files first - §7
    9   refinery rates and yields           not in any file
    10  rental and fuel prices              small, absent, easy
    11  reputation gained per mission       partly held, worth validating
    12  kiosk item stats                    a cross-check on source 1, not new data

**Rows 1 through 3 are the build.** Everything below comes free from the same
zones, the same atlas and the same vocabularies pointed at a different screen.

---

## 11. WHAT THIS CHANGES IN THE BUILD ORDER

Rev 3 §8, amended:

    2b.  inspect starmap.json and the quantum drive entries in
         ship-items.json BEFORE anything else here. Two files, on disk.
         Either may delete a build step outright.                        §7
    4b.  namespace the vocabulary by zone content class from the start.  §8
    5b.  the event recorder, on aUEC balance only, at a purchase.
         Smallest possible version, and it is what makes the reader
         falsifiable.                                                    §4
    6b.  session profiles.                                               §9
    9.   mission board reading, after commodity kiosks - same screen
         shape, higher value, but check CmdrQuattro's source first.      §6

---

## 12. NOT VERIFIED

- **Whether quantum drive specs carry a fuel consumption rate.** §7. Unopened.
- **Whether `starmap.json` holds jump routes.** §7. 3.0 MB, never inspected,
  flagged as a candidate on 2026-07-31 and never followed up.
- **Where CmdrQuattro's payout figures come from.** §6. Look before building.
- **Whether the aUEC balance is on screen often enough** to catch both sides of a
  transaction. It is a mobiGlas element and may not be visible at a kiosk.
  **If it is not, §4 does not work and the whole event recorder weakens.**
  **This is the assumption the section rests on and it is untested.**
- **Whether the mission board is readable while scrolling.** Class C structure
  detection on a moving list is the least tested idea in either addendum.
- **Whether payouts vary by player** — reputation, org, insurance, shard state.
  **If they do, an observed payout is one player's number and must be published
  as a range across observations, never as a fact.** Nobody has checked.
