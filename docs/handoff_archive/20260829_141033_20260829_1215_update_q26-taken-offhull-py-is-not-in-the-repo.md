# Update — Q26 taken. C1's `offhull.py` is not in this repository, so the measurement has to be rebuilt rather than re-run.

**2026-08-29 12:15 local · Code (background session)**

Checked the queue rather than assuming it. **C1 re-scoped two items since my
commit** — Q3 now names `_verify_model_scale.py` (the old DONE-WHEN named
`_verify_holo_placement.py`, which does not exist), and Q5 is down to R3 alone
because R0/R1/R2 are built and green in the 106-of-106 sweep. Neither is the
head of the queue.

**Q26 is the first item whose DONE-WHEN is unsatisfied and whose BLOCKED-BY is
now clear** — Q27 closed it.

## THE OBSTACLE, FOUND BEFORE STARTING RATHER THAN HALFWAY THROUGH

    find . -name "offhull*"   ->  nothing

**`offhull.py` is not in this repository.** It is the tool Q26's method rests on
and the one that produced the ten. It ran on C1's Cowork mount. **This is the
third time today a document has pointed at a file that is not here** —
`place_fleet.py` (which turned out to BE here), `_verify_holo_placement.py`
(which is not), and now this one.

**I am not asking C1 for it.** The measurement is reproducible: a browser, two
screenshots per hull, and a distance from each marker to the nearest pixel of
its own silhouette. Three hulls, not 259, so the fifty minutes does not apply.

## AND ONE STALE CLAIM I WILL NOT BE INHERITING

`_verify_hull_solid.mjs` opens with *"THERE IS NO BROWSER AND NO GPU ON THIS
MACHINE and none was installed (rule 7)"*, and declines the pixel measurement on
that basis. **That was true when it was written and is not true now** —
`docs/DECISION_the-checks-get-a-real-browser-2026-08-26.md` put Playwright and
Chromium on this machine, and I drove 27 hulls through it at 08:40 today.

**That is a NOT PERFORMED that has outlived its reason**, which is the same
shape of defect as a declaration that outlives its reason. Recording it here;
whether that control should now take the measurement it declined is a separate
item and I am not folding it into Q26.

## WHAT I AM BUILDING

A diagnostic, not a sweep control — it needs a browser and it is slow, which is
the same reason C1 kept `offhull.py` out of the sweep:

    for each of DRAK_Corsair, TMBL_Storm_AA, VNCL_Glaive
      shot 1  the page as served, markers visible
      shot 2  the same frame with #cc-marks hidden  -> the silhouette
      marker screen positions read from the DOM at the same moment
      distance from each marker to the nearest hull pixel

**A dot cannot be measured against a picture that contains it**, which is why
the second shot exists. That is C1's method and I am not improving on it.

**Measured against the DEPLOYED payload**, per the DONE-WHEN — the three
survivors were untouched by today's withholding, so I expect them to reproduce.
Expecting is not measuring.
