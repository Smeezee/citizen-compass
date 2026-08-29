# Update — Q12 (ORIGINAL) done: all 27 client-record hulls driven through a real browser, 27 of 27 draw their markers. And C1's newest finding says why it mattered.

**2026-08-29 08:40 local · Code (background session)**

    ---- 27 client-record hull(s), drawn on screen ----
    27 hull(s) driven; 0 have no ship row, 0 carry no marker
    ok   the client-record hulls were actually driven  (27 of 27)
    ok   and every one of them draws its markers  (27 of 27)

    GREEN - the markers on the page are on CIG's own coordinates.

**The 41 are 27 now** - the orientation refusal withdrew the rest overnight -
and the DONE-WHEN asks for the result by name, so: every one of
`AEGS_Eclipse`, `BANU_Defender`, `CRUS_Star_Runner`, `DRAK_Dragonfly`,
`MISC_Fury`, `ORIG_600i`, `ORIG_85x`, `TMBL_Nova`, `gama_tyilui`, `mrai_pulse`,
`mrai_pulse_lx`, the five `rsi_aurora_gs_*`, the four `crus_starfighter_*`, the
four `crus_starlifter_*`, `aegs_eclipse_bis2950`, `aegs_gladius_pir` and
`orig_600i_bis2951` was loaded in Chromium and asserted to draw.

## Why this was worth doing rather than declaring answered

`_verify_marker_provenance.py` proves every dot the page calls `cig` sits on its
own hull's CIG coordinate. **It cannot say whether that coordinate renders where
the mount is**, and no browser control had ever looked at these hulls.

**C1's off-hull audit, filed at 23:49 last night, makes that concrete.** Ten dots
float in empty space across four hulls - and the worst in the entire fleet, port
51 on the **Banu Defender at 38px clear of its own silhouette**, is a
client-record hull. These are also the hulls whose provenance was wrong for a
day.

## What it adds, and what it deliberately does not

It asserts the markers exist and are DRAWN. **It does not assert they are on the
hull** - that needs a silhouette and a second screenshot, which is what
`offhull.py` does in fifty minutes and a sweep cannot. A dot in the wrong place
still passes here; a hull that draws nothing does not. The label says so.

Cost: the control goes from 8.6s to **77s**. That is real and it is the price of
27 model loads in a browser. Still half of `_verify_broken_checker_end_to_end`'s
126s, which is the sweep's current ceiling.

## THE SECTION CAUGHT ITSELF TWICE BEFORE IT CAUGHT ANYTHING ELSE

I wrote a `check(checked > 0, ...)` guard - *"a section that drove nothing is not
a section that passed"* - and it earned its place immediately:

    FAIL the client-record hulls were actually driven  (0 of 27)
    ok   and every one of them draws its markers  (0 of 0)

**Twice.** Both times my key lookup went through `SHIPS[k].cls`, and the second
assertion sat there reporting green on an empty set beside it.

**`SHIPS` rows carry no `cls` field at all.** MARKS and SHIPS share a key
directly - the page itself reads `MARKS[shipId]`. Without the guard this section
would have shipped as two green lines that had looked at nothing, which is the
exact defect the whole suite exists against.

**It also explains something I had seen and not chased.** Every
`_diag_served_ship.mjs` run all week printed `"marksForClass": null`, because my
diagnostic used the same wrong indirection. The number was always null and I read
past it for two days.

And the Gladius block above it finds its own ship by a NAME SUBSTRING for the
same reason - its `SHIPS[k].cls === c` term has never matched anything. Not
touched: it works, and changing a passing control's lookup at 08:40 to tidy it is
how a green suite becomes a red one.

## Standing

    Q1-Q6, Q8-Q19 and Q12 (ORIGINAL)   done
    Q7                                 104 of 105; the last is C1's file

**Nothing on Code's queue is open.** What is outstanding is not queue work:

- **a very large uncommitted tree** - two days of it, since `1a1b4b7`
- **the decision I have flagged twice and not made**: the sweep's own
  `_verify_deploy_drift.py` rebuilds the artifacts other controls read, which
  perturbs measurements AND destroyed a "before" copy I needed last night
- **the RULE16 separator trap** - four occurrences, two people
- **going live** - Sleven's, and the worker still 404s
