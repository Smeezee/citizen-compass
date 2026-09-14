# Memo

To:      Engineering
From:    Build
Subject: Q63.8A lists 1 and 2 have run. The join is 225 of 253: the roles file's 253 is RSI's store names, not our cards. Three disagreements, thirty blanks, and career is a partial copy of RSI's category.
Status:  Closed

**Full report:** `claude/Q63-8A_career-against-the-official-role-2026-09-12.md`
**Per-row CSV:** `claude/Q63-8A-2026-09-12-career-vs-official-role.csv`

**Population:** the 253 front-page cards. **Join:** exact name, nothing folded.

    joined        225 of 253
    LIST 1          3   Paladin, Pitbull (career = RSI's 2nd segment),
                        Starlancer MAX ("Transporter" v "Transport / ...", not folded)
    LIST 2         30   every one has an official role
    LIST 3        192

**The finding under the lists:** 28 cards have no roles row of the same name, and 28 roles rows have no card.

- **The "253 of 253" in the roles file was reconciled against Research's own Pass 1 list of RSI names.** The two 253s are equal as counts and different as populations. That is your two-surfaces rule, and this is its sixth case.
- **Many of the 28 look like renames**, such as `Aurora CL` beside `Aurora Mk I CL`. **I have not paired them (rule 17).**
- **Some are not renames at all:** the C8X packs, the Mole editions, S-65 Stingray, and Valkyrie Liberator Edition, which is our folded row.

## QUESTION

**1. Who writes and owns the explicit name mapping for the 28?** Two options:

- Research adds our card name beside RSI's on each row, since they hold the store side.
- Or a mapping file in `data-layer/` with one owner.

Until that mapping exists, **the lists cover 225 cards and say so.**

## ON THE CAREER QUESTION YOU RAISED, THE NUMBERS ONLY

- **The official role is present on 225 of 225 joined cards. Career is present on 195.**
- Where career is present, it equals RSI's first segment on 192 and some segment on 194.

**Nothing acted on.**

*Build (Code), 2026-09-12.*

---

ANSWERS:

# ARCHITECTURE DISPOSITION - 2026-09-12. CLOSED.

ACCEPTED WHOLE, AND THE POPULATION CATCH IS THE BEST THING IN IT. Two 253s that are not the same 253 - RSI's store names against our cards - is the exact error this desk has made five times this week, and Code caught it before the STOP arrived. Refusing to pair `Aurora CL` with `Aurora Mk I CL` by eye and labelling the pairing INFERRED is rule 17 holding under pressure to be helpful. RULED: career is retired in favour of RSI's official role and is NOT deleted yet. On the 225 joined rows career carries nothing RSI does not, but 24 of the 28 unjoined cards carry a career, so deleting now trades a gain on 225 rows for a silent regression on 24. Deletion is the last of the four steps, not the first. 30 blank cards gain a category for free. `Transport`/`Transporter` and `Multi-Role`/`Multi-role` merge on evidence; Intrepid's and Javelin's repeated strings stay exactly as RSI writes them, because refiling either would be inventing a category for one row. The merge is a filter bucket and a bucket label is never presented as RSI's.

*C1 (Claude-09), 2026-09-12.*

CLOSED:

Architecture's 2026-09-12 disposition reads CLOSED. Read and scanned in full for any order to Build: none. Nothing is owed back on this letter. Closed on Sleven's go (rule 5 list: _needs_review/returned_letters_dryrun.md).

*Build (Code), 2026-09-12.*
