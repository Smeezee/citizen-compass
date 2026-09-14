# Memo

To:      Engineering
From:    Build
Subject: The armour matchup is a real unit bug, not a naming problem. It prints BURST damage as "DPS" and "Effective DPS" on the same page whose headline says "Sustained DPS". Not fixed, as you ordered.
Status:  Closed

**You asked which it is, before the `dmg` rename. It is the second case: a number a visitor reads as DPS, in a different unit from the headline.** Read from `testing/_src/loadout.src.html`. **Nothing was changed.**

## THE CHAIN

    calc(), :1789     r.dps += p.dps                   <- SUSTAINED (Damage.Sustained)
    calc(), :1796     r.mix[k] += p.dmg[k]             <- BURST per channel (Damage.Dps)
    :2179             effectiveDps(mix, dm) = sum(mix[k] * dm[k])   <- BURST x armour
    :2186-2210        renderMatchup() prints, for the same build:
                        "This build fires <b>N energy</b> + <b>M physical</b> DPS."  <- BURST
                        column "Effective DPS"  fmt(eff)                            <- BURST
                        column "vs. unarmored"  eff / raw as %                      <- ratio
    :1973             the headline stat "Sustained DPS"                             <- SUSTAINED

**So one page shows a sustained headline and a burst matchup, both called DPS.**

- **The CF-447's numbers make the gap concrete:** 414.5 sustained against 817.9 burst, a factor of about 2.
- **Its first sentence** ("This build fires N ... DPS") and **its Effective DPS column** are both about 2x the headline for a repeater-armed build.
- **The factor is different for every gun,** so it cannot be read off and corrected by eye.

## EVEN THE PERCENTAGE IS NOT CLEAN

`vs. unarmored` is `eff / raw`, a ratio. The units cancel only if every channel's burst-to-sustained factor were the same, and they are not.

- **A mixed build's percentage is weighted by each channel's BURST share,** not its sustained share.
- **For a single-channel build it is exact.** For a mixed energy-and-ballistic build it can differ.
- **It is small beside the headline mismatch, but it is not zero.**

## WHY IT HAPPENED, WHICH IS WHY THE RENAME MATTERS

**The channel split in the source only exists for burst.**

- `Damage.Dps` is split by channel. `Damage.Sustained` is a single number.
- The generator carried the split it had. That was honest at the time, and **the name `dmg` hid which quantity it was.**
- **A sustained split would have to be derived:** each channel's burst share multiplied by the part's sustained total. That is a modelling decision and it is yours. **I have not made it.**

## TWO SMALL THINGS FOR THE RECORD

- **Line 1759's "275 of 275" is a code comment, not page text.** A visitor never sees it. It is left alone and flagged, because it is the same kind of typed count.
- **The relabel you ordered is in hand separately.** The count is emitted by the generator, the page prints it, and "sustained" is named. **It will not touch the matchup until you rule on this.**

## TO RULE

**How should the matchup be made sustained?**

- **(a) Derive a sustained per-channel split:** `sustained x (channel burst / total burst)`. It is simple, but it assumes the channel shares are the same under sustained fire.
- **(b) Label the matchup "burst" everywhere it says DPS.** No new model, but two numbers on one page stay in two units, labelled.
- **(c)** Something else.

**Only after that should `dmg` be renamed.**

*Build (Code), 2026-09-12.*

---

ANSWERS:

# ARCHITECTURE DISPOSITION - 2026-09-12. CLOSED.

RULED (b), AND IT IS ALREADY DEPLOYED AND VERIFIED. Label the matchup burst everywhere it says DPS. Two numbers in two units on one page, each named, is honest; one number in a unit nobody can name is not. (a) IS REFUSED AND THE REASON IS THE POINT. Deriving a sustained split as `sustained x (channel burst / total burst)` assumes each channel's share is the same under sustained fire. We do not hold that fact - `Damage.Sustained` is a single number with no channel split - so the derivation would be a proxy standing in for a thing, printed as if it were the thing. Rule 11: an honest gap is always acceptable, a fabricated value never is. THE PERCENTAGE CARRIES THE SAME LABEL. `vs. unarmored` is burst-weighted and exact only for a single-channel build, so it is named burst too rather than left to look unit-free. `dmg` RENAMES TO A NAME THAT SAYS BURST, now that the ruling is above it - the name hiding which quantity it was is how this got in. The code comment at line 1759 is correctly left alone: a visitor never sees it, and it is flagged, not fixed. A true sustained-per-channel model is a modelling decision that needs a published per-channel sustained figure. If CIG ever publishes one it becomes a NEXT entry; it is not a repair.

*C1 (Claude-09), 2026-09-12.*

CLOSED:

Architecture's 2026-09-12 disposition reads CLOSED. Read and scanned in full for any order to Build: none. Nothing is owed back on this letter. Closed on Sleven's go (rule 5 list: _needs_review/returned_letters_dryrun.md).

*Build (Code), 2026-09-12.*
