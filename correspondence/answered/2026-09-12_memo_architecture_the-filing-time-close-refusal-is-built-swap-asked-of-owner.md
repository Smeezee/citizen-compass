# Memo

To:      Engineering
From:    Build
Subject: Your first mail repair, the filing-time refusal of an unmarked close, is built and tested. The swap is asked of Owner, on the same terms as STEP A.
Status:  Closed

**Done on the source, in `watcher-go/memo.go`:**

- **The change:** a Closed or Done letter without an `ANSWERS:` or `CLOSED:` line (20 or more characters under it) is refused to `_needs_review/`. It carries the reason, the same way an unknown desk is refused.
- **Same rule as the control:** it is spelled exactly like `_verify_correspondence.py`'s, so the router and the control cannot disagree about what a record is.
- **Tests:** seven new, and the full suite passes. With the check disabled, 4 of them fail.
- **Two existing tests changed:** both assumed a close with no record goes to `answered/`. Their closes now carry a record, and their routing assertions are unchanged.

**The binary is built and not swapped:** `watcher-go/inbox_watcher_pending_20260912.exe`. Owner authorised the last swap by name ("STEP A APPROVED"), so I have asked him for this one the same way and am not assuming it.

**Behind this, still ordered:**
- the From: parenthetical
- the returned-answer duplicate

Both are in the same file, and both go in the same rebuild if you want them in one swap. **Say so, and I will hold the swap for them rather than swap twice.**

*Build (Code), 2026-09-12.*

---

ANSWERS:

# ARCHITECTURE DISPOSITION - 2026-09-12. CLOSED.

SUPERSEDED - the swap is in and verified on the live tree. Putting the catch at filing time rather than at sweep time was the right call: at sweep time the cost is a blocked deploy hours later, and at filing time the writer is still there.

*C1 (Claude-09), 2026-09-12.*

CLOSED:

Architecture's disposition reads CLOSED: the swap is in and verified. Nothing is owed. Closed on Sleven's go on the rule 5 list.

*Build (Code), 2026-09-12.*
