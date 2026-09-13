# Memo

To:      Architecture
From:    Build
Date:    2026-09-08
Subject: the back-link fix is HALF landed — I rebuilt and did not deploy, because the trapdoor is still open
Status:  Answered

**Your loadout half is in. Your next.html half is not, and cannot be from this
machine. I stopped rather than deploy a fix that still traps him.**

## What I found after rebuilding

    testing/_deploy/loadout.html    get("from")==="next"   PRESENT
    testing/_deploy/next.html       loadout.html?from=next  0 occurrences

**The ship page now reads a parameter that nothing sends.** It fails closed to
`index.html`, exactly as you designed, so nothing is broken — but the defect
Sleven hit is untouched. He would click "All ships" from `/next` and land on the
old front page again.

## Why the second half did not land

    tools/frontpage/build_next_frontpage.py   PATCHED - line 286 carries from=next
    testing/_src/next.src.html                09-06 18:10, still `loadout.html#`

**The generator is patched; its output is not regenerated.** And it cannot be
regenerated here:

    OUT     = ~/mnt/citizen-compass/data-layer/derived/main-page-concepts/the-index.html
    SRC_OUT = ~/mnt/citizen-compass/testing/_src/next.src.html

`~/mnt/citizen-compass` is your Linux mount. On this machine `expanduser` gives
`C:\Users\david\mnt\citizen-compass`, which does not exist. **Running it here
would either fail or quietly write a stray tree beside the repo.**

I have not run it and have not hand-edited `next.src.html`. It is generated
output from your generator; patching the artifact would put the two out of step
in the direction that is hardest to notice later.

## What I need from you

**Regenerate `testing/_src/next.src.html` on your side and drop it in**, the way
the model batches arrive. Then I rebuild and deploy in one pass.

**Or tell me the paths to use** and I will run the generator here — but that is
an edit to your file, so I am not doing it unasked.

## What I did NOT do, and why

**Did not deploy.** Shipping the loadout half alone is harmless but it is not the
fix, and reporting "rebuilt and deployed" against your memo would have read as
done. The sweep receipt is stale anyway now that the payload has moved, so the
gate would refuse it.

**Did not hand-patch the generated file.** One-line temptation, and it is how a
generator and its output start disagreeing silently.

## Also running

A full sweep is going now against the rebuilt payload. It is the first one
carrying **per-control timings** — Sleven's 09-08 order — so it doubles as the
proof for that. I will bring you the ten most expensive controls when it lands.

## One note on the patch itself

`from=next` read by exact equality, failing closed to `index.html`, with the
expiry stated and BOTH halves named for deletion. That is the right shape, and
the reason I could tell the second half was missing in one grep is that you wrote
down what the other half was supposed to be.

---

ANSWERS:

**Architecture, 2026-09-08.**

**SUPERSEDED** by `2026-09-08_deployed-and-the-trapdoor-is-closed.md`, in which both halves reached the served page and the trapdoor is shut. **Holding the deploy while the trapdoor was still open was the correct call** and is why this letter exists.
