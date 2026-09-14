# Memo

To:      Owner
From:    Engineering
Subject: Five named process cuts for a yes or no each — and the one place your two rulings today pull against each other
Status:  Closed

**You asked for a short list of specific cuts, each named, with what it removes and
what it risks. Five. Mark each one.**

**Read section 6 first if you only read one part.** Your record ruling and your
cut-process ruling land on the same desks on the same day and they pull in opposite
directions, and I would rather say so now than discover it in a week.

---

## 1. THE NARRATIVE DESK LOG

**What it is:** `CCDesk-logs/<project>/<year>/<month>/<date>/<desk>.md`. Every pass,
each desk appends several hundred words about what it found and what it got wrong.
Today's C1 page is 20,679 bytes across six passes.

**Cut:** stop writing it. A desk records what it found in a finding, and nothing else.

**What it removes:** roughly one long write per pass per desk, and a second copy of
material that is already in the memos and the findings.

**WHAT IT RISKS, AND THIS IS REAL:** three of this week's better findings came out of
writing that page rather than out of the work — the proxy shape, the "nothing quiet
stays invisible" shape, and tonight's near-miss on a false accusation. **The page is
where a desk notices what it keeps doing.** Cutting it saves time and removes the one
artifact whose whole purpose is noticing a pattern across jobs.

**My recommendation: cut it to a cap rather than to zero.** Ten lines a pass, findings
only, no narrative. You lose the reflection; you keep the ledger.

## 2. STATUS-ONLY LETTERS TO YOUR TRAY

**What it is:** a desk writes to `correspondence/open/owner/` to tell you something is
done. Your tray currently holds nine open letters and several are reports, not
decisions — *step A is done*, *containment is staged*, *both replies-path items
handled*.

**Cut:** a desk writes to your tray only when it needs a decision, a permission, or a
ruling from you. Status lives in `docs/CURRENT-STATE.md`, which you read when you want
it and which is one document rather than nine.

**What it removes:** most of the volume in your tray. You would open it and find only
things waiting on you.

**What it risks:** you lose the push. A thing that is finished and wrong stays finished
and wrong until you happen to read the state document. **Mitigated by the state
document being current, which it now is, and which is the thing that actually failed
before.**

## 3. A SECOND DESK REVIEWING A REVERSIBLE CHANGE THAT ALREADY HAS A CONTROL

**What it is:** an audit or architecture pass over an implementation detail that can be
reverted in one command and that a check already covers.

**Cut:** if the change is reversible and a control can fail on it, it ships on the
building desk's judgement. The review happens if the control goes red.

**What it removes:** a whole hop per change, and the routing records that go with it.

**What it risks:** a control that is green for the wrong reason lets something through
that a person would have caught. **This project has that exact failure on record** —
four green controls passed a heap of markers because every one asked whether a marker
was correct and none asked whether the set was plausible.

**Narrow it to make it safe: the control must be one that has been proven able to
fail.** A check nobody has watched go red does not earn the cut.

## 4. ROUTINE COMMIT APPROVAL FOR DOCUMENTS

**What it is:** hard rule 2 — every commit needs your go-ahead. Under your record
ruling, that is every document.

**Cut:** the narrowest standing permission, specified in full at
`claude/SPEC_the-record-is-what-is-committed-2026-09-11.md` §4. Documents only,
explicit file list, one item per commit, **no push**, no delete, no rename, nothing
that is not a document in the same commit — and a pre-commit hook that refuses rather
than a desk that promises.

**What it removes:** you from the loop on a reversible, local, invisible act.

**What it risks:** almost nothing, **provided the hook is proven able to refuse before
the permission is used once.** If the hook cannot be made to refuse, do not grant this.

**There is a separate problem underneath it that the permission does not solve — §4 of
that spec, and it is in question 3 below.**

## 5. THE DESIGN REVIEW OF A SPEC THAT IS ABOUT TO BE BUILT

**What it is:** a spec gets reviewed by a second desk, then built, and building it
finds what the review did not.

**Cut:** a spec that will be built within the week is not reviewed. The build is the
review, and the build produces evidence instead of opinion.

**What it removes:** a hop, and the illusion that the review proved something.

**What it risks:** an expensive build against a wrong spec. **Bound it: this applies
to specs whose build is under a day and reversible.** The brakes, the containment work
and anything touching a boundary keep their review.

---

## WHAT I AM NOT PROPOSING TO CUT

Echo's keep-list — database destruction, spending, publication, deployment, security
boundaries, final independent verification — **and you said you have not ruled on it,
so I have not treated it as ruled.** I would add two of our own to it:

**Rule 16 verification from a different source stays, and it is not a review hop.**
Reading a file rather than trusting a memo about it has caught something real on three
of the last four days.

**Rule 1 stays absolutely.** Nothing is deleted. A cut to process never becomes a cut
to that.

---

## 6. YOUR TWO RULINGS TODAY PULL AGAINST EACH OTHER, AND I WOULD RATHER SAY IT NOW

**You told me to cut process. In the same letter you made the record what is
committed, which ADDS a step to every document this project produces** — write,
commit, mirror, with a provenance header on the mirror and a detector that re-hashes
it.

**That is more process, not less, and it lands on the same desks on the same day.**

**I am not arguing against the record ruling.** It is right, the drift is real, and
four documents chosen at random were genuinely not on disk. **But the honest accounting
is that today's net change is more overhead, not less**, and the five cuts above do not
pay for it — they are smaller than the thing you just added.

**What would actually pay for it:** the commit step and the mirror step being one
scripted act a desk runs, rather than three deliberate ones it performs. **That is
build work, it is not specified, and it goes behind the front page like everything
else.** Until it exists, the record ruling costs a desk real time per document and you
should expect the queue to move slower rather than faster.

**If that trade is not what you intended, the place to change it is the mirror** —
mirroring only the documents that a session without repository access actually needs,
rather than all of them. **I have not proposed that because you have not said the
mirror should shrink, and guessing at scope is how the export design went wrong the
first time.**

---

## QUESTIONS

1. Cut 1 — the narrative desk log: cut to zero, cut to a ten-line findings-only cap,
   or leave it?
2. Cuts 2, 3, 4 and 5 — yes or no on each.
3. Under the record ruling, who runs the git command? **Architecture is barred from
   index-touching git on the mount after the eight-day `.git/index.lock` jam, and
   `device_bash` is down on every Cowork desk since the 2026-09-08 Windows update — so
   C1 can write a document and physically cannot commit it, whatever permission you
   grant.** Does document committing route to Code, or does Architecture get the git
   exception back?
4. Did you intend today's net process change to be an increase? If not, should the
   mirror shrink to only what a repository-less session needs?

---

CLOSED:

**Owner, 2026-09-12. Answered and closed.** All five cuts and your two extra questions are ruled in the same file, items 18 to 24. Your accounting in section 6 was right: the mirror shrinks.
