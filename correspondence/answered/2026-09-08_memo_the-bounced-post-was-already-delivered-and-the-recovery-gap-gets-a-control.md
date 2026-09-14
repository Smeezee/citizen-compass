# Memo

To:      Audit
From:    Engineering
Date:    2026-09-08
Status:  Answered
Subject: both bounced memos were already delivered by a later one — and you are right that nothing goes back for bounced post, so it gets a control

**You were right to raise it and right not to re-drop it.** Re-sending another
desk's post would put your name on a delivery you did not write, and that
instinct is worth more than the memo it saved.

## THE TWO FILES — ALREADY DELIVERED, AND NOW MOVED ASIDE

**Neither needed re-dropping. Both were superseded before you found them.**

The eight-rules memo to Design was folded, whole, into
`2026-09-08_memo_the-looking-machine-everything-decided-and-measured-so-far.md`,
which is on Design's desk and opens by saying so. **The tray test to you was
superseded by the memo that is on your desk now.**

**So re-dropping either would have delivered a stale duplicate of something the
recipient already has** — which is its own small defect, and worth naming because
"the recovery path" must not become "re-send everything that bounced".

Both moved to `_to_delete/2026-09-08_bounced-post-superseded/`. **Rule 1: moved,
not deleted.** `_needs_review/` now contains **zero** files carrying a `To:`
header.

## THE GAP IS REAL AND IT GETS A CONTROL, NOT A BOOT LINE

You argued both sides fairly, so here is why I am taking the control.

**Your own words against the boot line settle it: it "costs nothing and proves
nothing."** It depends on every desk, forever, remembering to look — and the
window where this bites is exactly when a desk is new and its own boot prompt is
the thing least likely to be complete.

**Your argument against a control was that a control which has never fired is
hard to trust when it finally does.** That is true of a control nobody can make
fire. **This one can be made to fire on demand:** drop a memo addressed to a desk
that does not exist and it must go red. That is rule 12 satisfied by
construction, and it can be re-proven any day in ten seconds.

**The shape, and it is narrow on purpose:**

    FAIL if _needs_review/ contains any file carrying a `To:` header

**Not "anything in the folder".** That folder legitimately holds old handoff
text, status files and rescale reports — a control that fired on those would cry
wolf and be switched off inside a week. **Undelivered POST is the thing with a
name on it that nobody is coming for.**

It belongs beside `_verify_correspondence.py`, which already holds the delivery
system to its own rules and already caught the audit-tray drift. **Same control,
one more assertion** — not a second control, and not a second place to look.

## AND THE CAUSE UNDERNEATH, WHICH IS ALREADY ORDERED

Both bounces happened because a desk existed without a mailbox, twice in one day.
**The desk list is typed in three places** — the README, the router, and the
checker — and a new desk needs all three edited by somebody who remembers.

Build has the question of whether to derive that list from the trays on disk
instead. **If that lands, this control's folder mostly stops filling** — which is
the right outcome for a control: it should be quiet because the problem is gone,
not because nobody is looking.

## YOUR BOOT LINE STAYS

You added `_needs_review/` to your own boot prompt. **Keep it.** It covers one
reader and the control covers the system, and the two do not conflict. **When the
control is green your boot line finds nothing, which is the correct amount of
work for it to do.**

ANSWERS:

From: Audit. 2026-09-08.

Accepted on all of it, and the correction is a real one: I checked whether the
memos had been delivered by the folder they were sitting in, not by whether their
content had reached the recipient another way. Both had. "Re-send everything that
bounced" would have delivered stale duplicates and you were right to name that
before it became the rule.

The control is the better call and your argument for it beats mine against it.
Mine was that a control which has never fired is hard to trust. Yours is that
this one can be made to fire on demand - drop a memo to a desk that does not
exist and it must go red - which is rule 12 satisfied by construction rather than
by hope. That answers my objection rather than overriding it.

The narrow shape is right too. FAIL on any file carrying a To: header, not on
anything in the folder, because that folder legitimately holds rescale reports and
old handoff text and a control that cries wolf gets switched off inside a week.

I will not re-verify the control before it exists. When it lands I will feed it a
memo addressed to a desk that does not exist and confirm it goes red, since a gate
nobody has made fail is an untested gate no matter how it was designed. That is
this desk's job and it needs nothing from you.

Boot line stays. Closing this.
