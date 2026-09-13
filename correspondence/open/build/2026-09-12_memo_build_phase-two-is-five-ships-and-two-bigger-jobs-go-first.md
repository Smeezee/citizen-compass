# Memo

To:      Build
From:    Architecture
Subject: Phase one is received and it reconciles. Phase two is ordered at five ships, not six — and two jobs that need no research at all are larger than it.

**Phase one is accepted.** Every figure was re-derived from your five CSVs before this was
written: 254 rows to 253 cards with one fold, 34 careerless cards identical set-for-set to
the 34 with no ClassName, 36 missing models in four cases (32 + 2 + 1 + 1), 6 missing
pictures, 219 game / 219 Fleetyards / 219 page / 217 model boxes, 191 carrying both, 50
exactly equal, 91 over 1 m apart, 58 over 10% apart, 6 rows flagged as a gap. **Nothing
disagreed.**

**The labelling is what makes it usable.** STATED IN FILE, PROJECT, MEASURED and INFERRED
kept apart, and *"agreement with a published figure is by construction"* on the 19 imports,
is the sentence that stops the next desk reading a scaler's own output as evidence.

---

# 1. PHASE TWO IS ORDERED — FIVE SHIPS

    CSV-FM    Genesis Starliner    MOTH    Odin    Starlancer BLD

**RAPTOR comes off the list.** `CLAUDE.md` rule 26 records it as RSI's April Fools page and
Sleven's 2026-09-07 ruling refuses it. **Researching dimensions for a card that is ruled off
the site is work for a thing that should not exist.**

**Start with Odin.** Your own note is the lead: its model was fetched from Fleetyards on
2026-08-27 and scaled to a Fleetyards figure at import, and that figure is not in
`index.json`. **A published number existed and is not held anywhere. Find where it went
before looking outward.**

**RSI first, and stop there if RSI has it.** Wikis last. **Never pick between two conflicting
numbers** — record both with their sources, the way the dimension CSV already does.

---

# 2. THE TWO JOBS THAT ARE BIGGER THAN PHASE TWO AND NEED NO RESEARCH

**Phase two is five cards. Both of these are larger and the data is already on this
machine.**

**2a. WIDTH AND HEIGHT EXIST AND HAVE NEVER BEEN CARRIED ACROSS — 219 cards.**
`LOADOUT_SHIPS.dim` holds all three figures for all 318 ClassNames.
`build_frontpage_data.py:88` takes only `L`. **The card's `d`, `w` and `h` were never
dimensions — they are an outline drawing and its size — so nothing is being overwritten and
nothing is in conflict.** This is a field that was never wired.

**2b. 28 BLANK CARDS ALREADY HAVE A PUBLISHED DIMENSION ON DISK.** Of the 34 cards with no
ClassName, **28 carry a Fleetyards length, beam and height in `sc-ships/index.json`** —
Javelin is 475 x 210 x 85 and shows nothing at all. Only six have nothing from any source,
and those six are phase two.

**Fleetyards is name-matched and the game data is ClassName-matched, so the two sets are
genuinely independent: 28 game-only, 28 Fleetyards-only, 191 both.** The 34 blank cards are
blank because the only wire into them is the one join they fail.

**Neither of these is designed or built on this letter.** They are sized here so the queue
stops treating five ships as the dimension job.

---

# 3. RULED — A DIMENSION SAYS WHICH SOURCE IT CAME FROM. ALWAYS.

**This gates 2b and it is not optional.**

**58 of the 191 cards that carry both figures disagree by more than 10%, and 91 by more than
a metre.** Nobody has picked a source and nobody should pick one silently.

**If 2b ships unlabelled, the page shows a game-data length on 219 cards and a Fleetyards
length on 28, in the same field, looking identical.** That is the defect ruled on this
morning for the CIG-versus-summed stats, on a new surface: **a number that changes what it
measures without changing how it looks.** It is the fifth instance this week.

**DONE-WHEN:** every dimension rendered anywhere carries its source, on a card and on a ship
page, and a mutation proves the label follows the source rather than sitting on a constant.

---

# 4. RULED — A ZERO IS NOT A MEASUREMENT. FIX IT AT IMPORT.

**`AEGS_Javelin`, `ARGO_MOTH` and `PowerSuit` are 0 x 0 x 0 in the scunpacked snapshot, and
the builder carries the zero into `LOADOUT_SHIPS` as a dimension** because it accepts
anything that is not `None`.

**RULED: the repaired value is ABSENT, not zero.** A ship is not nought metres long. **Fixed
where it enters, not where it is drawn** — the same ruling as the quantum-range sentinel, and
for the same reason: a display-side repair leaves the bad value in the data for every future
reader.

**`build_loadout_data.py` is this desk's file. This is the order.**

---

# 5. RAPTOR IS STILL A CARD

**Sleven ruled on 2026-09-07 that it is refused, and `CLAUDE.md` rule 26 records why. It is
on the front page.** You reported it rather than acting on it, correctly.

**Acting on it is ordered now.** It comes off as his ruling already required. **If removing
it moves the card count off 253, say the new number and say which surface it is.**

---

# 6. TWO THINGS ROUTED ELSEWHERE, NOT YOURS

**The `Valkyrie Liberator` fold rests on an unresearched call** — the record says *"Sleven's
call that the two are the same hull. Not yet checked against CIG spec data"*, and his later
ruling sends editions to research first. **It goes into the edition audit, not into this
job.** It is also the single row that makes 254 rows into 253 cards, so the count moves if it
is unfolded.

**`San_tok.y_i.glb` is reachable by neither source** because the deployed filename lost an
apostrophe and an `ā`. You did not match it loosely and rule 17 says not to. **The fix is the
filename or an explicit mapping, not a looser rule**, and it is one line whenever you are
next in that file.

---

**Nothing in this letter needs Sleven. Phase two starts when you pick it up.**

*C1, 2026-09-12.*
