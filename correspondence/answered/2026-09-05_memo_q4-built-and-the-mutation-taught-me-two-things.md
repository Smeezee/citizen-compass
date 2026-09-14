# Memo

To:      Engineering
From:    Build
Date:    2026-09-05
Status:  Answered
Subject: Q4 built - and proving it could fail twice showed the control was wrong, not the fleet

`checks/_verify_model_plausible.py`. **RULE16: INDEPENDENT** - CIG's published
Length/Width/Height reach `loadout_data.gen.js` from the scunpacked record and
are derived from no `.glb` anywhere, so a wrong model cannot corrupt the figure
it is checked against.

All four assertions are in. **212 of 256 checked**, 44 have no published
dimensions and are counted as NOT CHECKED rather than passed.

## The mutation failed twice and both failures were mine

**First: the cap could not catch what it was written for.** I set AXIS_CAP at
2.00, per your "no axis more than ~2x". Doubling an axis on a hull whose axis
sat at 0.98 of published lands at **1.96** - under a strict `> 2.00`. The rule
written to catch a doubled axis could not catch a doubled axis.

I moved it to **1.75, chosen from the fleet rather than from taste.** Worst
per-axis ratio across 212 hulls: median 0.99, p90 1.21, p95 1.54, p98 1.68.

    cap 2.00 flags 3 hulls (1.4%)     cap 1.75 flags 4 (1.9%)
    cap 1.50 flags 12 (5.7%)          cap 1.30 flags 15 (7.1%)

1.75 sits above the 98th percentile of real hulls and below a doubling of a
typical one. One extra flagged hull, and the assertion gets its purpose back.

**Second, and this one is more interesting: my planted defect made the model
more correct.** The mutation doubled whichever hull came first - the 100i - and
was still not caught. The reason:

    100i published   19.0  12.0  5.0
    100i measured    17.49 11.43 2.73     height ratio 0.55
    after doubling   17.49 11.43 5.46     height ratio 1.09

**The 100i is 45% short on height, so doubling it moved it TOWARDS CIG's
figure.** A control that flagged that would have been wrong. The plant was the
defect, not the check.

The target is now chosen from the data: the hull agreeing with published on
every axis most closely - currently `Tiburon.glb`, within **0.2%** - so a
doubling there is unambiguous. **PROVEN: the planted model is flagged.**

Both mistakes are written into the file at the point they bit, because the
second one is a trap anybody re-proving this will walk into.

## It is NOT green on the fleet, and I am not widening anything to make it so

**31 models disagree with CIG's published figures beyond the stated tolerance.**
Your DONE-WHEN says green; it is not, and the honest answer is the list rather
than a bigger number.

    Clipper       49.5 vs 26.5   1.87x        Cyclone      5.7 vs 8.8   0.65x
    Basher        16.7 vs 13.7   1.22x        Cyclone AA   5.7 vs 8.8   0.65x
    C8/C8R/C8X    12.4 vs 16.0   0.77x        CSV-SM       6.1 vs 8.8   0.69x
    M80  worst axis 2.78x        Reliant Kore 2.47x        Fury 2.04x

Your own order says *"a named, reasoned exception rather than widening the
tolerance for all 256"*, and you are right - **but thirty-one exceptions is not
a list, it is a capitulation.** Some of these are surely published-data
problems rather than model problems, and I cannot tell which from here.

**So it is REPORT-ONLY by default**, same as the price control and for the same
reason: the runner discovers every `_verify_*.py` and the gate refuses an
unclean sweep, so a non-zero exit freezes every deploy - including unrelated
work - until 31 models are reconciled. `--strict` is one word and the ruling is
yours.

The 85X is the one named exception, with your hinge evidence written into it.

## What it does not claim

It is a net for gross error, not a proof of correctness. It still cannot catch a
doubling of an axis that started below 0.875 of published, because that lands
under the cap - and the file says so rather than implying completeness.

---

ANSWERS:

**Architecture, 2026-09-08.**

**Accepted and closed.** Q4 built, and proving it could fail twice showed the control was wrong rather than the fleet. That is hard rule 12 done properly and it is the standard for this project: a control nobody has made fail is not yet a control.
