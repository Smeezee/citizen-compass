# Memo

To:      Architecture
From:    Owner
Date:    2026-09-10
Subject: The date on a filename is not mine to type — a verified correction to the record, a standing rule, and one question that changes the answer to all the others

Status:  Closed

**This authorises analysis and correction of the record only. It does not authorise
code changes, step B, or any other build work.**

---

## 1. WHAT HAPPENED, FROM THE FILESYSTEM AND NOT FROM ANYBODY'S ACCOUNT

**The answer routing worked. The supersede missed. Those are two different things and
only the second one is broken.**

Two files, twenty-one minutes apart, one day apart in their names:

    mtime 1789085040720   named  2026-09-11_...      written FIRST
    mtime 1789086286610   named  20260910_...        written SECOND

**The supersede compares basenames. Different names, no match, nothing superseded.**

**The cause is a clock, not a bug.** The Adjutant desk runs on UTC. This machine runs
America/Chicago. **After 19:00 my time those are different days**, so every filename
that desk typed after 19:00 was stamped a day ahead.

**This is not new and the record proves it.** In `correspondence/answered/`:

    2026-08-30_2026-08-31_owners-md-is-yours-and-says-so-twice.md

**Two dates in one filename**, and two siblings alongside it with the same signature.
The watcher stamped the real date onto a name that already carried tomorrow's. **The
same defect, months old, filed and never diagnosed.**

---

## 2. THE CORRECTION I OWE YOU — RULE 14 WAS CITED WRONG AND I ACCEPTED IT WRONG

**Rule 14 is one WRITER per artefact. It is not one reader.**

Build refused a second reader of `protected_folders.txt` on rule 14, and I accepted
that refusal on Q7. **The refusal may still be right, but the reason given was not
rule 14 and my acceptance of it stands corrected.** All three incidents this
repository has paid for under rule 14 were concurrent *writers*.

**Build half-conceded this itself** in §3 of the step B request, proposing a checker
that reads both sources and calling it "rule 16 working as intended, drawing its truth
from a different place than the thing it checks." **That is a second reader, correctly
described.**

**Nothing about step B changes on this letter.** The recommendation in §3 of that
request still stands or falls on its own merits and I will answer it there. **This
corrects the reasoning in the record, not the decision.**

---

## 3. THE STANDING RULE — EFFECTIVE NOW, NOT A RECOMMENDATION

**No desk types a date into a filename again. Ever.**

    A NEW ORIGINAL LETTER carries NO manually added date. The watcher stamps it.
    A REPLY preserves the filename it received, EXACTLY, character for character.

**Why it has to be the watcher and nobody else:** the watcher reads the clock of the
machine the files actually live on, at the moment the file is actually filed. **Every
other source of a date is a guess made somewhere else at some other time.**

**And the sharp edge in the current code, which is why "put the right date in" is not
an acceptable version of this rule.** From `memo.go`:

    if !reLeadingDate.MatchString(base) {
        base = time.Now().Format("2006-01-02") + "_" + base
    }

**The watcher only fills a GAP. It does not correct a wrong date.** A filename that
arrives already stamped keeps whatever it was stamped with, right or wrong, forever.
**So the rule cannot be "stamp it correctly" — it has to be "do not stamp it at all."**

**This letter is the first one filed under that rule.** Its filename carries no date.

---

## 4. A FUTURE REQUIREMENT, NOT A PROCEDURE — AND IT IS NOT AUTHORISED TODAY

**A renamed answer should be treated as a protocol error and reported.**

Today a reply that comes back under a different name is not an error to the system —
it is simply a file that matches nothing, and the supersede quietly does nothing.
**Silent, exactly like the fifty-five seconds Build found where routing failed and the
watcher logged nothing.** Same shape: the failure is real, recovery is not attempted,
nobody is told.

**That is a code change to `memo.go` and this letter does not authorise it.** Specify
it as a requirement. Do not build it. **It goes into the queue behind containment and
the brakes, and it does not jump them.**

---

## 5. THE QUESTION THAT CHANGES THE ANSWER TO EVERY OTHER QUESTION

**`memo.go` WAS REWRITTEN as part of the answer-routing build.**

    before   11,336 bytes   mtime 1788986402290
    now      15,276 bytes   mtime 1789070845607

**`clearOpenCopy` gained a `skip` parameter, and the supersede gate moved** from "did
it go to `answered/`" to "is the status answered, closed or done."

**So any statement anybody makes about how the supersede behaves must be checked
against the 15,276-byte file.** I had verified the date logic against the old one and
said so as though it were current. **It happens to be unchanged — I have re-read it in
the new source and it is the code quoted in §3 above — but I did not know that when I
said it, and that is the part worth writing down.**

**Put this at the top of anything you route to Build about the supersede.** An answer
drawn from superseded source is a confident wrong answer, which is the one kind this
project cannot afford.

---

## 6. WHAT I WANT BACK

**Short. Plain language. Not a menu.**

    1  confirm the rule in §3 is recorded where a desk will actually hit it -
       and say WHERE, because a rule with no reader is the defect we just found
       twice in one week

    2  whether `memoTrays` being a typed map now collides with the standing
       ruling that the desk list is DERIVED from the tray folders on disk -
       I asked this in my last letter and it is still open

    3  the §4 requirement written down as a requirement, in the queue, behind
       containment and the brakes

**Nothing here authorises database work, deployment, unrestricted execution, or any
access to the Looking Project.**

---

ANSWERS:

**Architecture, 2026-09-11.**

**This reply is the first test of your own rule.** It carries the filename it
received, character for character. If the supersede fires, the open copy leaves my
tray and your rule is proved on the same letter that made it.

**I re-read the 15,276-byte `memo.go` before writing a word of this**, per your §5.
Build's rewrite is exactly what was specified: `From:` validated only on an answered
memo, self-answer filed to the archive, `skip` on `clearOpenCopy`, and the gate moved
to "is it answered." **And your §3 quote is current — the date logic is unchanged.**

---

## 1. WHERE THE RULE GOES — AND A RULE A DESK HAS TO REMEMBER IS A RULE WITH ONE READER

**`correspondence/README.md`. That is the procedure for correspondence and this is a
correspondence rule.** The boot prompts get a pointer, not a copy — **copying it into
three places is the defect that put the desk list in three places.**

**BUT THAT IS NOT ENOUGH AND YOU ALREADY KNOW WHY.** You found the one-reader defect
twice this week. A rule that lives only in a document is obeyed by whoever read the
document.

**SO IT GETS A CHECK, AND THE FIXTURES ALREADY EXIST IN YOUR ARCHIVE.**
`_verify_correspondence.py` asserts no filed memo carries two dates. **Both shapes are
real and both are on disk right now:**

    2026-08-30_2026-08-31_owners-md-is-yours-and-says-so-twice.md
    2026-09-08_20260908_memo_audit-to-design_ten-pairs-for-angles-md.md

**The second one matters more than it looks.** `reLeadingDate` only recognises the
dashed form, so a desk that types `20260911_` gets a second date stapled on and the
regex never sees it coming. **A check that only looked for the dashed-dashed shape
would miss half the defect.**

**And it means the check can be proved against real data today** rather than a planted
one — which is the standard this project holds.

## AND A CORRECTION OF MY OWN, WHICH IS THE USEFUL PART

**I have been breaking your §3 rule all day, in the opposite direction.**

**Every answer I have filed today stripped the watcher's date prefix and went back in
undated**, relying on the watcher to re-stamp it. It worked every time until the clocks
split, and then it produced exactly the miss you found.

**Your rule is not a tightening of what I was doing. It is the reverse of it.** Taken
from now: a reply carries back the name it arrived with, untouched.

## 2. THE `memoTrays` COLLISION — YES, AND IT IS ANSWERED

**It is in your tray**, in the three-job letter —
`correspondence/open/owner/2026-09-10_memo_architecture_intake-tray-rotations-recommendation-and-the-export-design.md`.
**That one routed correctly; it is the open copy in my tray that did not clear, which
is why it still reads as unanswered to you.**

**The answer in one sentence so you do not have to go and find it: yes, it collides,
the derived ruling stands, and the watcher is the one that is wrong** — `memoTrays` is
typed in `memo.go` while `desks()` in `wake_desk.py` derives from the trays on disk and
quotes your 2026-09-10 ruling in its own comment.

**And the watcher's reason for typing it survives the change**, which is why it is
cheap: it wanted a typed list so a memo to a nonexistent desk is refused. **Refusal
comes from the tray not existing, not from the name being absent from a list.** Same
refusal, better source. **Ride it with the adjutant tray — same file, same rebuild,
same swap.**

## 3. THE §4 REQUIREMENT — WRITTEN DOWN, IN THE QUEUE, NOT BUILT

Added as section 9 of `claude/SPEC_an-answer-goes-back-to-the-sender-2026-09-10.md`,
which is where the supersede already lives. **Behind containment and the brakes,
exactly as you placed it.**

**A renamed answer is a protocol error, reported, not silently ignored.**

---

## ONE THING YOUR RULE SOLVES THAT YOU DID NOT CLAIM

**It fixes the supersede without anybody touching a clock.**

If a reply carries back the exact name it received, **both copies carry the same date
— right or wrong — and the basenames match.** The clock disagreement becomes cosmetic
rather than load-bearing.

**That is worth saying because the obvious fix was to go and change the watcher's
timezone**, which collides with the `America/Chicago` ruling already in the brakes
spec. **Your rule makes that fight unnecessary.**

## AND YOUR §2 — I DID NOT BUILD ON THE WRONG REASONING

**Checked.** My argument for a second reader of `protected_folders.txt` was that a
rule enforced by one program and not the other is a rule with one reader. **I never
cited rule 14 and nothing I have filed rests on it.** Your correction to the record
stands and changes nothing of mine.

*C1, 2026-09-11.*

---

**Owner, 2026-09-11. Read. Closed.**
