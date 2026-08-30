# FINDING — the payload changes itself at UTC midnight, and three separate guards are built on the assumption that it does not

    from    Code, 2026-08-30 (03:40 UTC / 2026-08-29 22:40 local)
    method  served bytes against local bytes, then the line that produces the difference
    status  REPORTED, not fixed. It needs a decision rather than a patch.

---

## 1. WHAT WAS SEEN

After the 106-of-106 sweep, the sweep receipt's payload fingerprint had moved
from `add0c868` to `0f4f5ff3` with nobody having built anything on purpose.

Every file in `testing/_deploy` was fetched from the served site and compared to
its local copy. **Nineteen of twenty are identical. `index.html` differs by two
lines:**

    -<title>Citizen Compass v0.4.0 - testing 2026-08-29</title>
    +<title>Citizen Compass v0.4.0 - testing 2026-08-30</title>
    -  <h1>... <span ...>testing 2026-08-29</span></span></h1>
    +  <h1>... <span ...>testing 2026-08-30</span></span></h1>

## 2. WHERE IT COMES FROM

`testing/_src/build_deploy.py:741`

    _stamp = _dt.datetime.now(_dt.timezone.utc).strftime('%Y-%m-%d')

**The build stamps the UTC date into the page.** That is a reasonable thing for
a build to do - a viewer can tell which build they are looking at. The problem
is not the stamp.

## 3. THE PROBLEM: THREE GUARDS ASSUME A REBUILD IS REPRODUCIBLE

**a. `_verify_deploy_drift.py` - mine.** Its whole proof of the assembled file
is *"REBUILD, and require the bytes not to move"*. **Across a UTC midnight the
bytes move on their own.** A sweep whose snapshot is taken before 00:00 UTC and
whose rebuild lands after it will report `index.html` as drifted, name it, and
preserve both versions as evidence of a defect that does not exist. It has not
happened yet only because tonight's sweep began after the rollover.

**b. `sweep_gate.py`'s payload fingerprint.** It is content-based, so it moves
with the stamp. **A clean sweep receipt is silently invalidated by the clock**
the first time anything rebuilds after midnight, and the gate then refuses a
payload nobody touched.

**c. The served site drifts from local every day at 00:00 UTC** - 19:00 local -
without anyone doing anything. Today's deploy shipped `2026-08-29`; the local
payload now says `2026-08-30`. **Neither is wrong and they do not match.**

## 4. WHY IT HAS NOT BITTEN BEFORE

The window is narrow: it needs a rebuild on one side of the boundary and a
comparison on the other. Both this project's rebuilds and its sweeps have mostly
run inside a single UTC day. **That is luck, not design**, and the sweep is now
on a scheduled task.

## 5. WHAT I AM NOT DOING

**Not removing the stamp** - it is the only thing on the page that says which
build a viewer has, and that is worth more than the convenience of a
reproducible byte comparison.

**Not making the drift control ignore the line.** An exemption is a hole, and
"ignore anything that looks like a date" is the widest kind. If the drift
control is to tolerate this it must be as narrowly declared as its other
injections - the stamp, at that offset, matching that pattern, and nothing else.

**Not changing it unilaterally**, because the honest options differ in what they
cost and the choice is not mine:

    A  declare the stamp as a fourth injection in _verify_deploy_drift.py,
       narrowly, the way the vendor marker and the trademark strip are
    B  make the stamp an input rather than a clock read - the build takes a
       date, and the same inputs give the same bytes
    C  accept the daily false red and re-deploy every morning

**A is what I would do**, and it is a small change to a file I own. Say so and
it is done.

## 6. HOW THIS WAS FOUND, BECAUSE THE ROUTE MATTERS

It was not found by a control. It was found because a fingerprint moved when
nothing should have moved it, and that was worth ten minutes rather than a
shrug.

**Two false trails on the way, both mine, both worth recording:**

- A first comparison reported EVERY file as differing. That was
  `sha256sum FILE` prefixing its output with a backslash when the path contains
  one, which shifted a `cut -c1-12` by a character. **Hashing through stdin
  removed the filename and the artifact with it.** A tool that changes its
  output format based on the input path is a hazard in any script that parses it.
- A second reported `index.html` and `loadout.html` as differing when they were
  simply not fetched: the worker answers `/loadout`, not `/loadout.html`, and
  returns 307. **An empty response hashes perfectly well** - `e3b0c442...` is
  the SHA-256 of nothing, and it will sit in a comparison looking like data.
