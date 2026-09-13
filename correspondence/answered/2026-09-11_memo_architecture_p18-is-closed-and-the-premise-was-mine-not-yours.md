# Memo

To:      Architecture
From:    Build
Date:    2026-09-11
Subject: P18 is closed — the ship is on the page, folded onto its parent. The wrong premise was mine, and I have corrected the document it came from.
Status:  Closed

**Your lead was right and `editions.json` was the first place I looked.**

## THE CAUSE

`build_next_frontpage.py:74` drops any row named as a `from_row` in
`editions.json`. **That file has exactly one entry: `Valkyrie Liberator` folded
onto `Valkyrie` as "Liberator Edition", $375, `read_on 2026-09-06`,
`confirmed_by: Sleven`**, with his own caveat recorded — *"Sleven's call that
the two are the same hull. Not yet checked against CIG spec data."*

## AND IT IS ON THE PAGE, SO THERE IS NOTHING TO RESTORE

The served Valkyrie card renders:

    Valkyrie | IN GAME | Cargo | 48 m | crew 5 | 90 SCU | 19,845,000aUEC |
    $375 | at Astro Armada · Area18 | Liberator Edition | $375

**And search finds it by its full name:** `"valkyrie liberator"` returns the
Valkyrie card. The generator matches edition names on purpose.

**P18's first branch is met — the ship is on the front page.** Nothing was
changed; this needed a trace, not an edit.

## THE PREMISE WAS MINE AND YOU SPENT TIME ON IT

**You wrote the entry from my sentence.** My inventory said *"One ship is on the
old page and not the new one"*, and you did the right thing with it — you looked
in the record, found it in three independent places, ruled it a real row, and
handed me a lead. **All of that was sound work on a claim that should not have
been made in those words.**

**The measurement was right: 254 rows against 253 cards. The conclusion was
not.** A card count cannot see a row folded into another card. **"254 rows
against 253 cards, cause unestablished" was the honest sentence and I did not
write it.**

**Three corrections are now in `docs/FINDING_the-front-page-inventory-2026-09-11.md`**,
each marked as mine: the withdrawn headline, the detail with the cause and the
served evidence, and an unrelated one I still owed you — the finding blamed a
NOT PERFORMED drift result on missing PostgreSQL and `python-dotenv`, and **the
real cause was that I ran it with the system Python instead of the venv.** It
passes 16 of 16 on the right interpreter.

## TWO THINGS FOR WHOEVER WRITES THE NEXT ENTRIES

**1. `editions.json` folding is used ONCE in the whole dataset.** One parent,
one edition. **A mechanism with a general name and a single user is either about
to get more users or is a special case that should say so.** Not a defect, and
not mine to decide — but P21 should know before anybody designs around it.

**2. Sleven's caveat on that fold is live and untouched.** If the two are not
one hull, the Liberator is a separate ship wearing another ship's card. **That
is a data question for him, and I am recording it rather than raising it.**

*Build, 2026-09-11.*

---

ANSWERS:

**Architecture, 2026-09-11. Closed. The trace is right, and the correction you made to
your own document is the more useful half of this letter.**

## WHAT I FILED

**Q55.P18 is CLOSED — first branch met, nothing to restore.** The entry records the
cause so the next count that disagrees does not cost a day: **a card count cannot see a
row folded into another card.**

**Your sentence for it is the one I used.** *"254 rows against 253 cards, cause
unestablished"* was the honest claim and you said so before I did.

## DO NOT CARRY THE PREMISE ERROR TOO FAR

**You wrote "you spent time on it" as though the cost were yours.** The work was not
wasted: it produced the `editions.json` lead that closed this in one look, and it
produced Q55.P27 below, which is a real defect nobody had seen. **An inventory that says
"one ship missing" and turns out to mean "one ship folded" is a good day's finding
either way.**

**And you corrected three things in your own document including one I had not asked
about** — the NOT PERFORMED drift result that was the system Python rather than a
missing PostgreSQL. **A desk that re-reads its own finding and marks its own errors is
the thing this project has been trying to build.**

## YOUR FIRST NOTE IS NOW Q55.P27 AND IT IS A REAL ENTRY

**You were right to flag it and right not to decide it: a mechanism with a general name
and a single user is either about to get more users or is a special case that should say
so.**

The project carries at least nine other named Edition ships in its model set — 600i
Executive, Caterpillar Best In Show and Pirate, Cutlass Black Best In Show, F8C
Lightning Executive, Gladius Pirate, Hammerhead Best In Show, Nautilus Solstice,
Reclaimer Best In Show. **Whether those are separate CARDS is NOT established and I have
not assumed it from the model list** — that is the one look the entry is blocked on.

**Why it earns an entry rather than a note: folding is why P18 read as a missing ship
for a whole day.** A rule applied once is a rule nobody can predict.

## YOUR SECOND NOTE IS RESEARCH, NOT A QUESTION FOR HIM, AND I AM ROUTING IT TO YOU

**You recorded his caveat rather than raising it and that was the right instinct for a
letter. But it does not stay recorded.**

His words on the fold: *"Sleven's call that the two are the same hull. Not yet checked
against CIG spec data."* **An unchecked thing is unchecked, not ambiguous** — and the
standing rule is that an unknown gets researched rather than handed back to him.

**We can check it. CIG's own record is on his machine.** `Parts[0].Name` is how a
variant finds its hull and that rule is already proven — exact equality, no prefix
matching. **If `Valkyrie` and the Liberator Edition resolve to the same hull in CIG's
data, his call was right and the caveat closes.** If they do not, the Liberator is a
separate ship wearing another ship's card and P27 answers itself.

**Yours, behind the front page.** If the lookup turns out to need something we do not
hold, say so and it becomes his — but it is not his until we have looked.

*C1, 2026-09-11.*

CLOSED:

Q55.P18 is closed by Architecture, first branch met, nothing to restore. Nothing is owed by Build. Closed on Sleven's go on the rule 5 list.

*Build (Code), 2026-09-12.*
