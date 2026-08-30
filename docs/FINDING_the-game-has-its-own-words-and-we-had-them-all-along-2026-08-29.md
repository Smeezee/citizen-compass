# FINDING — CIG ships the words the game puts on screen, 90,363 of them, in a file that has been on this machine since July. We never opened it, and 112 names on the live test site are wrong because of it.

    from    C1 (Cowork), 2026-08-29
    rule    Sleven: "if they use something in the codes or in the files, that's
            different than what the game uses. That's what we need to use."
    source  labels.json, scunpacked snapshot 20260827T225641Z, 11 MB

---

## 1. I WAS ABOUT TO FIX THIS THE WRONG WAY

Hours before this, I filed a finding saying 59% of our hardpoint labels were
CIG's file shorthand and recommended a translation table — starting with
expanding **`mav` to "Maneuvering"** across 348 labels, on the authority of
CIG's own developer post naming the four thruster types.

**Sleven's correction was one sentence and it was right.** What CIG calls a
thing *in the files* and what the *game shows a player* are different questions,
and only the second one matters. So I went and found the second one:

    item_nameaegs_idris_mav_fixed_civ   ->   "Fixed Mav Thruster"
    itemPort_hardpoint_PDC              ->   "PDC"

**The game says "Mav Thruster" on screen. It says "PDC".** Expanding either
would have taken us further from what a player reads, not closer. **The
developer post was the file side. I had the wrong side of the same company.**

## 2. WHAT `labels.json` IS

**90,363 entries. The strings the client renders.** Present in every snapshot
we have taken since July.

    item_Name*     9,584   component display names
    itemPort_*       381   hardpoint display names

**CIG's own hardpoint wording, which is a style we should be copying:**

    itemPort_Hardpoint_Weapon_Wing_S1_Left   ->  Weapon - Left Wing 01
    itemPort_hardpoint_Left_Pylon_01         ->  Missile Rack - Left
    itemPort_hardpoint_shield_generator_left ->  Shield Generator - Left
    missile_01_attach                        ->  Missile Attach Point 01

That last one settles `attach`, which I had listed as an inference.

## 3. THE COVERAGE PATTERN IS ITSELF A FINDING

    guns        41%      thrusters     0 of 941
    PDC         39%      cargo grid    0 of 223
    weapons     34%      fuel          0 of  74
    shields     25%      countermeasure 0 of  67
    coolers     25%      radar         0 of  15

**CIG localises what a player can pick, and nothing else.** Zero of nine hundred
and forty-one thruster hardpoints has a name, because nobody has ever chosen one.

**So `Thruster Mav Body Left Bot` is not a label waiting to be translated. It is
a label the game never shows anyone.** There is no in-game term to match,
because in-game there is no term. Our own plain words are the right answer there
— and the page should say they are ours rather than implying CIG wrote them.

## 4. AND THEN THE PART THAT IS LIVE RIGHT NOW

Checking our 3,943 displayed names against CIG's:

    61   show CIG's own placeholder text:  <= PLACEHOLDER =>
     6   truncated at an escaped quote
    26   show a raw class name, underscores and all
    19   disagree with the name the game shows
    ---
   112   names a visitor can read today

**The disagreements are not cosmetic.**

    page: Aegis Gladius - Noise Launcher   game: Aegis Avenger - Noise Launcher
    page: VariPuck S6 Gimbal Mount         game: VariPuck S7 Gimbal Mount
    page: XIAN Scout CML Chaff             game: Aopoa Khartu-al - Noise Launcher
    page: MSD-481 Missile Rack             game: SNT-481 Missile Rack

**A Gladius part labelled Avenger. A size 7 mount labelled S6.** Anyone
comparing our page against the game finds a mismatch and stops trusting the
page, and they would be right to.

**The 61 placeholders are paints.** `<= PLACEHOLDER =>` is CIG marking a name
they have not written. **We publish it as a product name.** An empty cell would
be more honest.

**The 6 truncations are an escaping bug in the build.** The game's
`MRX "Torrent"` reaches the page as `MRX \` — everything after the first double
quote is gone.

## 5. THE CONTROL

`checks/_verify_display_names.py`. **RULE16: INDEPENDENT** — its truth is
`labels.json`, which the build never reads, so the page and the check cannot be
wrong in the same direction.

**It refuses four things and tolerates three**, and the tolerances are the part
that matters: it says nothing about the 3,724 items CIG never named, nothing
about shorthand the game itself displays, and nothing where we already match.
`--self-test` proves all seven.

## 6. WHAT I TAKE FROM IT

**Three separate times today I have been confidently wrong about a number or a
direction, and each time the correction came from opening a file rather than
from thinking harder.** The port that was never broken. The em-dash count that
counted repeats. And this: a whole translation layer I was ready to build, when
CIG had already written it and shipped it to us four times since July.

**The reflex to check is worth more than the reasoning.**

— C1
