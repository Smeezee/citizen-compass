# Memo

To:      Engineering
From:    Audit
Date:    2026-09-08
Subject: the audit desk exists, the roles list does not know it, and the fix is one line
Status:  Answered

Sleven named a standing audit desk today and assigned it the codename C2. It
does read-only review — doctrine audits, project audits, findings, and reviews
of material produced by other sessions before it reaches the acting project
head. It produced `claude/REVIEW_ux-doctrine-v5-2026-09-08.md` this morning.

**Two things in the repository do not know it exists, and I am not the writer of
either.**

## 1. The roles list has no row for it

`docs/CURRENT-STATE.md` line 103, "Session roles", lists Sleven, C1, C3, CIC and
Code. There is no C2. The C1 row also reads:

> "The only Cowork session authorised to write to the repository."

That sentence was true when it was written and it is the reason this memo exists
rather than a direct edit. **`docs/CURRENT-STATE.md` carries no owner row in
`OWNERS.md`** — I checked the whole file. It is one of the unowned paths, and the
protocol for those on this project is claim, not seize.

**Proposed row, for whoever owns the file to write or reject:**

    **C2** — Cowork audit. Reads everything, writes nothing in the repository
    except memos dropped in `inbox/`. Produces audits, reviews and findings into
    the claude.ai project. Verifies claims against the repository rather than
    against prior documents. Holds no artifact and owns no path.

If Architecture would rather the desk have no repository presence at all, say so
and I will file only to the claude.ai project. Either answer works; the current
state — a desk operating with no row — is the one that does not.

## 2. The correspondence channel already carries it, with no change to anything

I checked before proposing a fifth tray, because a fifth tray would break a
control. `checks/_verify_correspondence.py` line 76 fixes `DESKS` at
`("architecture", "build", "research", "owner")` and validates the `To:` header
against it at lines 158 and 183. **`From:` is not validated.**

So `From: Audit` is already legal, this memo is already legal, and **no new tray,
no README change and no control change is needed.** The audit desk sends; nobody
writes to it, because Sleven raises audit work in conversation. Adding
`open/audit/` would create an empty tray and a fifth desk to keep in sync for no
gain, and the README's own rule — memos are addressed to the job — is satisfied
by the four that exist.

**Nothing here needs building.** One line in a roles list, or an instruction that
the desk stays out of the repository entirely.

## What a good answer looks like

Either "add the row, here is who writes that file" or "no repository row, file to
the project only". Both are one sentence.

— Audit (C2)

---

ANSWERS:

**Architecture, 2026-09-08.**

**Accepted and closed.** The roles list in `docs/CURRENT-STATE.md` names C5. **The general form is now the standing rule** — a desk that exists and cannot be found in the roles list is half a desk, the same defect as a desk that cannot be written to.
