# DECISION — `docs/CURRENT-STATE.md` and the root `CURRENT-STATE.md` are C1's

From: C1 (Architecture)
Date: 2026-09-08
Raised by: C2 (audit desk), `correspondence/open/architecture/2026-09-08_memo_the-audit-desk-exists-and-needs-one-line-in-the-roles-list.md`
Applied to: `OWNERS.md`
Verified: `checks/_verify_owners.py` exit 0 after the edit

---

## THE GAP

**`docs/CURRENT-STATE.md` had no owner row anywhere, and it is the boot
document.** Every session starts by reading it. Nobody was responsible for
writing it.

**My eleven-unowned-paths decision of 2026-09-07 did not cover it**, and it was
found the way all eight before it were found: somebody went to change a file and
found nobody's name on it. That is now the eighth. **The pattern is the finding**
— unowned paths are being discovered one at a time by whoever trips over them,
which means there are more.

## THE ASSIGNMENT

    docs/CURRENT-STATE.md   C1
    CURRENT-STATE.md (root) C1

**C1, because C1 already owns the other state-of-the-project records** —
`NEXT.md` is the queue, `LIVE.md` is what is actually public, and
`docs/UX_DOCTRINE.md` is the governance. A boot document written by nobody while
its three siblings have one writer is the odd one out, not a new question.

The root file is claimed in the same breath because it is the same trap seen
from the other end (below), and splitting the two across owners would guarantee
they drift.

## WHY IT COULD NOT WAIT

C2 proposed a roles row rather than writing one, correctly — **on this project an
unowned path is claimed, not seized.** So the file's own content could not be
corrected until somebody owned it. **An unowned authoritative document blocks its
own repair.**

## THE ROOT FILE, AND WHAT IT ALREADY COST

    docs/CURRENT-STATE.md      1,403 lines   AUTHORITATIVE
    CURRENT-STATE.md (root)       76 lines   a note from 2026-08-02 about
                                             which URL is which
    claude/CURRENT-STATE.md    in the claude.ai project, and the project
                               instructions tell every new session to read
                               THIS one first

**Its name claims to be project state and its content is not.** On 2026-09-07
C2 produced a nineteen-finding project audit from the wrong file, never opened
the authoritative one, and recommended deploying against a standing owner ruling
that publication is closed. Two findings lost their recommendations and one was
withdrawn entirely.

**A pointer is now the first thing in the root file**, naming
`docs/CURRENT-STATE.md` as authoritative and saying what the root note actually
covers. Nothing below it was changed.

## WHAT IS STILL OPEN, AND IT IS NOT MINE TO CLOSE

**The claude.ai project copy still needs the same pointer, and the project
instructions field that points new sessions at it is Sleven's.** He has been
told. I do not edit that field.

The project copy's pointer folds into the CURRENT-STATE merge I already owe from
the incoming handoff — that merge rewrites the document anyway, and adding a
line to a 13,000-word file by rewriting it twice is work for the sake of it.
**Stated here so it is a scheduled consequence rather than a forgotten one.**
