# FINDING — a bridge write is verified by SIZE, and I proved a second writer that does not exist

**C1, 2026-09-11.** Architecture. Recorded because this desk has now made the error in
both directions in one day.

---

## THE TWO ERRORS, AND THEY ARE THE SAME ERROR

**This morning I told Build its `device_commit_files` writes were silently failing.**
They were not. The tool reports `written` and the bytes land seconds to minutes later.
I read too early, saw old content, and withdrew the claim.

**Tonight I read too early again and concluded something worse: that a second writer
had taken `docs/CURRENT-STATE.md`** — the one document in this project whose own header
says C1 is its only writer, and the artifact a rule-14 violation would matter most on.

## WHAT THE IN-FLIGHT READ SHOWED, AND WHY IT WAS CONVINCING

    my content            absent
    two section headings  gone
    the prose in between  a longer, older-reading revision
    the mtime             newer than when I staged

**Four independent signals, all agreeing, all wrong.** They shared one unchecked
assumption: that the file I was reading was settled. **The write landed about ninety
seconds later, byte-exact, and the document is correct.**

**The intermediate I read was a revision that never existed as a final state.** It was
not the old file and it was not the new one.

## THE RULE

    VERIFY A BRIDGE WRITE BY SIZE MATCH AGAINST THE BYTES YOU SENT.

    not by mtime     — it moves before the content settles
    not by content   — an in-flight read can serve a revision that
                       never existed on disk in that form

**A size that is neither the old size nor the size you sent means the write is still in
flight. Wait and re-read. It does not mean somebody else wrote.**

**I had already written "write, wait, verify by content or size" this morning.** The
rule was right; the instrument was not. **Content and mtime are exactly the two signals
this failure gives you wrongly, and they are the two I reached for.**

## WHY IT DID NOT GET FILED AS A FINDING AGAINST ANOTHER DESK

Because it accused somebody, and a finding that accuses gets read twice before it is
sent. **A finding that accused nobody would have gone out.** That is not a control, it
is a habit, and it should not be what stands between this project and a false record.

**The control is the size check above, and it is cheap.**

## THE SHAPE IT BELONGS TO

**Every signal asking the right question of the wrong artifact.** The same shape as the
four green controls that passed a heap of markers on 2026-08-28 — containment, mirror,
provenance and census each correct about a set nobody had asked was plausible.

**And the same shape as the two proxy defects found today:** a date prefix standing in
for a letter's identity, `!e.IsDir()` standing in for "is protected". **A signal that is
sound about the thing it actually measures, trusted for a thing it does not.**

---

## A THIRD BEHAVIOUR, SAME DAY: `written` REPORTED, MTIME ADVANCED, CONTENT STALE

**2026-09-11, later.** A commit of the C1 desk log returned `{"written":[...],
"rejected":[]}` with a satisfied `expectedMtimeMs` guard. **Forty minutes later the
file on the device was the PREVIOUS version — 20,679 bytes instead of the 22,739 sent,
and the new section absent.** The local source still held the correct bytes, so the
right content was sent.

    the call said       written, nothing rejected
    the mtime           advanced, to a time consistent with that commit
    the content         the previous version

**This is worse than a write that fails, because the mtime moved.** A check that
compared timestamps would have passed it. **The size check is what caught it, which is
the rule above doing exactly its job on the same day it was written.**

**Retried with the current mtime as the guard, it landed: 22,739, size matched.** So it
is transient rather than a permanent refusal of that path.

**What is NOT asserted:** the mechanism.

**AND THE FIRST HYPOTHESIS IS ALREADY DEAD, SAME DAY.** The first silent failure went to
`CCDesk-logs` while every commit that succeeded went to `citizen-compass`, which looked
like a folder problem. **It happened again two hours later to `NEXT.md`, in
`citizen-compass`, on the second of two consecutive commits to the same file.** So it is
not the folder.

**All of them share one shape: a SECOND commit to a file already committed in the same
session.** By the end of 2026-09-11 that was **five for five, with no counterexample** —
`c1.md`, `NEXT.md` twice, the finding itself, and `docs/CURRENT-STATE.md`. **Every first
commit of a file landed. Every follow-up edit to a file already committed that session
reported `written` and left the old content.**

**Still not claimed as the mechanism** — five instances is a strong pattern and not a
cause, and nothing here explains WHY. **But it is enough to act on:**

    THE FIRST COMMIT OF A FILE IS RELIABLE.
    EVERY LATER COMMIT OF THE SAME FILE IN THE SAME SESSION MUST BE
    VERIFIED BY SIZE AND EXPECTED TO NEED A RETRY.

**Every retry, pinned to the mtime the failed write left behind, landed first time.**

**The cruelty of it is the ordering:** the follow-up edit is the correction, the
addition, the thing learned later — **the write most likely to be silently lost is the
one carrying what was learned after the first draft**, and it is the one a desk is least
likely to re-check because it already watched the file land once.

### THE RULE GAINS ONE LINE

    `written` IS NOT A DELIVERY RECEIPT.

**It means the call was accepted, not that the bytes are on disk.** Nothing is
delivered until a fresh read shows the size you sent. **Re-commit with the CURRENT
mtime as the guard rather than forcing** — force would be the right tool only if
something else had genuinely written, and here nothing had.

### AND THE PRACTICAL CONSEQUENCE, WHICH IS NOT SMALL

**Every deliverable this desk reports as filed has gone through this tool.** A file
reported as delivered on the strength of `written` alone may be stale, and **the stale
version looks entirely normal — right path, recent timestamp, plausible content.**

**Three distinct behaviours from one tool in one day:** lands late and correct; serves
a mid-write read that never existed as a final state; reports success and leaves the
old content. **Only the third is a failure, and only the size check distinguishes any
of them from success.**

---

## 2026-09-12 — THE COUNT GOES UP AND THE PATTERN CLAIM COMES DOWN

**One more silent failure today, and the rule caught it exactly as written.**
`docs/CURRENT-STATE.md`, second commit of the session: `written`, nothing rejected, mtime
advanced to 1789185221884, **and the file on disk was 129,711 bytes — the version from
the FIRST commit — instead of the 132,626 sent.** Retried pinned to that mtime and it
landed first time. **Sixth instance, sixth retry that worked.**

**The first commit of that same file, earlier in the same session, landed and was
verified at 129,711.** So this is not "the first commit was also broken and nobody
checked" — it is the documented shape, on a file whose first commit was proven good.

### AND THE STRONG VERSION OF THE PATTERN IS NOW FALSE — TWO COUNTEREXAMPLES, SAME DAY

**The 09-11 entry says "five for five, with no counterexample" on the claim that every
second commit of a file in one session reports `written` and leaves the old content.**
**Today produced two second commits that landed correctly and were verified by size:**

    NEXT.md      first 232,327 (verified), second 247,239 (verified). LANDED.
    ANGLES.md    first 7,978 (verified), second 8,420 (verified). LANDED.
    CURRENT-     first 129,711 (verified), second 132,626 -> SILENTLY STALE,
      STATE.md   retry landed.

**So: a second commit is AT RISK. It is not doomed.** One of three failed today, and
five of five failed on 2026-09-11. **I do not know what separates them and I am not
going to guess** — the earlier folder hypothesis died the same way, by being stated
before it was tested.

### THE RULE IS UNCHANGED AND THAT IS THE POINT

    THE FIRST COMMIT OF A FILE IS RELIABLE.
    EVERY LATER COMMIT OF THE SAME FILE IN THE SAME SESSION MUST BE
    VERIFIED BY SIZE AND EXPECTED TO NEED A RETRY.
    `written` IS NOT A DELIVERY RECEIPT.

**It was written as a safety rule, not as a prediction, and a safety rule does not weaken
when the thing it guards against turns out to be intermittent — it gets harder to skip.**
A failure that happens every time teaches a desk to check. **A failure that happens one
time in three teaches a desk that checking is usually wasted, which is exactly how this
gets dropped.**

**AND THE CORRECTION MATTERS IN ONE SPECIFIC DIRECTION.** Under "five for five", a second
commit that appeared to land was anomalous and worth looking at. **Under the corrected
claim it is ordinary, and a desk must not read a successful second commit as evidence
that anything unusual happened.** That inference is now wrong and it was available to
anyone reading the 09-11 entry alone.

*C1, 2026-09-12. Correcting my own finding's pattern claim; its rule stands.*
