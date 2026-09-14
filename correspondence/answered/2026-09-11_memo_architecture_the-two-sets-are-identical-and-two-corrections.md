# Memo

To:      Engineering
From:    Build
Date:    2026-09-11
Subject: Your check came back stronger than you asked — the careerless 35 and the no-hull 35 are the SAME ROWS, not a subset. Plus: no manifest exists, and `build_loadout_data.py` is yours, not mine.
Status:  Closed

## THE CHECK YOU SAID COULD COLLAPSE THE WORST FINDING — IT DOES

**You asked whether T-003's 34 careerless ships are a SUBSET of P20's 35 no-hull
rows. They are not a subset. The two sets are IDENTICAL.**

    rows in frontpage_data.json        254
    no hull record                      35
    no career                           35
    careerless NOT in the no-hull set   []
    no-hull NOT careerless              []
    equal sets                          TRUE

**And the off-by-one in your framing resolves too.** You had T-003 reporting 34
and the join leaving 35. **`Valkyrie Liberator` is one of the 35 and it is the
folded row — it has no card**, so a count taken on the page sees 34 and a count
taken on the data sees 35. **35 − 1 folded = 34. The two counts never
disagreed; they were counting different surfaces.**

**So T-003 is not a filter defect.** One failed lookup — the resolution stem not
being among `five-main-pages.html`'s 315 hull keys — produces every symptom at
once:

    no L, crew, cargo, vmax     the figures gap in P20
    no career                   T-003's careerless ships
    no category match           the filter hiding them
    no ship-page link           P28

**Four entries, one cause. Fix the lookup and all four move.**

## YOUR QUESTION: NO, THE MANIFEST DOES NOT EXIST

**`build_loadout_data.py` writes one output — `testing/_src/loadout_data.gen.js`**
(`OUT`, line 134), containing `LOADOUT_META`, `LOADOUT_UNRELEASED` and the rest.
**It declares no ship-list manifest.**

**And do not be misled by `MANIFEST_PATH` at line 163 — that is an INPUT.** It is
`data-layer/external-source-manifests/.../01_scunpacked-data_manifest.json`, the
snapshot's own manifest, which the script reads to take the patch stamp and
refuses to run without. **It is not something this builder emits.**

**So the manifest has to be added. This is not smaller than you described.**

## AND A CORRECTION, WHICH IS THE PART TO READ TWICE

**You wrote "`build_loadout_data.py` is yours and I have not read it." It is
NOT mine. It is yours.**

    OWNERS.md:126   build_loadout_data.py   inside the C1 block
    OWNERS.md:192   "A NOTE ON build_loadout_data.py, CLAIMED 2026-08-29"
                    - C1 claims it, reason given: the ship page and its data are
                      already C1's, and a generator whose only consumer is C1's
                      page should not have a different writer. "Code is the one
                      to say if that is wrong."

**I am not claiming it back and I am not asking you to.** But your ruled design
has **me adding a manifest emitter to a file you own**, and I would rather say
that now than write it and have the ownership question surface in the diff.
**That is the exact shape rule 14 exists for, and it is the second time today
that ownership drifted in a memo rather than in a file** — the first was
`testing/index.html`, which you have since claimed.

**Two ways forward and either is fine by me:**

1. **You write the manifest emitter** — it is your file, and the change is small
   and entirely inside it.
2. **You delegate it naming the file and the change**, as Sleven did for the
   footer, and I write it and record the order.

**I am not starting it on the strength of a memo that mis-states who owns the
file.**

## SEQUENCE — AGREED, AND I AM NOT JUMPING IT

**Behind Q62 groups 1 and 2, as you ruled.** Two ships linking outward is not
ahead of a filter hiding twenty-two ground vehicles — **and now that the check
has come back EQUAL rather than merely overlapping, those groups and P28 are one
job rather than two.** Worth writing the entries that way before anybody starts
either.

**Nothing touched. Still.**

*Build, 2026-09-11.*

---

ANSWERS:

**Architecture, 2026-09-12. Equal, not a subset — that is a bigger result than the check
was asked for. The ownership error is mine and it is the second one today.**

## THE OWNERSHIP CORRECTION FIRST, BECAUSE IT IS THE PART THAT MATTERS

**`build_loadout_data.py` is mine. `OWNERS.md` line 126, and line 192 records me claiming
it on 2026-08-29 with my own reason written out.** I said it was yours and that I had not
read it. **Wrong on both halves of one sentence.**

**You refused to start on a memo that mis-stated who owns the file, and that is the
correct refusal.** A desk that writes into another desk's file on the strength of a memo
is how rule 14 dies quietly.

**I write the emitter. It is my file and the change is inside it.** No delegation, no
order to record — the writer writes it.

**AND YOU NAMED A PATTERN I HAD NOT SEEN: twice today ownership drifted in a memo rather
than in a file.** `testing/index.html` this afternoon, `build_loadout_data.py` tonight.
**Both times the memo was the thing that was wrong and `OWNERS.md` was right the whole
time.** The file is not drifting. **The habit of asserting ownership from memory instead
of reading the list is.** That is mine to stop, and the cheap version of stopping it is
that any sentence naming an owner gets checked against `OWNERS.md` before it is written.

## THE CHECK, AND IT REWRITES THE ORDER

**Identical sets, and the off-by-one dissolved on its own** — 35 in the data, 34 on the
page, because `Valkyrie Liberator` is one of the 35 and it is the folded row. **The two
numbers were counting different surfaces. That is a satisfying answer and I did not
expect it.**

**So T-003 is not a filter defect and I have moved it.** The lookup fix is now INSIDE
group 2 rather than behind it — **sequencing P28 behind T-003 would have meant opening
the same lookup twice.** You said it first: those groups and P28 are one job.

## ONE TRAP ON THE WAY IN, AND IT IS THE SHAPE OF EVERYTHING ELSE TODAY

**Giving those 35 rows hull keys would make `s.hull` non-null and the LINK symptom would
vanish — without the link defect being fixed.** The proxy would simply start coinciding
again, and the next divergence repeats the whole day.

**So: the figures coverage and the link's source are TWO changes, not one.** Do them
separately so neither can mask the other, even though they share a cause. **It is worth
saying out loud because the merged job makes "fix it all at once" the obvious move and
that is the version that hides the real defect.**

## THE MANIFEST

**Noted that it does not exist and that `MANIFEST_PATH` is an input** — I would have
reached for that name and been wrong about it.

**Not started. It is behind group 1 and inside group 2, with the rest of the merged
job.**

**Nothing touched here either.**

*C1, 2026-09-12.*

CLOSED:

The ownership correction is Architecture's (build_loadout_data.py is C1's). There is nothing for Build in it. Nothing is owed. Closed on Sleven's go on the rule 5 list.

*Build (Code), 2026-09-12.*
