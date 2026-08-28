# Update — Deployed. C1's transparency and panel-side changes are live on testing, and `_verify_deploy_drift.py` is back to 12/0.

**2026-08-27 22:37 local · Code (background session)** — Sleven: *"build and
deploy it"*. Version `8589fbab-851a-4c58-ba49-936b1e77902b`.

## Exactly the two files C1 touched, and no others

    + /cc_viewer.js
    + /loadout.html
    Uploaded 2 files (522 already uploaded)

**Two uploads for two changed sources** is the correct blast radius. If a third
file had moved, that is the number that would have said so.

Build clean: seven in-process gates passed, `deploy guard: safe to deploy`,
4 browser checks GREEN, hull markers unchanged at **6,400 on 271 hulls**.

## THE DETECTOR IS GREEN AGAIN, AND THAT IS THE POINT

    _verify_deploy_drift.py    12 passed, 0 failed    exit 0

It was red at 22:18 **because** `_deploy` and `_src` disagreed after C1's write.
A deliberate build is what makes them agree, so this going back to 12/0 is the
proof that the payload is what the source says it is. **The rule 14 detector
went red on an unauthorised write and green again once the write was
acknowledged and shipped through the front door.** That is the whole mechanism
working end to end, for the first time.

## Both features confirmed in the SERVED bytes, not in the build log

    served /cc_viewer.js     hullAlpha: 0.86        13 occurrences
    served /loadout          let side = (px <= sw/2) ? "left" : "right"   present
    served /loadout          the old `let side = "right"` rule             GONE
    served /loadout          C1's rationale comment                        present

And the served page is byte-identical to what was built:

    served  sha256 6d8d2e279a6f18c6...
    local   sha256 6d8d2e279a6f18c6...

**Fetched from `/loadout`, not `/loadout.html`.** My first attempt used the
`.html` path and came back **0 bytes**, which I nearly wrote up as a missing
feature — the worker serves the extensionless route. Worth recording: a
zero-byte fetch reads exactly like a page that lost the change.

## Still green after the deploy

    _verify_deployed_links.mjs    SWEEP CLEAN, canary reporting
    Drake Buccaneer               8 dots, 8 visible, model loaded

## The provenance, stated once more so the record is complete

These two changes entered `testing/_src/` from C1 rather than through this
session — a rule 14 breach in the channel, detected at 22:18, reported at 22:28,
and authorised by Sleven at 22:33. **The content was never the objection**; every
control that touches it was green before the deploy and after.

What rule 14 asks for is that such a write be loud and immediate rather than
found later in a diff. It was.

Nothing committed since `2fc7008` — the two source files and the rebuilt payload
are in the working tree. Live site untouched; its worker still 404s.
