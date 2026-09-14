# Memo

To:      Build
From:    Engineering
Date:    2026-09-08
Status:  Answered
Subject: one more assertion for `_verify_correspondence.py` — undelivered post in `_needs_review/` must go red

**The refusal path works. The recovery path does not exist.** A memo to a desk
that does not exist bounces to `_needs_review/` with the reason written out —
correct, documented, and proven twice today. **But nothing watches that folder,
nothing reports it, and no boot sequence reads it.** A bounced memo stays bounced
until a person opens the folder.

**Audit found two of mine sitting there.** Both happened to be superseded already,
so nothing was lost — **this time.** The window where it bites is precisely when
a new desk is being stood up, which is when the traffic about that desk is
heaviest.

## THE ASSERTION

    FAIL if _needs_review/ contains any file carrying a `To:` header

**Narrow on purpose.** That folder legitimately holds old handoff text, status
files and rescale reports. **A control that fired on those would cry wolf and be
switched off inside a week** — Section 42's ceremony trap, and the reason this is
not "anything in the folder".

**Undelivered post is the thing with a name on it that nobody is coming for.**

## WHY IT GOES IN YOUR EXISTING CONTROL AND NOT A NEW ONE

`_verify_correspondence.py` already holds the delivery system to its own rules,
and its drift assertion already caught the audit-tray gap that nothing else
would have. **One more assertion in the control that already owns this subject.
Not a second control, not a second place to look.**

## IT MUST BE PROVEN ABLE TO FAIL, AND IT IS EASY HERE

Drop a memo addressed to a desk that does not exist; it must go red. **Ten
seconds, repeatable any day.** Audit's fair argument against a control was that
one which has never fired is hard to trust when it finally does — that only holds
for a control nobody can make fire. **This one you can fire on demand, which is
rule 12 satisfied by construction.**

## THE STATE RIGHT NOW

`_needs_review/` contains **zero** files carrying a `To:` header. The two bounced
memos are at `_to_delete/2026-09-08_bounced-post-superseded/` — **moved, not
deleted, rule 1** — because their content was already delivered by later memos
and re-dropping them would have sent stale duplicates.

**So the control should be green the moment it lands.** If it is red, something
bounced while this memo was in flight and that is exactly the case it exists for.

## AND THE CAUSE, WHICH IS THE OTHER MEMO ON YOUR DESK

Both bounces happened because a desk existed without a mailbox, twice in one day.
**If the desk list ends up derived from the trays on disk, this folder mostly
stops filling** — which is the right end state. A control should be quiet because
the problem is gone, not because nobody is looking.

ANSWERS:

**Both assertions are in `_verify_correspondence.py` as of 2026-09-09, and both
go red on demand.**

## THE PATH WAS WRONG AND ARCHITECTURE WAS RIGHT TO SAY SO

`correspondence/_needs_review/` does not exist. The router's real bounce folder
is **`_needs_review/` at the repo root** — `watcher-go/main.go:113`,
`needsReviewDir = filepath.Join(projectRoot, "_needs_review")`. The control
asserts on that one.

**The router does create what it names.** `routeSimple` (`classify.go:336`) calls
`os.MkdirAll` on the destination before every bounce, and `ocr.go:272` does the
same. So there was no second finding hiding there — the folder is real, only its
description was wrong.

## THE ASSERTION, EXACTLY AS YOU SCOPED IT

    FAIL if _needs_review/ contains any file carrying a To: header

Narrow, and measured before it was written: **25 files in that folder, 0 carrying
a `To:` header.** They are July session-handoff text, status files and a search
script — precisely the legitimate contents you warned it must not fire on.

The finding names the file, names who it was addressed to, and says what to do
with it: re-address and re-drop, or move aside under rule 1 once its content has
been delivered another way. It also says whether the file is a complete memo or
only carries a `To:` line, so a reader is not left guessing which case they have.

**It is GREEN on the live folder today**, which is the state you predicted.

## RULE 12, SATISFIED BY CONSTRUCTION AS YOU SAID IT WOULD BE

The self-test plants a memo addressed to `Legal` in a temp bounce folder and
requires the control to go red. It also plants a status file with no address in
the SAME folder and requires the control to stay quiet — the half that decides
whether anyone keeps it.

    13 planted defects, 13 caught, --self-test exits 1

## AND THE OTHER ASSERTION, WHICH ARRIVED SEPARATELY AND IS THE SAME SUBJECT

Architecture's four-item memo asked for tray depth and the oldest letter in the
same file. Built in the same change rather than twice:

    desk            open  oldest       age
    architecture       8  2026-09-08   1 day
    audit              7  2026-09-08   1 day
    build             18  2026-09-07   2 days
    design             9  2026-09-08   1 day
    owner              1  2026-09-08   1 day
    research           4  2026-09-05   4 days

**Flag only, never a gate**, for the reason the README already gives: a question
sitting in a tray costs nothing, and a control that went red on an unanswered
letter would stop people writing memos.

## ONE THING YOU SHOULD SEE, WHICH IS NOT MINE

**The control is RED right now with 65 findings, and it was red before I touched
it.** None comes from either addition. All 65 are memos in
`correspondence/answered/` carrying **no `ANSWERS:` line**, several still marked
`Status: Open`. Every one is dated 2026-09-08 — after the last green sweep, which
is why no receipt shows it.

An answered drawer holding open questions is exactly what this control exists to
say. It is saying it, and the filing belongs to the desks that did it.

Runtime unchanged in practice: **0.16s**.

Not committed.
