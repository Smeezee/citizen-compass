# FINDING — the 107 wrong names are fixed at the source. Auditing my own work first found that four of the numbers I had reported were my measurement, not the data.

    from    C1 (Cowork), 2026-08-30
    asked   by Sleven: "fix everything and get everything re straightened out.
            And I expect you to audit yourself to make sure you are correct."
    method  parse, never regex, and re-derive every number before acting on it

---

## 1. WHAT I HAD REPORTED, AND WHAT WAS ACTUALLY TRUE

I filed **112 wrong names** in four groups. Auditing before changing anything:

    reported            actual   what happened
    61 placeholders        61    correct - and they are all LIVERIES
     6 truncated            0    MY REGEX. `"n":"([^"]*)"` stops at the
                                 escaped quote inside `MRX \\"Torrent\\"`.
                                 The payload holds the name correctly.
    26 raw class names     27    close, and split 8 parts / 19 paints
    19 disagreements       19    correct
    --                    ---
    112                   107    unique items, after overlap

**And one group I had never looked at:** 45 armour records whose name differs
from the game's, which turns out to be deliberate and is left alone (§5).

## 2. THE ROOT CAUSE, WHICH WAS ONE LINE

`build_loadout_data.py` resolved a name as:

    st.get("Name") or it.get("name") or it.get("className")

**Three sources, none of them the one the game reads.** `labels.json` — CIG's
localisation table, in the same snapshot, 9,559 `item_Name*` entries — was
never opened. So a class identifier reached the page whenever the entity record
was blank, and CIG's placeholder marker reached it whenever CIG had not written
a name yet.

**The fix is a fourth source, first in line.** The join is `item_name` plus the
className, case-folded, exact. **Case-folding was checked rather than assumed:
of 9,559 keys, 0 collide when folded and 0 collide with conflicting values.**
No prefix trimming, no nearest match. **No fuzzy matching, here as everywhere.**

## 3. AND IT UNCOVERED A SECOND DEFECT THAT WAS WORSE

An older branch fired whenever the entity record said `<= PLACEHOLDER =>` and
**overwrote the name after it had been resolved** — throwing away four names
CIG's file had just supplied, for the Sabre Raven's and the Khartu-al's
countermeasure launchers.

It also set `nn = 1` on **1,450 parts**, while the page composed:

    const fam=[p.m, p.nn].filter(Boolean).join(" · ");

**A number joined into a text line. Click any of those 1,450 parts and the
family line read "Unknown Manufacturer · 1".** Nobody had reported it because
it only appears once a panel is open, which is why reading the rendered page
without clicking anything did not find it.

`un` replaces it as a flag, and the WORDS live in the page —
*"not named in the game files"* — which is the right side of that line: the
generator ships facts, the page ships wording.

## 4. THE RESULT, AUDITED FIVE WAYS

    107 names changed - 3,283 parts, 915 paints, 179 armour: none added, none lost
      0 placeholders remain          0 raw class names remain
      0 stray `nn` fields remain     0 names got worse
      0 parts or paints where CIG names it and we still differ

**"Did anything get worse" is the audit that mattered** and it is the one I
would have skipped a week ago. A name that was correct and became derived would
be a regression dressed as a fix, and the count of improvements would have
hidden it.

    Aegis Gladius - Noise Launcher   ->  Aegis Avenger - Noise Launcher
    XIAN Scout CML Chaff             ->  Aopoa Khartu-al - Noise Launcher
    VariPuck S6 Gimbal Mount         ->  VariPuck S7 Gimbal Mount
    <= PLACEHOLDER =>                ->  125a          (flagged as our wording)

## 5. WHAT I DID NOT CHANGE, AND WHY IT IS SLEVEN'S CALL

**45 armour records read "Avenger Stalker ship armour" where the game says
"Avenger Stalker Ship Armor".** The generator derives armour names from the
ship on purpose — 164 of 179 — and the difference is British spelling plus our
phrasing.

**Sleven's rule says match the game. The site's own copy is British throughout.**
Changing these alone would leave the page mixing *armour* and *Armor* in the
same sentence. **Flagged, not decided.**

## 6. TWO CONTROLS WENT RED AND BOTH WERE RIGHT

`_verify_ship_page` counted fixed rows and the countermeasure summary folds two
into one. `_verify_loadout_fitment` allows a livery exactly four keys and `un`
is a fifth. **Neither is a false alarm; both are assertions whose premise I
changed.** Queued as Q37 and Q39 with the exact edit, because they are Code's
files and I am not touching those again.

## 7. THE PATTERN I HAVE TO NAME

**Four wrong numbers in two days, and every one was a measurement that quietly
discarded part of the thing it measured** — the port id split at the first dot,
the em-dashes counted per render instead of per sentence, the off-hull test
reading one camera angle, the names read with a regex that stops at an escaped
quote.

**None of them was a wrong conclusion from good data. All four were good
conclusions from data I had damaged on the way in.** The fix is not more care
in reasoning. It is parsing instead of pattern-matching, and re-deriving a
number by a second route before acting on it.

— C1
