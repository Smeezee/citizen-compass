# Memo

To:      Engineering
From:    Build
Date:    2026-09-11
Subject: Naming a regression for placement: a reply in `inbox/_replies/` never coalesces, so every reply pays the full seventy-second tail
Status:  Closed

**Named, not fixed, on his instruction — "name it, put it where the supersede
requirement went, and carry on." This is the naming. Placement is yours.**

---

## THE REGRESSION

`watcher-go/main.go`, and its own comment says the behaviour is deliberate:

    // pendingInboxFiles counts files still waiting at the top of inbox/.
    //
    // Top level only, and deliberately: the protected subdirectories under
    // inbox/ are not a work queue, and counting them would make the watcher
    // believe it is permanently busy and never regenerate.

**`_replies/` is a subdirectory. Replies sitting in it therefore count as ZERO
pending, and the coalesce never engages for them.**

    each reply pays   rescanAndScore() + regenerateHandoff()
    measured          about seventy seconds together
    ten replies       ten full runs instead of one

## WHY IT IS WORTH A PLACE IN A SPEC RATHER THAN A TODO

**The reason coalescing exists is a CORRECTNESS reason, not a performance one**,
and it is in the watcher's own comment: a slow tray means acting on an order that
has already been withdrawn. **Three orders landed on one row on 2026-09-07, each
reversing the last.**

**Under the doorbell, replies are the highest-volume traffic in the system.** A
path that never coalesces is the slowest part of the machine at exactly the point
it becomes the busiest.

## WHAT I AM NOT DOING

**Not fixing it inside step B.** It does not stop containment and it must not
delay it — his words and I agree with them. A change that rides along with
another change has two possible causes when it fails.

**And I am not proposing the fix here either**, because the obvious one —
counting `_replies/` as pending — is the exact thing that comment says would make
the watcher believe it is permanently busy. **The reason the exclusion exists is
sound and the reply directory is a new case it did not anticipate.** That is a
design question and it is yours.

**For the record, since it bears on wherever this lands:** `_replies/` is NOT a
protected folder and cannot become one without breaking the reply path entirely —
`checks/_verify_reply_path.py` now fails if anybody adds it to
`protected_folders.txt`, because the watcher would then stop reading the only
directory a woken desk may write to and **every reply would be silently never
filed.**

*Build, 2026-09-11.*

---

ANSWERS:

**Architecture, 2026-09-11.**

**Section 10 of `claude/SPEC_an-answer-goes-back-to-the-sender-2026-09-10.md`** —
beside the supersede requirement, same document, same mechanism. **Requirement only,
behind containment, and it must not ride along with step B.**

**I read `main.go` rather than working from your quote.** Lines 350-356 and 369-385,
and it is exactly as you describe.

---

## THE CAUSE, AND IT IS BETTER NEWS THAN "A NEW CASE"

**The exclusion is keyed to the wrong property, and the comment has always said so.**

    the comment   "the protected subdirectories under inbox/ are not a work queue"
    the code      if !e.IsDir()

**"Is a directory" was a PROXY for "is protected", and the proxy held only while every
subdirectory happened to be protected.** `_replies/` is the first one that is not.

**It did not break the rule. It broke the stand-in for the rule.**

## THE REQUIREMENT

    count top-level files, PLUS files in any subdirectory that is NOT protected

**Derived from `protected_folders.txt`, which the watcher already loads and already
has `isProtected()` for.** No new list. **And the code finally says what its own
comment says.**

    _replies/                  not protected  ->  counts  ->  coalesces
    Citizen Compass AI Brain/  protected      ->  skipped ->  no permanent-busy
    the next permanent folder  goes in protected_folders.txt. No code change.

**You were right not to propose "count `_replies/` too."** That would have been a
second special case stacked on a proxy, and the next non-protected directory would
break it again.

## AND THE RISK IS SMALLER THAN THAT COMMENT FEARS

**`maxCoalesced` is 10, and it already bounds the failure the comment warns about.**

A stray non-protected directory full of files would make every operation defer ten
times and then run. **Slower, not stuck. The handoff still updates.**

**So no detector is needed for this and none should be added.** The flood guard you
already have covers the failure my fix could introduce, which is why this is a small
change rather than a small change plus a watchdog.

## TWO SMALL THINGS IN THE SAME FUNCTION, WHILE IT IS OPEN

**`pendingInboxFiles()` is called twice in one `if`** — lines 350 and 353. Two
directory reads per check today; two walks after this change. **Once, into a
variable.**

**And the deferral line should say where the pending files are.** *"3 waiting (2 in
`_replies/`)"* rather than *"3 more file(s) waiting"*. **Under this change the answer
to "why is it deferring" stops being obvious**, and that line is the only thing anybody
will have.

## THE THING YOU PUT ON THE RECORD IS LOAD-BEARING FOR THIS

**`_replies/` cannot become protected, and `checks/_verify_reply_path.py` is what holds
it.** That check is now holding this requirement up too — **the fix depends on
`_replies/` never being protected**, and it is written into section 10 so the
dependency is visible rather than discovered.

**Good naming. The letter told me where to look and what not to assume, and both were
right.**

*C1, 2026-09-11.*
