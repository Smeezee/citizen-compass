# Memo

To:      Owner
From:    Build
Date:    2026-09-10
Subject: The answer routing is built, tested and proved on a copy. Reporting before the swap, as ordered. The running watcher is untouched.
Status:  Closed

**Every condition you set is met except the last one, which is yours to give.
`C:\Users\david\citizen-compass\inbox_watcher.exe` has not been touched and is
still the binary moving your mail.**

    build it and test it                          DONE
    prove the three cases by TEST, each made
    to FAIL first                                 DONE - 5 tests seen to fail
                                                  against the old router
    prove an answer to Owner reaches your tray,
    ON A COPY                                     DONE - 9 of 9, live tree
                                                  untouched
    keep the current binary, named, recoverable   DONE - nothing replaced;
                                                  the new one is staged beside
                                                  it under its own name
    REPLACE THE RUNNING WATCHER                   NOT DONE. Waiting on you.

---

## WHAT CHANGED, IN THREE LINES OF BEHAVIOUR

    Status: Open       ->  open/<To:>      a question travelling out
    Status: Answered   ->  open/<From:>    the answer travelling back
    Status: Closed     ->  answered/       the thread is finished

**On `From:`, not `To:`.** Answering a memo appends a block and flips the
status - it does not change the headers - so an answered letter of yours still
says `To: Architecture`. **Routing it on `To:` would have sent your answer back
to the desk that just wrote it.** Architecture caught that; I built what it
specified.

`From:` is now validated on an answered memo only, and an unknown sender is
refused to `_needs_review/` rather than guessed at. **An open letter with an odd
`From:` still routes exactly as it does today** - refusing working traffic over
a header nobody has ever filled in carefully would cost more than it saves.

`clearOpenCopy` is told which tray not to touch, and its gate widened from "did
it go to answered/" to "is it answered".

## THE PART YOU ASKED FOR SPECIFICALLY - AN ANSWER REACHING YOUR TRAY

**Run against a real copy of the tree, with the newly built binary, in a temp
folder. Not simulated - the actual watcher process, watching an actual inbox.**

    THE ANSWER REACHES HIS TRAY - correspondence/open/owner/        PASS
    and it is the answer, not the question                          PASS
    and it did NOT go into the archive nobody reads                 PASS
    the answered question left Architecture's tray                  PASS
    and the superseded copy was KEPT, not deleted (rule 1)          PASS
    a desk answering a desk reaches THAT desk's tray too            PASS
    an answer from an unknown desk goes to _needs_review            PASS
    and the refusal moved NOTHING out of anybody's tray             PASS
    the LIVE inbox was untouched by any of this                     PASS

**The copy cannot become a second watcher on your real inbox, and that is
structural rather than a promise I am making:** the watcher takes its project
root from the folder its own executable sits in, so a binary in a temp folder
is physically unable to see `citizen-compass\inbox`. Rule 14's defect, closed by
where the file is rather than by care.

## MADE TO FAIL FIRST - THE CONDITION I WOULD HAVE CUT IF YOU HAD NOT WRITTEN IT

**The new tests were run against the OLD router. Five of them failed, which is
what makes them tests rather than decoration:**

    TestAnAnswerArrivesInTheSendersTrayAndSurvives      FAILED, as it must
    TestAnAnsweredMemoGoesBackToTheSender               FAILED, as it must
    TestAnAnsweredMemoFromAnUnknownDeskIsRefused        FAILED, as it must
    TestADeskAnsweringItselfGoesToTheArchive            FAILED, as it must
    TestTheFourStatusWordsRouteWhereTheSpecSays         FAILED, as it must

**Five others passed against the old router too, and that is correct** - they
assert behaviour that did not change: an open memo still routes on `To:`, a
closed thread still reaches the archive, an unknown addressee is still refused.
**A test that passes before and after is either a regression guard or a lie, and
these are the first kind.**

### AND THE THIRD CASE PROVED ITSELF ON THE MACHINE

Architecture's warning was that the supersede sweep would delete the answer it
had just filed, **nondeterministically**, because Go randomises map order.

**Ran the sweep the old way forty times: it took the ANSWER on nine of them.**
Not argued - counted. That test is in the suite permanently, and it fails if the
map order ever stops being random, because at that point the argument for the
guard needs re-reading.

## WHAT IS STAGED, AND HOW THE SWAP GOES WHEN YOU SAY SO

    running now, untouched   C:\Users\david\citizen-compass\inbox_watcher.exe
                             5,768,192 bytes, 2026-09-09 21:58
    the new one              watcher-go\inbox_watcher_pending_20260910.exe
                             5,770,752 bytes, built 2026-09-10 15:14

**On your word: stop the task, move the current binary aside under a dated name
(rule 1 - moved, never deleted), copy the pending one into its place, start the
task, and drop one memo through it to confirm the mail still moves.** If
anything looks wrong the old binary is one move back.

**I am not doing any of that until you say so.** Your reasoning is the right
one: if the mail stops, nothing in this project can tell anybody that the mail
stopped.

## TWO THINGS I DID NOT DO

**The nine letters already in `answered/` are where they are.** Architecture
ruled against a migration and I agree - guessing which still need answering is a
second guess about each one. Re-open any you want by hand.

**The watcher's missing rescan** - the `fsnotify` buffer-overflow defect
Architecture filed at 13:40 - is not in this build. Different fix, different
memo, and bundling it would have given a failed swap two possible causes.

## AND THE BRAKES ARE PARKED, NOT ABANDONED

Items 1 and 2 (the record shape, the master switch) are in and tripped. **Item
3, the per-desk lock, is not started and resumes the moment this is off my
desk.** Nothing wakes; the switch is off and the machine is fail-closed.

---

ANSWERS:

**Closed. Step A is done and this letter is what it asked for.**

The swap went in at 19:47, the rollback was taken and hash-verified first, and all
four conditions passed on the live tree. **Superseded by
`2026-09-11_memo_owner_step-a-is-done-the-swap-is-in-and-verified-on-the-live-tree.md`.**

`Status: Closed` rather than `Answered` on purpose — **the thread is finished and
does not need to travel back to you.** First deliberate use of the third word, on
the binary that made it mean something.
