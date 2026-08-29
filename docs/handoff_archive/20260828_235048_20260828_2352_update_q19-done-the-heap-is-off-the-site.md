# Update — Q19 done. The heap is off the served site, 106 controls green, and I lost a piece of my own evidence on the way.

**2026-08-28 23:52 local · Code (background session)**
Version `588f1f6c-50a4-45a5-9b70-9c5a91a7b833`.

---

# THE HEAP IS GONE FROM WHAT A VISITOR GETS

    106 ok, 0 failed, 0 skipped, 0 NOT RUN, in 616s
    2 files uploaded

Verified from the SERVED bytes, not the build log:

    served 283,031 bytes  ef9be078c18f8de5
    provenance: 1,875 cig / 141 est / 4,044 anc = 6,060

    AEGS_Tiburon                     0 markers, 0 labelled cig
    RSI_Mantis                       0 markers, 0 labelled cig
    RSI_Hermes                       0 markers, 0 labelled cig
    MISC_Starlite                    0 markers, 0 labelled cig
    ORIG_m80                         0 markers, 0 labelled cig
    GLSN_Basher                      0 markers, 0 labelled cig
    ORIG_600i_Executive_Edition      0 markers, 0 labelled cig
    RSI_Aurora_Mk2                   0 markers, 0 labelled cig

And on the served page itself: **the Tiburon renders its model and draws zero
dots**, where until this deploy it drew seventeen in a clump and called them
CIG's own. The Buccaneer is unaffected - 337px of spread, dots where they belong.

**Absent beats confidently wrong**, and that trade is now made on the live
testing site rather than in the tree.

## The fleet-level cost, stated rather than buried

    markers   6,326 -> 6,060    (-266)
    cig       2,006 -> 1,875    (-131)

Fourteen hulls lost their CIG markers. That is the correct outcome - they were
never CIG's positions, the scale came off the wrong axis on models that measure
taller than they are long - but it IS a visible reduction and Sleven should hear
it as one rather than discover it.

## The baseline, re-taken with C1's condition checked FIRST

C1 asked that the list be read before the snapshot, and that any name outside the
orientation-refused set be treated as the finding rather than the baseline.

    14 distinct hulls: Tiburon, Khartu-al, San'tok.yai, Pitbull, Basher, Railen,
    Reliant Kore, Starlite, 600i Executive, M80, Aurora GS SE, Aurora Mk2,
    Hermes, Mantis

**Every one is from that set. No stranger appeared.** Restore verified
byte-identical (`ef9be078` both sides), control 16/0, all four known-bad inputs
still exiting 1.

---

# A MISTAKE IN MY OWN EVIDENCE, AND IT IS WORTH THE PARAGRAPH

I tried to measure exactly what the page lost by diffing the marker file I had
saved aside against the new one. It reported **0 hulls lost markers and 0 hulls
had fewer** - which is plainly false, since the Tiburon went from seventeen to
none.

**The copy I saved as "SHIPPED" was already the fixed build.** The sweep's own
`_verify_deploy_drift.py` rebuilt the payload at 22:23, after C1's 22:19 data
fix, so by the time I copied it aside at 23:37 the heap was already out of it.
My "before" was an "after".

**I nearly reported 0/0 as though nothing had changed.** The numbers above come
from the fleet totals and the served bytes instead, which I can actually stand
behind. The true pre-fix marker file is the one that was being served until
tonight and I no longer have it locally.

Two things follow: **the drift control rebuilding mid-sweep destroys evidence as
well as perturbing measurements**, which is another entry for the decision I
flagged at 22:25 and have not made; and a "before" copy is worth taking before
the first rebuild rather than after the third.

---

# Q19'S OPTIONAL PART: NOT TAKEN, WITH A REASON

C1 offered an emitter-side rule - group by `PortId.split(".")[0]`, take the
shallowest, drop a hull's CIG markers if its drawn dots span under 0.47 while the
model measures taller than long.

**`_verify_marker_spread.py` exits 0 right now.** C1's placement fix already
covers the M80 and the Starlite, so the rule would have nothing to catch today.
Adding a guard with no work to do is inventing one rather than needing one, and
the control will say if that changes. **Taken if it goes red.**

---

    Q1-Q6, Q8-Q19    done
    Q7               104 of 105 labelled; the last is _verify_panel_dismiss.mjs,
                     which OWNERS.md names as C1's
    testing site     588f1f6c, served bytes match the build
    live site        404, never run for real

Nothing committed since `1a1b4b7` - and that is now a very large tree.
