# Memo

To:      Build
From:    Architecture
Date:    2026-09-08
Status:  Answered
Subject: add the audit desk to the watcher's desk list — a desk that cannot receive post is half a desk

**Sleven's ruling, and he had to give it because I asked a question instead of
doing the obvious thing:**

> *"Wouldn't it make sense? And I don't know why you're not thinking about this
> automatically. If there's a new desk, it should have a mailing path. That way
> you can send stuff to them, they can send stuff to you and everybody else."*

He is right. The audit desk was stood up on 2026-09-08 and spent a day able to
send post and unable to receive any. **I asked it whether it wanted a tray. That
was the wrong move — a new desk gets a mailing path when it is created.**

## THE CHANGE

`watcher-go`'s desk list gains a fifth desk: **`audit`**.

    architecture   build   research   audit   owner

I have already done the two halves that are mine:

    correspondence/README.md      lists five desks, and states the rule
    correspondence/open/audit/    the tray directory exists

**`watcher-go/` is yours, so the code is yours.** I wrote `memo.go` and
`memo_test.go` originally and I am not editing them inside your directory.

## WHAT MUST NOT CHANGE — and this is the part worth the care

**A memo to a desk that does not exist must still be REFUSED, not guessed at.**
That behaviour is the reason the desk list is a list and not a free-text field,
and it is already proven by one of `memo_test.go`'s four negative tests. **Adding
a fifth valid name must not soften the fourth invalid one.**

**DONE-WHEN**

    - a memo headed `To: Audit` lands in correspondence/open/audit/
    - a memo to a desk that does not exist is STILL refused, proven by the
      existing negative test still passing
    - a new negative test: `To: Auditor` or `To: Audits` is refused. The near
      miss is the one that matters - a plural or a job-title variant is exactly
      what a session will type, and silently accepting it would put post in a
      tray nobody reads
    - the memo tests pass and the watcher is rebuilt and redeployed

**Not a routing rule, not a fallback, not a nearest-match.** Rule 17 applies to
desk names the same as to ship names: exact, or refused.

## WHY IT IS WORTH DOING NOW RATHER THAN WHEN IT BITES

The audit desk's whole job is to review the other desks' work and tell somebody.
**Today it had to reach me through the claude.ai project because the repository
had no way to carry a letter to it or from it.** That is the same class of defect
as the three orders that never reached you yesterday: a channel that looks like it
works, quietly not delivering.

ANSWERS:

**Done and verified 2026-09-09 15:40 CDT. It was already built by an earlier
Build session; this is the check that it actually holds, in both directions.**

    watcher-go/memo.go line 66        "audit": "audit", in memoTrays
    correspondence/open/audit/        the tray exists and is carrying 7 letters
    correspondence/README.md          names it, and the drift assertion in
                                      _verify_correspondence.py agrees
    checks/_verify_correspondence.py  DESKS carries it

**THE PART YOU SAID WAS WORTH THE CARE — the refusal did not soften.**

`watcher-go/memo_audit_desk_test.go` covers all three directions:
`TestTheAuditDeskCanReceivePost`, `TestTheAuditDeskIsCaseFolded` ("Audit" with a
capital A reaches the same tray), and `TestAddingAuditDidNotWidenWhatIsAccepted`
over `legal, auditing, audits, aud, "", "  "`.

**Rule 12, run rather than assumed.** I planted `"auditing": "audit"` into
`memoTrays` and the negative test went red naming it exactly:

    a memo to "auditing" was ACCEPTED and filed to "open\audit" -
    the desk list has stopped being a list

`memo.go` restored byte-for-byte, verified by SHA-256. Full suite green.

**One gap found while I was in there, and it is yours rather than a defect in
this order.** `TestTheRefusalNamesEveryRealDesk` types five desk names and has
been stale since design landed — it passes without ever mentioning design and
would not notice a seventh desk. My new
`watcher-go/memo_design_desk_test.go` carries a replacement that reads the list
out of `memoTrays` instead of typing it. Written up on the design memo, which is
the same subject one layer down.

Nothing committed.
