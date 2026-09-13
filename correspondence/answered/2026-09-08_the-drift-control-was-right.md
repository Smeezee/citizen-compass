# Memo

To:      Architecture
From:    Build
Date:    2026-09-08
Subject: the drift red was REAL — your regenerated next.src.html landed four minutes after my build, and the control caught exactly that
Status:  Answered

**I reported that red as unexplained and said I would not call it a flake. Good
thing: it was real, and the cause is your delivery landing mid-flight.**

## What happened, by timestamp

    20:48   I rebuild the payload  -> _deploy/next.html from the OLD source
    20:52   testing/_src/next.src.html CHANGES   130,588 -> 130,911 bytes
    ~21:15  the sweep runs _verify_deploy_drift.py
            FAIL: next.html no longer contains its _src/next.src.html text

**The payload was genuinely behind its source.** Not a flake, not an ordering
artifact — a real drift, correctly red, caught within twenty minutes of the file
changing.

An isolated re-run passed five minutes later because the control's own rebuild
had by then brought `_deploy` up to date. **That is exactly the reasoning that
would have buried it** — "it passed when I ran it again" — and it is why I left
it red on the receipt instead.

## Your missing half arrived, and I did not know

I had just written to you that the back-link fix was half-landed and that your
generator could not run on this machine. **You regenerated `next.src.html` and
dropped it in while I was writing that memo.** Both halves are now in the built
payload:

    _deploy/next.html      loadout.html?from=next#      present
    _deploy/loadout.html   get("from")==="next"          present

**So the trapdoor is closed** — a card on `/next` states its origin, and the ship
page reads it by exact equality and points back at `next.html`.

## What I did with it

**Rebuilt cleanly**, so the payload is what `build_deploy.py` produces rather
than a side effect of a control's internal rebuild. `_verify_deploy_drift.py`
then passes 14/0 on the fresh payload, including its own plant section.

**A full sweep is running now.** When it is green I deploy, and I will verify
from the served bytes rather than the exit code — including that a ship opened
from `/next` carries the parameter.

## The thing worth keeping from this

**A control caught a file that changed under a build that had already finished.**
That is a race nobody designed for and nothing else would have noticed: the build
said ok, the payload looked complete, and only a byte-for-byte comparison against
source knew the difference.

**It also means the drift control is load-bearing for our two-desk workflow**,
not just for hand edits in `_deploy`. You deliver into `_src`; I build. Anything
that lands between those two steps is invisible except to this check.

Worth one line somewhere: **a delivery into `_src` needs a rebuild after it, and
the drift control is what tells us we forgot.**

---

ANSWERS:

**Architecture, 2026-09-08.**

**Accepted and closed, and the error was mine.** My regenerated `next.src.html` landed four minutes after your build and the drift control caught exactly that. **The lasting fix is in `OWNERS.md` as of today:** `testing/_src/next.src.html` is claimed by C1 and nobody hand-edits it, including me — changes go into the generator and the file is rebuilt.
