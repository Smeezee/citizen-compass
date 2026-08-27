# RULING — the exposed credentials were rotated. CLOSED. This is the SECOND file written this week for the same structural reason, and that is the finding.

    ruled by  Sleven, 2026-08-15, in session. Standing ruling.
    status    CLOSED. Do not re-raise, do not re-ask, do not "flag for
                awareness". A session that raises this again has not read this
                file.

---

## The ruling, in Sleven's words

> "the leaks with the passcodes and stuff like that and the tokens — that has
> already been taken care of. Like, completely wipe that from the thing. I don't
> understand why that keeps coming up."

## What is settled

**All three were rotated by Sleven. There is nothing outstanding.**

    UEX token             rotated
    PostgreSQL password   rotated
    Cloudflare token      rotated

**Older documents in `docs/` still describe these as exposed and unrotated.**
`CURRENT-STATE.md` said so until today, and so do
`handover-to-c1-20260805.md`, `workorder-backup-01-external-drive.md`,
`workorder-cloudflare-testing-deploy.md`, `workorder-finish-phase1.md`,
`workorder-task2-source1-reacquisition.md` and
`prompt-code-collector-cloud-upload-2026-08-10.md`.

**Those documents are stale. They are not evidence of an open item.** They were
true when written and were never updated, which is a different thing from being
true now. **This ruling outranks every one of them.**

## THE ACTUAL FINDING — this is the second identical failure in 24 hours

**Yesterday:** `RULING_rights-questions-are-settled-2026-08-14.md` was written
because sessions kept re-raising a settled rights question. Its diagnosis:

> "The document was the cause, not anybody's memory. A session doing exactly
> what it was told to do produced the loop."

**Today: the same list produced the same loop about credentials.** I read
`CURRENT-STATE.md`, saw three security items marked open, and handed Sleven a
list of three passwords to change that he had already changed. **I even wrote a
note into that section this session pointing out that item 3 was a token — while
failing to ask whether any of them were still true.**

**Two different topics, one cause: a list of open items that nothing updates when
the item closes.** Every session is instructed to read `CURRENT-STATE.md` first,
so every session inherits every stale entry and dutifully raises it.

**This will happen a third time on a different topic unless the mechanism
changes.** The rights ruling fixed its own entry. This one fixes its own entry.
Neither fixes the list.

## What should change, so this stops needing a ruling each time

**Every entry in "Open, and only Sleven can do these" needs a date and a last-
confirmed marker.** An item nobody has re-confirmed in weeks is not "open" — it is
**unknown**, and it should say so rather than presenting as fact.

**That is the lifecycle rule this project already adopted** for checker findings
after the 874-findings incident: *a finding is CLOSED only by a run that looked
and did not find it; a check that was skipped goes to UNKNOWN, never CLOSED.*
**The open-items list is a findings list with no lifecycle attached to it.**

**Recommendation, not an instruction — this is Sleven's document:** before any
session presents an item from that list as open, it re-checks it or presents it as
unconfirmed. And when Sleven closes something in conversation, the closing goes
into the list the same day, not into a chat transcript nobody re-reads.

## What a session should do instead

- **Do not re-raise the credentials.** Not as a question, not as a caveat, not as
  "just flagging". Flagging is raising.
- **Do not attach it as a rider** to unrelated work.
- **Do not trust an older document that says they are exposed.** Check the date.
  If it predates 2026-08-15, it is stale on this subject.
- If a **new** exposure occurs — a fresh credential in a fresh screenshot — that is
  a new fact and must be raised as one, naming what leaked and when. Nothing else
  qualifies.

## What I checked and what I did not

**Checked:** which documents in `docs/` still describe these credentials as
exposed — listed above by name, so nobody has to rediscover them.

**Did NOT check:** the credentials themselves. **I have no way to verify a
rotation and I am not implying I did one.** This records Sleven's statement that
they are done, which is the only evidence that exists and is sufficient. **The
stale documents were NOT edited** — there are seven of them, several are historical
work orders, and rewriting history to match the present is worse than a ruling that
outranks it.
