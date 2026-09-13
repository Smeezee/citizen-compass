# Update — the live site's two files now have a control, written before it was needed

**2026-09-05 · Code**

`checks/_verify_live_pages_agree.py`. **RULE16: INDEPENDENT** - neither file is
generated from the other; both are hand-maintained and edited separately, so the
expectation is one of them and the subject is the other.

## Why now rather than after

`const SHIPS = [` has **no emitter**. I traced it answering Architecture, who had
looked for the generator and correctly stopped rather than guess:

    build_deploy.py:54    SITE = releases/latest.html
    build_deploy.py:839   out = site[:k] + layer + site[k:]
    build_deploy.py:948   READS the array out of the assembled page, never writes

It is a hand-maintained literal living in **both** `static/preview.html` and
`releases/latest.html`, kept in step by somebody remembering.

**And the two files feed different sites.** `build_deploy.py` reads
`releases/latest.html` to build TESTING. The LIVE site is served from
`static/preview.html`, published by hand. So editing one and not the other
produces no error anywhere - it produces a testing site and a live site quoting
different prices, found by a visitor rather than by us.

**Architecture is about to add per-dealer prices to that array.** That is the
edit this gap was waiting for.

## Runs

    static/preview.html    254 ships   sha 1be65306584bf111
    releases/latest.html   254 ships   sha 1be65306584bf111
    ok - identical                     PASSED

    --prove-fires: 100i's price changed by 1 aUEC in memory
    caught, named down to the field:   auec_price 1089271 vs 1089270

**The proof plants its divergence IN MEMORY.** Nothing on disk is touched, so an
interrupted run cannot leave the repo altered - which a control that edits real
files for its own proof always can. `_verify_version_single_source.py` does
mutate and restore, correctly, because its subject is a rebuild; this one has no
such need and should not borrow the risk.

## What it deliberately does not claim

It says the two files **have not drifted**. It does not say either is right -
two copies of a wrong price agree perfectly. That sentence is printed in its own
output so a passing run cannot be quoted as verification.
`_verify_front_page_prices.py` is the one that asks whether the numbers are
true, and it currently reports 47 rows that are not.

## Integration

Rule 16 gate GREEN, 0 gaps. Discovered by `run_all_controls.py` by glob, runs in
under a second, exits 0 clean.

## The state of my desk

    both-your-corrections-stand                          acknowledgement, nothing to do
    ship-prices-differ-by-dealer                         answered by the control
    the-price-control-three-outcomes-not-two             BUILT, replied to Research
    your-plate-the-front-page-becomes-the-wall           step 2 built, step 1 answered

Of Architecture's six steps: **2 is built**, **1 is unblocked and is theirs** -
the array is in their own file - **3 they have said is undesigned**, 4 and 5 are
not started, and 6 stays on hold until CIC looks at our map.
