# Update — `_verify_deploy_drift.py`: 11/1 -> 12/0. Rule 14's un-provenanced-write detector was red by default, and that is worse than absent.

**2026-08-27 23:23 local · Code (background session)** — second of the sweep's
14, same sitting as the deploy-guards one.

## Why this one mattered more than its count suggests

Section 3 is **the thing that makes an unauthorised write to `_deploy` loud**
(rule 14: where prevention is not available, detect on every build, fail the
deploy, name the files). It had been reporting three files as changed since this
morning.

**A section that is red by default cannot be read.** A genuine hand edit and the
noise print the same way, so the detector was effectively off while looking on.

## Two causes, both real, neither a hand edit

**1. A third injection nobody told the control about.** The disclosure CSS went
into the build this morning — one `_disc.css` substituted into four pages at
`/* CC_DISC_CSS */`. The control declared exactly two injections, vendor and
attribution, so keybinds/loadout/find were reported as no longer containing
their source.

Declared now, and **pinned as narrowly as the vendor marker**: the gap must be
`_disc.css` byte for byte. "Some CSS is there" would pass a page whose bars had
been restyled in `_deploy` only — precisely the change no source diff shows.

**2. `find.src.html` is the one source still saved CRLF.** The build writes
every page with `newline='\n'`, so the deployed file diverges at byte 15 and the
control reported the entire file as changed, blaming "attribution". True, and
the least useful true statement available.

Modelled as what it is — the build's own normalisation — **one direction only.
A CRLF in `_deploy` is now REPORTED**, because the build cannot produce one, so
something else put it there.

## And the ordering logic was rewritten, because a third marker broke its shape

`declared_transforms` enumerated the two possible orderings of vendor-vs-
attribution by hand. Three markers need six cases; four need twenty-four.

It now finds every injection **by position, in source order, however many there
are** — with the attribution point spliced in as a sentinel so a
position-appended block and a marker-substituted one are found the same way.
**A marker appearing twice now yields two gaps** instead of stranding the second
copy in a segment that could never match.

## Proven by behaviour, four plants, on a temp copy that touched nothing real

    plant  CSS hand-edited in _deploy   -> "not _disc.css byte for byte - it was edited in _deploy"
    plant  marker left unsubstituted    -> "the bars ship unstyled"
    plant  substituted with nothing     -> "replaced with nothing"
    plant  CRLF reintroduced            -> "which the build cannot produce ... something edited it after the build"
    restored                            -> CLEAN

Every new branch was **observed firing on input that must fail**, and the file
came back clean afterwards. `--self-test` still exits 1.

Section 5's existing plant test — the one that rewords hard rule 8's own
trademark line in `_deploy` only — still passes, so the older half of the
detector is unaffected.

## Where the sweep stands

Two of the 22:15 sweep's 14 are closed and both were controls that had gone
stale against the same day's deliberate changes, not regressions:

    _verify_deploy_guards.py   40/3 failed  ->  56/0   exit 0
    _verify_deploy_drift.py    11/1 failed  ->  12/0   exit 0

Both gained assertions rather than just being re-baselined. Nothing committed,
nothing pushed, live site untouched.
