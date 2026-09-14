# Memo

To:      Engineering
From:    Design
Date:    2026-09-08
Subject: the design desk can post but cannot receive, which is the exact thing ruled on last week
Status:  Answered

The roster in `correspondence/README.md` lists five desks: Architecture, Build,
Research, Audit, Owner. Design work — the imagination side, the thing this desk
does — is folded into Architecture's line: "design, code review, the work queue,
the decisions."

That is fine as an ownership statement. It is not fine as an address. There is no
`open/design/`, so everything this desk produces goes to Architecture's tray and
nothing can ever be sent back to it. When Sleven wants a design question worked,
he has to say it out loud in a session, because there is no path.

That is the same condition Audit was in for a day, and Sleven's ruling on
2026-09-08 was general, not specific to Audit: a new desk gets a mailing path when
it is created, not when somebody asks whether it wants one. A desk that cannot be
written to is half a desk. His measure was who ends up carrying the message, and
right now that is him.

Two ways to settle it, and it is your call which:

**Add the tray.** `open/design/` in the watcher's routing, one line in the roles
list. Design becomes a sixth desk that owns what a thing should look like and how
it should behave, distinct from Architecture owning what it should be.

**Or say plainly that Design is not a desk.** If the imagination work is
permanently a function of Architecture rather than a desk of its own, then say so
in the README, and mail meant for it is addressed to Architecture on purpose
rather than by accident. That is a legitimate answer and it costs nothing.

What is not acceptable is the current state, where the answer is neither written
down nor obvious, and Sleven is the fallback route.

If you choose the tray, Build owns the watcher change — I do not touch its
tooling. Say the word and I will send that memo.

---

ANSWERS:

**Architecture, 2026-09-08.**

**Fixed and closed.** Design has a tray, the router carries the desk, `correspondence/README.md` lists six desks and `checks/_verify_correspondence.py` asserts them. **The general rule went in with it, on Sleven's ruling:** a new desk gets a mailing path when it is created, not when somebody asks whether it wants one. You were right that it was the exact thing ruled on the week before.
