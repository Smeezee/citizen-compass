# ERRATUM — I said Deflection was not on the site. It has been on the ship page since 08-22, with better framing than I gave it. Two of the four claims in yesterday's finding survive; one is withdrawn and one gets sharper.

    from      C3 (Cowork), 2026-08-27
    corrects  FINDING_the-damage-multiplier-fields-exist-and-armour-is-
              mislabelled-2026-08-27.md, §2 and §6
    status    the finding stands EXCEPT as corrected here. Read both.
    cause     I measured the source data and never checked the build.

---

## 1. WITHDRAWN — "Deflection is not on the site, not in the schema, not in any brief"

**False on the first count and on the third.** `testing/_src/loadout.src.html`
renders it, and `build_loadout_data.py` line 743 extracts it:

    ("PenetrationResistance", "pr"), ("Deflection", "df")

The page's own words, which are better than mine:

> *"Damage below these values is deflected outright."*

**Code stated the mechanic flatly where I hedged it.** §2 of the finding said *"I am
not asserting the mechanic"* and offered threshold-versus-multiplier as open. The
shipped page already asserts it. **One of us is wrong and it is not settled by either
of us saying it** — but the honest position is that my §2 presented as a discovery
something that was built five days earlier, and it should not have.

**Penetration resistance is also rendered**, and so is a "what gets through" block for
damage reaching internals. Both were in my finding's list of fields nobody had used.

**Also wrong:** the finding treated `Armor.DamageMultipliers` as unused. CURRENT-STATE
has said since 08-22 that *"armour is a real dimension now, ten distinct
damage-multiplier profiles"*, and the page computes effective DPS per hull from them.
**I counted nine distinct profiles across 209 items and the site says ten. That gap is
worth a look** — most likely the template or placeholder records — but it is a
reconciliation, not a finding.

**Root cause, and it is the same one as the shared-models erratum on 08-14:** I
measured a source file and reported what the project does with it without opening what
the project does with it. **Measuring the input is not measuring the system.**

## 2. STANDS, and it is the part that matters — every shield in the game is identical

Unchanged. 73 shield items, one Absorption pattern, one Resistance pattern.

**Checked against the build this time:** the ship page shows shields as HP and regen
only. There is no absorption or resistance display anywhere in `loadout.src.html`.
**So this is not a rediscovery — it is a reason not to build one.** Any future brief
proposing "compare shields by damage type" should be closed by pointing here: there is
no choice in the game to show.

The one sentence it supports is still worth weaving in: shields stop all of an energy
shot and at most 45% of a ballistic one, and no shield you can buy changes that.

## 3. SHARPENED — the mislabel defect is live, reaches the page, and here is the line

Confirmed further than the finding did. `build_loadout_data.py` line 740:

    "n": (it.get("stdItem") or {}).get("Name") or it.get("name")

**Both of those fields carry the wrong name.** Verified on five records:

    ARMR_RSI_Bengal      stdItem.Name = "Aurora Mk I MR Ship Armor"
    ARMR_AEGS_Idris_P    stdItem.Name = "Hammerhead Ship Armor"
    ARMR_ORIG_890J       stdItem.Name = "350r Ship Armor"
    ARMR_RSI_Perseus     stdItem.Name = "Constellation Andromeda Ship Armor"
    ARMR_AEGS_Avenger_Stalker  correct

That value is rendered as `${a.n}` in the hull-armour heading. **So the 890 Jump's
ship page names its armour "350r Ship Armor" and the Perseus names its own
"Constellation Andromeda Ship Armor."**

**The numbers are right and only the name is wrong.** The page resolves armour through
each ship's own `Loadout`, so no ship is showing another ship's multipliers. That
narrows the defect from what §3 implied — it is a labelling bug, not a data
mix-up — **but it is visible to every visitor and it says the wrong ship's name out
loud on a page whose whole claim is that the numbers can be trusted.**

**31 of 91 named armour records are affected. 118 more are `<= PLACEHOLDER =>`** and
whatever the page does with those needs its own look.

**The fix is §4 of the finding and that part stands:** the wiki gives every one of 285
vehicles an `armor.uuid`, and all 285 join to a scunpacked armour item by exact UUID
lookup. Deriving the label from the ship rather than from the item's own broken name
removes the class of bug rather than correcting 31 strings. **Whoever owns
`build_loadout_data.py` decides — I am not writing to it.**

## 4. What this erratum does not touch

The 285/285 join (§4 of the finding), the distortion mechanic (§2b), the
`resistance_multiplier` open question (§5), and the 4.9 patch caveat (§7) are all
unchanged and were all checked by measurement.

## 5. What I checked this time

`build_loadout_data.py` for the extraction and the naming line;
`testing/_src/loadout.src.html` for the rendering of deflection, penetration
resistance, damage multipliers and shields; `CURRENT-STATE.md` §"THE SHIP PAGE IS
BUILT" for what was already claimed. **Read, not inferred.**

**Did NOT check:** whether the deployed site matches the source I read, or what the
page renders for the 118 placeholder-named armour records.
