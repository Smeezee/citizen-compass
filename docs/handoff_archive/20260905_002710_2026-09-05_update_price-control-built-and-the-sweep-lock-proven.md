# Update — the price control is built, and the sweep lock is proven in a real race

**2026-09-05 · Code**

Sleven asked why I was not working. The answer was that I had been reading
`inbox/` and `docs/` and had never looked in `correspondence/open/build/`, where
**four memos addressed to my desk had been sitting since 2026-08-31.** One of
them was a finished design handed to me to build. That is now built.

## `checks/_verify_front_page_prices.py`

Reads the `SHIPS` array out of the **built** `testing/_deploy/index.html`,
because Research's structural point was right: `app/models.py` was already
correct, and a control against the schema or the seeded rows would have passed
every day while the site stayed wrong. The defect lives in the gap between a
correct model and the thing that renders.

**Their predictions against what it measured:**

    116 ships with a dealer and no source     116      exact
    16-ship negative-control fixture           16      exact
    A3 fires on 46                             47      they said 47 would be interesting
    A1 fires on the 400i                      yes

## A1 is 13 and only one of them is the defect A1 was written for

    400i             page 8,389,063   nearest off by 8,997
    12 other ships   off by 2 to 5 aUEC

**Every measured figure ends in a zero: Fleetyards rounds to 10 aUEC and our
page carries the finer number.** That is a source difference. The 400i is a
number that came from nowhere.

**No tolerance was added.** Rounding both sides to 10 would silence twelve real
disagreements AND still catch the 400i - which is what makes it tempting and
what makes it not mine to do quietly. Rule 17 wants the normalisation stated and
collision-checked first. Asked Research for the ruling.

## The negative control did its job

`F7C Hornet Mk II` was the one fixture ship flagged, and **A3 did not fire on
it** - so the assertion reads disagreement rather than the presence of several
dealers, which is exactly what Research was watching for. A1 fired on a 5 aUEC
rounding delta. It is in the fixture because the page shows two dealers and only
one is measured.

`--prove-clean` repairs the data in memory and requires zero failures. **It
passes** - the assertions read the data rather than always firing, which is the
half of rule 12 that gets forgotten.

## Report-only by default, and that was a deliberate refusal to decide

The runner discovers every `checks/_verify_*.py` and the deploy gate refuses an
unclean sweep, so a non-zero exit here **freezes every deploy, including
unrelated work**, until 47 rows are corrected.

That may well be worth blocking on. It is also a data correction belonging to
Architecture and Sleven, and freezing the deploy path in passing is not a
control author's call.

    default        report-only, findings printed in full, exit 0
    --strict       exit 1
    --prove-clean  exit 1 if repaired data still fails

Confirmed by run: 0, 1, 0 respectively. The runner discovers it and the sweep
stays green.

## The sweep lock, proven in a real race rather than a simulated one

While the guard was being tested a genuine sweep was running. A second one was
**refused, exit 2**, and it named both pids of the running sweep. With nothing
else sweeping it runs normally. That sweep finished **117 ok, 0 failed**.

## Correction carried forward

My earlier report that two sessions were sweeping was drawn from bad evidence -
`venv\Scripts\python.exe` is a launcher and spawns the base interpreter, so
every sweep shows as two processes, one "venv" and one "system". I told Sleven
and C1 that as fact. The guard now excludes its own ancestors and the mistake is
written into its comment.
