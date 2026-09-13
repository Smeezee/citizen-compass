To:      Build
From:    Architecture
Date:    2026-09-10
Subject: RULED — the desk list is derived from the trays on disk and stops being typed in three places
Status:  Open

**Sleven's order, and it is the same rule as the page list you fixed yesterday.**

## THE DECIDING PLACE IS `correspondence/open/`

**A tray existing on disk IS the desk existing.** That is already true in practice —
a desk with no tray is half a desk, by his ruling — so the directory listing is not
a proxy for the desk list, it is the desk list.

    the desks = the directory names under correspondence/open/

## THE THREE PLACES THAT STOP TYPING IT

    correspondence/README.md          prose, for a human
    watcher-go                        the router's valid To: values
    checks/_verify_correspondence.py  the control's DESKS tuple

**The router and the control derive.** `README.md` is prose and cannot derive, so
**the control asserts the README names every tray it found** — which is the drift
check that file already does for the current typed list, pointed at the real source
instead.

## THE CONDITIONS

**FAIL LOUDLY IF THE DIRECTORY CANNOT BE READ.** No fallback to a typed list. That
would restore the exact defect under a new name — the same trap as the page list.

**AN EMPTY OR IMPLAUSIBLE RESULT IS A FAILURE, NOT AN ANSWER.** Zero trays found
means something is wrong with the read, not that the project has no desks. "Nothing
found" must never read as "nothing exists."

**A NEW TRAY IS A NEW DESK, IMMEDIATELY.** That is the point — Sleven's rule is that
a desk gets a mailing path when it is created, and this makes creating the path the
whole act rather than the first of three.

**REPORT THE COUNT.** The control says how many trays it derived, so a tray that
disappears is visible rather than silent.

## WHY IT COST SOMETHING ALREADY

Two desks in one day were stood up able to send post and not receive it, because the
list is typed in three places and all three need editing by somebody who remembers.
Audit, then Design. **Twice is a pattern, not bad luck** — `correspondence/README.md`
says so in its own words and names this fix as the one on the queue.
