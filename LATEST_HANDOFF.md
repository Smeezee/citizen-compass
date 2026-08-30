# LATEST_HANDOFF.md — Update #845 — 2026-08-29 11:02 PM

---

# CITIZEN COMPASS — LATEST HANDOFF

Copy/paste this whole file into a new AI conversation for instant context. It's regenerated automatically — always the most current snapshot available.

---

## CURRENT STATE (auto)

**Generated:** 2026-08-29 23:02:50 (auto-regenerated every time a file lands in inbox/ or this script runs — don't hand-edit this section)

**Project health score:** 35/100
- Data completeness: 0%
- Viewer progress: 50%
- Documentation: 100%

**Ships:** 2 complete viewers / 4 total (50%)
- Complete: arrow, cutlass-black
- In progress / not started: constellation-aquila, gladius

**Data layers:**
- data-layer: 119498 files (13787.21 MB)

**Scripts:** 53  |  **3D models:** 1137  |  **Docs:** 1402

---

## RECENT UPDATES (append-only, newest first)

### 2026-08-29 23:02:03 — 20260830_0030_update_q30-done-a-subset-can-no-longer-erase-a-sweep.md

# Update — Q30 done. A subset run can no longer erase a sweep, and the message that hid it for a day now names the path it actually wrote.

**2026-08-30 04:30 UTC / 2026-08-29 23:30 local · Code (background session)**

My call, made and built rather than restated: **fail-closed was not sufficient.**

    a full sweep   -> checks/.last_sweep.json          unchanged
    --only         -> checks/.last_sweep_partial.json
    --self-test    -> checks/.last_sweep_partial.json

**Self-test goes with it** because it inverts every expectation, so it is not a
sweep of the payload either - and until today a self-test run also took a good
receipt down with it.

## PROVEN, NOT ASSERTED

    routing        partial=F self_test=F  -> .last_sweep.json
                   the other three combinations -> .last_sweep_partial.json

    a 3-control --only run
      before  at 2026-08-29T22:26:57  partial=False  passed=106
      after   at 2026-08-29T22:26:57  partial=False  passed=106
      FULL RECEIPT BYTE-IDENTICAL - untouched
      partial went to .last_sweep_partial.json, 3 passed

    with the full receipt moved aside (rule 1: moved, not deleted)
      GATE EXIT 1, and it NAMES the partial while refusing to read it:
      "a subset is not a sweep - and it is kept separately so it cannot
       overwrite the real one."
      full receipt put back, byte-identical to before the test

**The gate did not change its mind about anything.** It reads the full receipt
and nothing else, so a partial still cannot masquerade as a sweep.

## THE MESSAGE THAT HID IT

`run_all_controls.py` printed `sweep_gate.RECEIPT` unconditionally, so a
`--only` run **announced the full receipt's path while writing over it.** The
message and the act disagreed, which is why the clobber went unnoticed until C1
happened to check. It now names the path it actually wrote, and says outright
when it did not touch the real one.

## ONE THING BROKE ON THE WAY AND THE EXISTING GUARD CAUGHT IT

My first patch aborted on an assertion **after** making its edit in memory, so
nothing reached disk - and the two later patches landed referring to a helper
that did not exist. The subset run then reported:

    SWEEP RECEIPT NOT WRITTEN: NameError: name 'receipt_path' is not defined
    The deploy gate refuses on a missing receipt, so this fails closed
    rather than quietly.

**Exactly as designed.** A receipt that cannot be written is reported and does
not silently look unreceipted-but-fine. I had not written that guard today and
it caught my own mistake within a minute.

## ALSO

`checks/.last_sweep_partial.json` added to `.gitignore` beside its sibling -
both are machine state and neither belongs in history. `.gitignore` has no
declared owner in `OWNERS.md`; the edit is one line adjacent to the existing
entry and is recorded here rather than done quietly.

## STANDING

    Q29, Q30   done
    Q3, Q5     the two still open, and both are older than today
    Q28        C1's
    draco3d    still not installed, still asked rather than assumed

Uncommitted: `checks/sweep_gate.py`, `checks/run_all_controls.py`, `.gitignore`.

### 2026-08-29 22:58:46 — 20260830_0020_update_taking-q30.md

# Update — taking Q30. My own answer to it changed once I did the same thing C1 did, so I am building the fix rather than re-stating the opinion.

**2026-08-30 04:20 UTC / 2026-08-29 23:20 local · Code (background session)**

Checked for updates: **C1 has changed nothing since `162231e`.** The queue is
where I left it, so I am taking the first open item that is mine and unblocked.

    Q26  withdrawn - C1's mesh distance supersedes it, and the Glaive is C1's
    Q28  BLOCKED-BY C1 by its own text
    Q29  done, verified in place at run_all_controls.py:239
    Q30  MINE, unblocked, DONE-WHEN is "your call"
    Q3   open - scale the 12 from model_scaled.glb
    Q5   open - R3 of the roadmap watcher

**Q30's DONE-WHEN is literally my call, and I have made it: fail-closed is not
sufficient.** C1 destroyed the full receipt with `--only`, reported it honestly,
and asked whether that was good enough. I said it might be. **Then I did exactly
the same thing within the hour**, running probe subsets while proving Q29. Two
sessions, same artifact, same day, both doing legitimate work.

"The gate catches it" is what you say about a defect you have decided to keep.

## THE SHAPE, AND IT IS RULE 14 INSIDE ONE SCRIPT

`sweep_gate.py`'s own docstring says **ONE writer** and it is right about the
writer. The defect is that **one path carries two kinds of run whose outputs are
not interchangeable**: a full sweep of 106 controls and a three-control subset
both write `checks/.last_sweep.json`, and the second silently destroys the first.

## WHAT I AM BUILDING

    a full sweep        -> checks/.last_sweep.json          (unchanged)
    --only              -> checks/.last_sweep_partial.json
    --self-test         -> checks/.last_sweep_partial.json

**Self-test goes with it for the same reason.** It inverts every expectation, so
it is not a sweep of the payload either, and the gate already refuses on it -
which means today a self-test run also destroys a good receipt.

**The gate does not change its mind about anything.** It reads the full receipt
only, so a partial can never masquerade as one. What changes is that a partial
no longer takes the full one down with it - and a full receipt that is still
valid for an unchanged payload survives, which is strictly better than forcing a
thirteen-minute re-sweep because somebody ran three controls.

**Rule 12 applies:** I will run a subset, confirm the full receipt is untouched
byte for byte, and confirm the gate still passes on it. A fix I cannot show
working is not a fix.

### 2026-08-29 22:51:22 — 20260830_0010_update_committed-and-pushed-162231e.md

# Update — committed and pushed as `162231e`. The injection fix and Q29 are in history; tree clean.

**2026-08-30 04:10 UTC / 2026-08-29 23:10 local · Code (background session)**

Sleven said commit and push, in this session, for this change. Rule 2 satisfied.

    162231e   20 files changed, 2,660 insertions, 423 deletions
    85e1d3b..162231e  main -> main
    local HEAD == origin/main == 162231e
    git status --porcelain    0 entries

## Verified after, not assumed

- **`_to_delete/` contributed 0 files.** Checked in the index before and in
  `git log -1 --name-only` after. Today's thirteen probes are all in there and
  none entered history.
- **No path outside the five expected roots.** Filtered the file list; empty.
- **The push landed** - `git fetch` and a hash comparison.

## THE DAY, IN FOUR COMMITS

    4710d30   the heap fix, the deploy gate, 295 ships photographed
    d1e60b4   the drift control stops writing to what it audits
    85e1d3b   three markers declared rather than forgotten, and deployed
    162231e   the sweep can say "I could not look", and the clock stops
              being a false red

## WHAT IS OPEN, HONESTLY

    Q26   withdrawn. C1's mesh distance is the measurement now.
    Q28   C1's to design - two placement writers, one containment gate
    Q30   open, and my answer changed to "not sufficient": --only should
          write its own receipt. Mine to fix on a word.
    the served site   still one date stamp behind local. Not broken, not
                      matching. A deploy would close it - the gate refuses
                      today only because the draco control is NOT RUN.
    draco3d           not installed. Asked properly rather than acting on a
                      conditional offer; rule 7 says downloaded code is data.

## AND ONE THING I WOULD SAY OUT LOUD

`checks/_verify_no_agent_traces.py` and
`docs/FINDING_the-public-source-reads-like-a-work-log-2026-08-29.md` arrived
from C1 today and are committed here unread by me beyond their names. **They are
about what the public source says**, which touches rule 8's territory even if it
is not legal text. Sleven should look at that one himself rather than take my
word that it is fine, because I have not formed one.

### 2026-08-29 22:50:32 — 20260830_0000_update_the-utc-stamp-is-declared-and-my-first-wiring-of-it-was-wrong.md

# Update — the UTC date stamp is a declared injection now, narrowed twice, and my first wiring of it compared a file against itself.

**2026-08-30 04:00 UTC / 2026-08-29 23:00 local · Code (background session)**

Option A, as Sleven asked. `build_deploy.py:741` stamps the UTC date into
`index.html` twice; across 00:00 UTC a rebuild is not byte-reproducible, and
section 4's whole proof is "rebuild and require the bytes not to move".

## DECLARED AS NARROWLY AS THE VENDOR MARKER AND THE TRADEMARK STRIP

Tolerated: **`index.html`, the literal text `testing <ISO date>`, the same
number of occurrences on both sides, every stamp in a file agreeing with every
other, and EVERY OTHER BYTE IDENTICAL.** Anything else is not this.

    stamp only, both occurrences   ACCEPTED
    stamp + a hand edit            refused - changed somewhere other than the stamp
    only ONE occurrence moves      refused - the stamps within one file disagree
    an extra stamp appears         refused - the stamp count changed: 3 -> 2
    identical files                refused - the stamps are not the difference
    a hand edit, no stamp move     refused - the stamps are not the difference

**The third row is a hole I opened and closed.** My first version tolerated one
stamp moving while the other did not - "only the stamp changed" is true of that,
and it is also a page telling a viewer two different things about which build
they are looking at. The build substitutes both from one `_stamp`, so they
cannot legitimately disagree.

## AND THE WIRING WAS WRONG BEFORE IT WAS RIGHT

The first version called the comparison **after** the `finally` that restores
`_deploy`. So it compared the snapshot against the file the snapshot had just
been restored onto - itself - and reported *"the stamps are identical"* on a
plant designed to make it fire.

**It only surfaced because the plant was supposed to go GREEN and went red.**
A test that expects a pass catches a class of defect that a test expecting a
failure never will: I would have shipped a declaration that could not fire and
believed it worked, because everything I had run until then was supposed to
fail. The comparison is now taken inside the try, before anything is put back,
and the comment at the site says why.

## PROVEN END TO END, NOT JUST IN A UNIT

    planted the 08-29 stamp        PASS + "DECLARED: the testing date stamp
                                   moved (2 occurrence(s), every other byte
                                   identical)"
    planted stamp + a hand edit    FAIL - "it is NOT the declared stamp: the
                                   file changed somewhere other than the stamp"
    clean run                      exit 0
    --self-test                    exit 1, correct

`testing/_deploy/index.html` was restored to the real build afterwards and the
hash checked against the copy taken before the plants: `0fe83cfc32c3` both
sides.

## STILL TRUE, AND NOT FIXED BY THIS

**The served site and the local payload still differ by that stamp** - the
deploy shipped `08-29`, local says `08-30`. This makes the drift control honest
about it; it does not make them match. And `sweep_gate.py`'s fingerprint is
still content-based, so a clean receipt still goes stale at UTC midnight.
Both are in the finding.

### 2026-08-29 22:30:57 — 20260829_1250_update_q29-done-and-the-payload-changes-at-utc-midnight.md

# Update — Q29 is built and proven in both modes, the new draco control now reads as NOT RUN instead of FAIL, and chasing a moved fingerprint found that the payload rewrites itself at UTC midnight.

**2026-08-30 03:50 UTC / 2026-08-29 22:50 local · Code (background session)**

## Q29 — DONE

    exit 0          PASSED
    exit 2          NOT RUN, with the control's own reason printed
    anything else   FAILED

    106 ok, 0 failed, 0 skipped, 1 NOT RUN, in 778s
    NOTRUN _verify_marker_mesh_distance.py  exit 2  NOT PERFORMED - NO_DRACO...

**Nothing was made to pass.** The gate still refuses, in its own words:

    sweep : the last sweep of THIS payload was not clean.
            NOT RUN  _verify_marker_mesh_distance.py
            A control that could not be run is counted against the
            sweep, never as a pass.
    GATE EXIT 1

**Proven in both modes, probes parked in `_to_delete/probes-20260829/`:**

    NORMAL     exit 0 -> ok     exit 1 -> FAIL     exit 2 -> NOTRUN + reason
    SELF-TEST  exit 2 -> NOTRUN

**The self-test half is the one that mattered.** There `ok = (code != 0)`, so
before this change a control that COULD NOT LOOK was counted as having CAUGHT
the planted defect — the silent success this suite exists against, wearing the
colours of the test meant to find it.

## AND I DID Q30 TO MYSELF WITHIN THE HOUR

My `--only` probe run overwrote the full receipt, exactly as C1's did. It failed
closed and the gate caught it — **and I have changed my mind about whether that
is sufficient.** Two sessions destroyed the same artifact the same day, both
doing legitimate work. "The gate catches it" is what you say about a defect you
have decided to keep. **A subset run should write its own receipt somewhere
else.** Mine to fix if Sleven wants it.

## THE PAYLOAD REWRITES ITSELF AT UTC MIDNIGHT

The sweep's fingerprint moved from `add0c868` to `0f4f5ff3` with nobody having
built anything. All twenty payload files were fetched from the served site and
compared. **Nineteen identical. `index.html` differs by two lines, and both are
a date.**

    -testing 2026-08-29        build_deploy.py:741
    +testing 2026-08-30        _stamp = datetime.now(timezone.utc).strftime(...)

**Three guards assume a rebuild is reproducible and it is not:**

- **`_verify_deploy_drift.py`, mine** — its entire proof of the assembled file
  is "rebuild and require the bytes not to move". A sweep straddling 00:00 UTC
  will report a drift that does not exist. It has not happened yet only because
  tonight's sweep began after the rollover.
- **`sweep_gate.py`'s fingerprint** — content-based, so the clock silently
  invalidates a clean receipt.
- **The served site** — today's deploy shipped `08-29`, local now says `08-30`.
  Neither is wrong and they do not match.

`docs/FINDING_the-payload-changes-at-utc-midnight-2026-08-30.md`, with three
options. **I would declare the stamp as a fourth narrow injection in the drift
control**, the way the vendor marker and trademark strip already are. Small
change, my file, not made without a word.

## TWO FALSE TRAILS ON THE WAY, BOTH MINE

- A first comparison said EVERY file differed. `sha256sum FILE` prefixes its
  output with a backslash when the path contains one, shifting `cut -c1-12` by a
  character. Hashing through stdin removed the filename and the artifact.
- A second said two pages differed when they had simply not been fetched — the
  worker answers `/loadout`, not `/loadout.html`, and returns 307. **An empty
  response hashes perfectly well**: `e3b0c442...` is the SHA-256 of nothing and
  it sits in a comparison looking exactly like data.

## STANDING

    Q26  withdrawn - my measurement was a photograph too
    Q29  done
    Q30  open, and my answer changed: not sufficient

**Uncommitted:** `checks/run_all_controls.py`, `checks/_diag_offhull.mjs`, the
UTC finding. **Not done:** `npm i draco3d`, which I have asked about properly
rather than acting on a conditional offer.

### 2026-08-29 22:12:08 — 20260829_1245_update_q26-withdrawn-taking-q29.md

# Update — my Q26 measurement is withdrawn, C1's mesh distance supersedes it, and I am taking Q29 because a control written today is already printing FAIL for saying "I could not look".

**2026-08-29 12:45 local · Code (background session)**

## WITHDRAWN, WITHOUT ARGUMENT

**The old off-hull list came from photographs and was wrong in both
directions, and mine was the same method.** `DRAK_Corsair` 80/93/94 and
`TMBL_Storm_AA` 4 are FINE against the mesh - Storm AA port 4 is the second
CLOSEST of its four. **I reported six off-hull dots this morning and four of
them are not off the hull.**

My instrument was not the problem - I found and fixed two contaminations in it.
**The measurement was.** A silhouette says where a dot is against a picture of
the hull; it cannot say where the dot is against the hull. C1's control decodes
the mesh and measures against vertices, which is a different claim and a better
one. **I am not defending the pixel numbers and the three "new" dots I raised
are withdrawn with them.**

The one I got right is the one that matters least: `VNCL_Glaive` 43. And the
real finding is the pair, not the port -

    43 and 44 - "Gun nose left" / "Gun nose right", 0.007 units apart,
    a mirrored pair, and the old test flagged ONE and passed the other.

**That is the whole indictment of the old test and it is not something a
photograph could have told anyone.**

**`GAMA_Tyilui`: 15 markers flagged, worst at 28% of hull length, never
mentioned anywhere in this repo before today.** 60 flagged on 20 hulls across
5,800 markers.

**The Glaive ruling is C1's and none of this is mine to fix.**

## WHAT IS MINE, AND IT ARRIVED ON SCHEDULE

    $ venv/Scripts/python.exe checks/_verify_marker_mesh_distance.py
    NOT PERFORMED - NO_DRACO. The hull meshes are Draco-compressed and cannot
    be read without it, so no marker was measured.
    EXIT 2

**Verified myself rather than taken from the note.** That is exactly right and
my sweep will print it as `FAIL ... exit 2`.

**Q29 predicted this and it landed on a control written the same day.** A
brand-new, correctly-written control whose first appearance in a sweep is a
false red. Read that output cold and you go looking for a defect in the newest
thing in the repo, which is where you would look anyway.

## WHAT I AM BUILDING

    exit 0   PASSED
    exit 2   NOT RUN, with the control's own reason printed
    anything else   FAILED

**NOT RUN still counts against the sweep and the deploy gate still refuses on
it** - `sweep_gate.py` already says so in as many words: *"a control that could
not be run is counted against the sweep, never as a pass."* **The only thing
changing is which true sentence gets printed.** If I make either state pass I
have built the silent success this suite exists against.

Then the DB-backed controls, which currently leak a traceback where they should
say what is absent.

## ONE THING I AM NOT DOING WITHOUT ASKING PROPERLY

**`npm i draco3d`.** Sleven has offered it and constrained it - not into a
shared `package.json` without saying so. **Rule 7 says downloaded code is data
and is not to be imported or run**, and a decode library imported by a control
is exactly that. Playwright got here through a dated `docs/DECISION_*`. I will
ask for this one properly rather than treat a conditional offer as the
authorisation, and Q29 does not depend on it: the honest NOT PERFORMED is the
correct state whether or not draco is ever installed.

### 2026-08-29 14:20:44 — 20260829_1230_update_q26-measured-and-there-are-more-than-three.md

# Update — Q26 measured against the deployed payload. The three survivors are real, there are SIX not three, and my instrument was wrong twice before it was right.

**2026-08-29 12:30 local · Code (background session)**

`offhull.py` is not in this repository, so the method was rebuilt:
`checks/_diag_offhull.mjs`. Diagnostic, not a gate - it needs a browser, which
is why C1 kept theirs out of the sweep too.

## THE RESULT, AGAINST THE SITE AS SERVED

    DRAK_Corsair    7 of 15 dots on the hull exactly
      port 94  37px  7.05% of hull span      port 80  18px  3.43%
      port 70  24px  4.57%                   (+ four under 15px)
      port 93  19px  3.62%
    TMBL_Storm_AA   2 of 5
      port 1   17px  2.96%                   port 4   16px  2.79%
    VNCL_Glaive     6 of 9
      port 43  29px  5.33%                   port 44  18px  3.31%

**C1's three all reproduce.** `DRAK_Corsair` 80/93/94, `TMBL_Storm_AA` 4,
`VNCL_Glaive` 43 - every one still off the hull on the payload deployed an hour
ago.

## BUT THERE ARE THREE MORE AT C1'S OWN THRESHOLD

C1's audit named only dots at 15px and above. Applying that same cut to this
measurement finds **three the fleet-wide audit did not list**:

    DRAK_Corsair   port 70   24px
    TMBL_Storm_AA  port 1    17px
    VNCL_Glaive    port 44   18px

**Six, not three.** I am not claiming C1's audit was wrong - it measured 259
hulls at one framing and this measured three at another, and I cannot re-run
theirs. What I can say is that on the served payload these six are off the hull
and three of them are not on anyone's list.

## THE NAMED CAUSE, AND IT IS C1'S HYPOTHESIS CONFIRMED BY EYE

The ringed screenshot shows it: the Corsair's four sit in open space **above the
tail fin, above the wing root, and below the fuselage** - adjacent to the hull,
not on it. Inside the model's axis-aligned box, outside its mesh. **The box is
not the hull**, exactly as C1 said.

**I have not widened the acceptance test and will not.** A containment gate that
passes these is not a gate with the wrong number in it; it is a gate measuring
the wrong shape.

## MY INSTRUMENT WAS WRONG TWICE, AND BOTH WOULD HAVE SHIPPED A WRONG ANSWER

**1. It counted the viewer's own chrome as hull.** "Any pixel that is not the
field colour" includes the Display button, Start spin, the mounts pill and the
drag-to-rotate hint. **A dot over the Display button would have measured as ON
THE HULL.** Caught because the hull's bounding box came back 788px wide on all
three ships - the frame, not the ship - which is impossible. Then confirmed by
looking at the picture rather than the number.

**2. A faint ring on the canvas's own rounded border survived that fix**, about
ten pixels in the outermost column, still holding the bounding box at full
width. Now only the largest connected blob counts as the ship.

Spans went 788 / 788 / 788 -> **525 / 574 / 544**. The distances did not move,
which is luck rather than vindication: for these particular dots the ship was
always nearer than the contamination. It would not always be.

**And a third thing, which is why C1's numbers and mine differ at all:** a pixel
distance is not a property of the ship, it is a property of how big the ship
happens to be drawn. `VNCL_Glaive` port 43 is 16px in C1's audit and 29px here,
and neither is wrong. Every distance is now also reported as a **fraction of the
hull's own on-screen span**, which is comparable between runs.

**Threshold sensitivity checked before trusting any of it:** 6, 12, 18, 30, 50
all give the same ports at the same distances. The answer does not depend on
where the line is drawn.

## STANDING

    Q26  measured. The three are six, the cause is named, and the fix is not
         mine to design - a containment gate that uses the mesh rather than the
         box is C1's pipeline.

New file: `checks/_diag_offhull.mjs`. Probes parked in
`_to_delete/probes-20260829/`. Nothing committed.

### 2026-08-29 14:10:33 — 20260829_1215_update_q26-taken-offhull-py-is-not-in-the-repo.md

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

### 2026-08-29 13:41:02 — 20260829_1205_update_committed-and-pushed-85e1d3b.md

# Update — committed and pushed as `85e1d3b`. Q27 and the deploy are in history; working tree clean.

**2026-08-29 12:05 local · Code (background session)**

Sleven said commit and push, in this session, for this change. Rule 2 satisfied.

    85e1d3b   14 files changed, 1,232 insertions, 412 deletions
    d1e60b4..85e1d3b  main -> main
    local HEAD == origin/main == 85e1d3b
    git status --porcelain    0 entries

## Staged by path, never `git add -A`

    checks/     _verify_child_markers.py (Q27), and C1's _verify_marker_census.py
                and marker_census.json
    build_hardpoint_overlay.py
    docs/       two of C1's findings, CURRENT-STATE.md, three handoff updates
                and the running log
    NEXT.md, LATEST_HANDOFF.md

## Verified after, not assumed

- **`_to_delete/` contributed 0 files** - checked in the index before and in
  `git log -1 --name-only` after. Today's eight probes are all in there and none
  entered history.
- **No path outside the five expected roots.** Filtered the file list; empty.
- **The push landed** - `git fetch` and a hash comparison, not the push's own
  output.

## THE DAY, IN THREE COMMITS

    4710d30   the heap fix, the deploy gate, 295 ships photographed
    d1e60b4   the drift control stops writing to what it audits
    85e1d3b   three markers declared rather than forgotten, and deployed

## STANDING

    Q21, Q22, Q23, Q24, Q25, Q27      done
    Q26   unblocked - the three survivors, against a payload now deployed
    Q28   C1's to design. Not mine.
    Q29   open. The sweep cannot say "I could not look".
    Q30   open, and it is a question for Sleven rather than work:
          `--only` overwrites the same receipt a full sweep writes. It failed
          CLOSED and the gate caught it. Whether fail-closed is sufficient, or
          whether a partial should write somewhere else, is a call not a fix.

**The testing site is current and verified on its served bytes.** Going live
remains Sleven's and is untouched.

**Next, unless told otherwise: Q29.** Two controls already exit 2 to say a
resource was absent and both print as FAIL. Nothing about it weakens a gate -
both states still count against the sweep - and it stops a clean machine from
looking like twenty defects.

### 2026-08-29 13:38:45 — 20260829_1200_update_q27-done-and-the-testing-site-is-deployed-and-verified.md

# Update — Q27 done with declared exceptions, the sweep is 106 of 106, and the testing site is deployed and verified on the served bytes.

**2026-08-29 12:00 local · Code (background session)**

## Q27 — DECLARED, NOT RE-BASELINED

Three exceptions in `_verify_child_markers.py`, each declaring the WHOLE
transition rather than just a port name, printed on every run:

    BANU_Defender 50   [-0.30751, 0.01049,  1.32494] cig  ->  REMOVED
    BANU_Defender 51   [ 0.30751, 0.01049,  1.32494] cig  ->  REMOVED
    MISC_Hull_C   34   [-0.0,    -0.10429, -1.27827] cig
                    -> [-0.00408, 0.00157, -1.00356] est

**I measured all three against the real data before writing them down** and they
match C1's table exactly. The third is declared as a DEMOTION, not a removal -
the mount kept its marker, the CIG position was withheld, and the page now says
`est`. Calling that "removed" would record the wrong event.

**A port name alone would have excused any future change to those mounts**,
including a second real regression landing on the same one. Both ends are
asserted.

## PROVEN THREE WAYS, RULE 12

    undeclared loss     FAIL  got=['Aegis Gladius:9']    the list does not blanket-excuse
    wrong transition    FAIL  x2 - unmoved AND stale     two independent alarms
    stale declaration   FAIL  got=['AEGS_Gladius:1']     a declaration nothing fires is fiction

All three probes are in `_to_delete/probes-20260829/`, never deleted.

## THE SWEEP AND THE GATE

    106 ok, 0 failed, 0 skipped, 0 NOT RUN, in 706s
    sweep_gate --check testing/_deploy
      106 control(s) green against this exact payload (2026-08-29T13:35:46)
      GATE EXIT 0

**The gate was refusing C1's `--only` receipt, exactly as Sleven said** - 9
controls, 3.7s, `partial: true`, naming a child-markers red that no longer
existed. Not the payload.

## DEPLOYED, AND VERIFIED ON THE SERVED BYTES RATHER THAN ON EXIT 0

    Uploaded 1 of 1 asset   + /loadout_marker.gen.js
    https://citizencompasstesting.citizencompass-contact.workers.dev
    Version a0f092a4-89f4-407e-b061-6b951ee3ad3d

**One file changed, and it is the fore/aft withholding.** The other 524 were
already uploaded.

The deploy script says in as many words that exit 0 is not proof, so:

    /                        HTTP 200    431,674 bytes
    /models/Hammerhead.glb   HTTP 200  3,608,636 bytes
    /loadout_marker.gen.js   HTTP 200    282,961 bytes
    served sha256 == local sha256   (2536dbdbe37aec05)
    index carries id="cc-kb" and id="cc-panel"

**And the three ports, read off the file the site is actually serving:**

    259 hulls, 6058 markers
    BANU_Defender port 50   GONE
    BANU_Defender port 51   GONE
    MISC_Hull_C   port 34   ['34', -0.00408, 0.00157, -1.00356, 'est']

The three deployed-site controls - `_verify_find_deployed.mjs`,
`_verify_deployed_links.mjs`, `_verify_picker_deployed.mjs` - are all green
against the new deploy.

**The site is no longer on 04:47.**

## WHAT THAT CLOSES

    Q21  DONE - the deploy gate passes
    Q27  DONE - declared exceptions, baseline untouched
    Q26  UNBLOCKED - the three survivors can now be measured against a
         payload that is actually deployed

Uncommitted: `checks/_verify_child_markers.py` and today's updates. Nothing has
been committed since `d1e60b4`.

**Not started: Q26, Q28 (C1's), Q29, Q30.** Q29 is the one I would take next -
the sweep cannot say "I could not look", and two controls already exit 2 trying.

### 2026-08-29 13:22:11 — 20260829_1145_update_q27-taking-the-declared-exception-list.md

# Update — Q27 taken. Declared exceptions, not a re-taken baseline, and C1's reasoning for that is right.

**2026-08-29 11:45 local · Code (background session)**

Sleven said go, Q27 first. Filing before I start, rule 13.

**C1 asked me to choose and said it would not argue twice. I am not choosing
differently: the declared-exception list is correct and re-taking the snapshot is
not.** Absorbing a loss into a baseline is the exact failure
`_verify_marker_census.py` exists to prevent, and it would be the same failure
in my file. A baseline re-taken quietly and one re-taken on purpose look
identical in six weeks; three declared entries that print on every run do not.

**And C1 is right that the red control produced the day's best evidence.**
Section 6 says 244 hulls changed and names exactly three moved markers. A
fleet-wide change to the containment rule moved three markers and nothing else,
with the four pinned negative controls holding. That is worth more than the pass
would have been.

## THE CORRECTION I AM ACCEPTING

Q21's DONE-WHEN said `MISC_Hull_C` port **2**. It is port **34**, the nose
turret. Port 2 is at fore/aft -0.97267, inside the box, and was never an
escapee. **I spent time hunting a port with nothing wrong with it.** C1 has
owned that. What I will note for myself: I reported "port 2 PRESENT" as a
finding without asking whether the number in the order was right, which is the
same trust I would not extend to a check's own output.

## WHAT I AM BUILDING

Three declared exceptions in `_verify_child_markers.py`, each carrying its
reason and printed on every run:

    BANU_Defender 50   cig -1.32494 fore/aft  -> REMOVED
    BANU_Defender 51   cig  1.32494 fore/aft  -> REMOVED
    MISC_Hull_C   34   cig -1.27827           -> demoted to est -1.00356

**The third is not a removal and must not be declared as one.** The mount kept
its marker; the CIG position was withheld and it fell back to a name-derived
estimate the page now labels `est`. A control that calls that "removed" would be
recording the wrong event.

Rule 12 applies: the list has to be proven not to hide a fourth. I will plant a
loss that is NOT declared and confirm the control still goes red.

### 2026-08-29 10:35:59 — 20260829_1120_update_q23-committed-and-pushed-d1e60b4.md

# Update — committed and pushed as `d1e60b4`. 23 files, the drift fix and today's docs, tree clean. Nothing went to the live site and nothing went to the testing site either.

**2026-08-29 11:20 local · Code (background session)**

Sleven said commit and push, in this session, for this change. Rule 2 satisfied.

    d1e60b4   23 files changed, 2,783 insertions, 796 deletions
    4710d30..d1e60b4  main -> main
    local HEAD == origin/main == d1e60b4
    git status --porcelain    0 entries

## Staged by path, never `git add -A`

    checks/            _verify_deploy_drift.py, rule16_baseline.txt,
                       _verify_panel_dismiss.mjs
    testing/_src/      build_deploy.py, loadout_marker.gen.js
    build_hardpoint_overlay.py
    docs/              the DECISION, C1's ERRATUM, the proposal, 9 handoff
                       updates and the running log
    NEXT.md, OWNERS.md, LATEST_HANDOFF.md

## Verified after, not assumed

- **`_to_delete/` contributed 0 files.** Checked in the index before the commit
  and in `git log -1 --name-only` after. The probes from this morning - three
  rule-16 label probes and two restore probes - are all in there and none of
  them entered history.
- **No path outside the eight expected roots.** Filtered the commit's file list;
  came back empty.
- **The push landed** - `git fetch` and a hash comparison, not the push's own
  output.

## ONE FILE IN THIS COMMIT IS A PAYLOAD SOURCE, AND IT IS THE FORE/AFT CHANGE

`testing/_src/loadout_marker.gen.js` moved by 4 lines - **that is C1's fore/aft
withholding, landing in a tracked file for the first time.** It is what Q23 asks
for. `testing/_deploy` is gitignored and is not in this or any commit.

## Q23'S BLOCKER, STATED RATHER THAN IGNORED

NEXT.md has Q23 **BLOCKED-BY Q21**, and Q21 is 2 of 3 - `MISC_Hull_C` port 2 is
still in the payload. **Sleven told me to commit anyway, in this message.** The
block was procedural rather than technical: nothing here depends on Q21 finishing,
and leaving a day of work uncommitted to honour an ordering constraint would have
been the worse call. Recording the deviation because it IS one.

## C1's FILES CARRIED, NOT EDITED

`OWNERS.md`, `NEXT.md`, `_verify_panel_dismiss.mjs`, `build_hardpoint_overlay.py`
and the proposal are in this commit exactly as C1 left them. **The overlay's
comment fix landed with a duplicated "So. So"** - C1's file, C1's to tidy, and I
am not touching it to make a diff look neater.

## STANDING

    Q22, Q24, Q25   done
    Q21             2 of 3
    Q23             done as of this commit
    Q26             blocked by Q21

**The deploy is still refused** by `sweep_gate.py` on `_verify_child_markers.py`
and `_verify_marker_census.py`. Both baselines are C1's. The served site stays on
04:47 until C1 clears them - and the gate is not going to be weakened to get past
its own finding.

### 2026-08-29 10:34:19 — 20260829_1110_update_q25-done-the-separator-is-three-characters-and-a-lowercase-label-is-invisible.md

# Update — Q25 done. The separator was never one character, the en dash is a worse trap than the comma, and a lowercase label is invisible to the gate.

**2026-08-29 11:10 local · Code (background session)**

`docs/DECISION_the-rule16-label-format-2026-08-29.md`, 149 lines. C1's
instruction was *"write what the gate does, not what it should do — if they
differ, that difference is the finding."* They differ in three places.

## 1. THE SEPARATOR IS THREE CHARACTERS

    LABEL = re.compile(r"RULE16:\s*(INDEPENDENT|UNPROVEN)\s*[-—:]\s*(.+)")

**Hyphen, em dash AND colon all pass.** `RULE16: UNPROVEN: reason` is a valid
label and always has been. Every error message the gate prints says *"with the
separator"* and shows only the hyphen, so **the rule as communicated has been
narrower than the rule as enforced since adoption.** Not a defect — a
documentation gap, and the document is the fix.

## 2. THE EN DASH IS WORSE THAN THE COMMA EVER WAS

    ACCEPTED   RULE16: UNPROVEN — reason      em dash  U+2014
    MALFORMED  RULE16: UNPROVEN – reason      en dash  U+2013

**One pixel apart, treated oppositely.** The comma cost two people an hour and a
comma is at least visible. The gate prints the offending line back in its error —
where an en dash looks correct. Anyone who hits this should suspect the character
before the code.

## 3. THE ONE ACTUAL HOLE, AND I FOUND IT BY TESTING RATHER THAN READING

**A lowercase label is not seen as a label at all.**

    checks/_verify_zz_probe_lowercase.py
      -> "a NEW check with no RULE16 label"

The regex is case-sensitive and **so is the fallback that detects a MALFORMED
label** — it greps for the literal `RULE16`. So `rule16: unproven - ...` produces
neither a match nor a malformed report. It is classified **unlabelled**.

**And `rule16_baseline.txt` excuses unlabelled files.** The baseline is matched
on the reason string `"no RULE16: line"` (`_verify_rule16_labels.py:167`), which
is precisely what a lowercase label produces. A baselined file carrying a
lowercase label would be **silently excused while appearing to have declared
itself.**

It fails today only because the debt list is closed and a NEW unlabelled check is
refused outright — **a second guard catching it, not the label logic working.**

**Not fixed.** Q25 was to record behaviour, and changing the gate would make the
document stale the day it was written. The fix is one word — case-insensitive
loose detection so a lowercase label reports MALFORMED rather than absent — and
it is mine when it is wanted.

## HOW EACH ROW WAS ESTABLISHED

Every acceptance row was run through the gate rather than reasoned about, and the
three interesting ones — colon, en dash, lowercase — were run **end to end as
real files in `checks/`**, so the gate discovered and classified them the way it
would any control. All three are parked in `_to_delete/probes-20260829/`, and the
suite is back to 105 of 105, 0 unlabelled, 0 malformed, GREEN.

## STANDING

    Q22  verified myself, 105 of 105
    Q24  done - the comment, plus a second stale premise (numpy IS installed)
    Q25  done - this
    Q21  2 of 3. MISC_Hull_C port 2 still in the payload.
    Q26  blocked by Q21
    Q23  blocked by Q21

**The deploy is still gated** on `_verify_child_markers.py` and
`_verify_marker_census.py`, and both baselines are C1's to clear. Nothing I own
is in the way of it.

### 2026-08-29 10:23:25 — 20260829_1055_update_i-was-wrong-about-q21-the-withholding-did-arrive-and-the-deploy-is-gated.md

# Update — I was wrong an hour ago: the withholding DID reach the marker file. Q21 is 2 of 3, the deploy is gated on two red controls, and both baselines are C1's to clear.

**2026-08-29 10:55 local · Code (background session)**

## THE CORRECTION, FIRST

At 10:45 I filed that the fore/aft withholding *"cannot reach `loadout_marker.gen.js`
through any build"* and that *"there is no port 50 or 51 in it to remove, and
there never was."*

**The second half was wrong and the first half was the wrong conclusion from a
true measurement.**

    BANU_Defender  port 50   GONE
    BANU_Defender  port 51   GONE
    MISC_Hull_C    port 2    PRESENT

**Ports 50 and 51 were removed — at C1's 09:19 regeneration, which is before the
09:47 baseline I measured from.** So my before AND my after both already had them
gone, my build was correctly a no-op, and I read "my build changed nothing" as
"the change can never arrive." Those are not the same statement and I should not
have made the second one.

**What survives from that update:** the marker pipeline genuinely does not read
`data-layer/derived/hardpoint-placement/` — one grep hit, line 1560, model
substitutions. The withholding reaches the payload through
`holo-hardpoints-align/`, regenerated at 09:19. Both facts are true; I joined
them into a false conclusion.

## SO Q21 IS 2 OF 3, NOT 0 OF 3 AND NOT DONE

`MISC_Hull_C` port 2 is still in the payload. That is the one named port the
09:19 run did not take out, and I do not know why — it is C1's pipeline and I am
not guessing at it.

## THE SWEEP, AND IT IS THE FIRST CLEAN MEASUREMENT

    104 ok, 2 failed, 0 skipped, 0 NOT RUN, in 677s

**This is the first sweep in this repo that could not be perturbed by its own
drift control.** Nothing rebuilt underneath it; every control measured the same
payload. That is what this morning's work was for.

## THE TWO REDS ARE THE WITHHOLDING ITSELF, ARRIVING AT BASELINES THAT PREDATE IT

    _verify_child_markers.py   every marker that existed before is still there
                               got ['Banu Defender:50', 'Banu Defender:51',
                                    'MISC Hull C:34']
    _verify_marker_census.py   REFUSED - BANU_Defender 10 -> 8

**Neither is a defect. Both are controls correctly refusing a loss nobody has
declared to them yet.** That is exactly what they are for, and I am not going to
make them quiet.

## AND I AM NOT CLEARING EITHER, BECAUSE NEITHER IS MINE TO CLEAR

    _verify_marker_census.py    C1's in OWNERS.md
    checks/marker_census.json   C1's in OWNERS.md
    _verify_child_markers.py    MINE by the default clause - but its baseline is
                                data-layer/derived/holo-hardpoints/
                                loadout_marker.pre-C1-20260829.js, and C1
                                CLAIMED that directory this morning.

**So the control is mine and the file it compares against is C1's.** Re-taking
that snapshot is a write into C1's path, and the whole point of this morning's
rule 14 work was to stop doing exactly that. C1 sets the condition for re-taking
it anyway — the pinned four checked first — and C1 is the one who can say
whether losing `MISC Hull C:34` was intended.

## THE DEPLOY IS REFUSED, AND I ASKED THE GATE RATHER THAN ASSUMING

    $ python checks/sweep_gate.py --check testing/_deploy
    sweep   : the last sweep of THIS payload was not clean.
              FAILED   _verify_child_markers.py
              FAILED   _verify_marker_census.py
    GATE EXIT 1

**Nothing was uploaded and I did not try to.** The served site stays on 04:47
until the two reds are resolved by their owner. Weakening the gate to ship past
its own finding is the one thing that is never on the table.

## WHAT I NEED FROM C1, SPECIFICALLY

    1  declare the BANU_Defender 10 -> 8 loss in marker_census.json, or say it
       is not intended
    2  say whether MISC Hull C:34 going was intended, and why port 2 stayed
    3  authorise a re-take of loadout_marker.pre-C1-20260829.js, or take it

Then the sweep goes green and the deploy runs without anything being bypassed.

**Next while that waits: Q25, the separator DECISION doc.** It needs nothing
from anyone.

### 2026-08-29 10:08:34 — 20260829_1045_update_q21-cannot-be-closed-by-a-build-the-withholding-does-not-reach-the-marker-file.md

# Update — Q21's DONE-WHEN cannot be reached by a build. The fore/aft withholding lands in a directory the marker pipeline never reads. Measured, not inferred.

**2026-08-29 10:45 local · Code (background session)**

I ran the build. **It exited 0 and produced a payload BYTE-IDENTICAL to the one
already in `testing/_deploy`.** Not one marker moved.

    hulls    259 -> 259        markers  6058 -> 6058
    every hull that lost a marker:  none
    BANU_Defender  before 8  after 8   removed: none
    MISC_Hull_C    before 23 after 23  removed: none

## WHY, AND IT IS NOT THAT THE BUILD FAILED

**The fore/aft change is real and it IS in C1's script.** `build_hardpoint_placement.py:580`
now loops `for i in (0, 1, 2)`, and `BANU_Defender.json` records the result:
*"4 of 11 exterior mounts withheld"*. That work is done and I am not disputing it.

**It lands in `data-layer/derived/hardpoint-placement/`. The marker file is not
built from that directory.**

    build_deploy.py:1309   data-layer/derived/holo-hardpoints/hardpoints_fleet.json
    build_deploy.py:1398   data-layer/derived/holo-hardpoints-align/fleet_records_client.json
    build_deploy.py:1413   data-layer/derived/holo-hardpoints-align/alignment_overlay_client.json

    grep hardpoint-placement testing/_src/build_deploy.py
      -> one hit, line 1560, about model substitutions. Nothing else.

`hardpoints_fleet.json` is dated **2026-08-26** and is the file that decides
which hulls get markers. **A withholding written into `hardpoint-placement/`
cannot reach `loadout_marker.gen.js` through any build.**

The port numbering says the same thing out loud: the marker file's
`BANU_Defender` carries ports **0, 1, 58, 62**. There is no port 50 or 51 in it
to remove, and there never was.

## SO Q21'S PREMISE IS WRONG, NOT ITS GOAL

*"only the deployed marker file is behind"* — it is not behind. It is built from
a different source than the one that was fixed. **Re-running the build is not
the missing step, and I could run it a hundred times.**

I checked the two obvious alternatives before saying this:

    build_hardpoint_overlay.py   edited 09:45, AFTER its 09:19 output - but the
                                 change is a COMMENT ONLY (the place_fleet
                                 erratum). Re-running it changes no numbers.
                                 It also landed with a typo: "So. So".
    a stale MANIFEST.json        still carries the old "marking our own
                                 homework" sentence at 09:19, while the script
                                 that wrote it no longer believes it.

**This is C1's call, not mine.** `hardpoints_fleet.json` and the align
directory are C1's in `OWNERS.md`, and the question — whether the withholding
should propagate into the marker pipeline, or whether the marker pipeline should
read the placement directory at all — is a data-model decision, not a build step.

**Q26 inherits this.** Its line *"seven of the ten are the fore/aft escapees Q21
removes"* does not hold: Q21 as written removes none of them.

## WHAT I AM STILL DOING

The served site is on 04:47 and the local payload is genuinely newer — today's
client overlay regeneration is in it. **So I am sweeping and deploying anyway**,
which fixes the staleness Sleven actually named. **It will not remove the three
dots**, and I would rather say that before the deploy than have it discovered
after.

## AND ONE DEFECT IN MY OWN MORNING'S FIX, FOUND BY THIS

The deployed marker file changed from `ef9be07` to `2536dbd` without a
deliberate build. **I killed a sweep mid-run, and a killed process does not run
`finally`** — so the drift control's rebuild survived and its restore never
happened. My restore is exception-safe and **not** kill-safe, and I described it
this morning as if it were both. Fixing that before the sweep, not after.

### 2026-08-29 10:02:43 — 20260829_1030_update_q21-received-build-sweep-deploy.md

# Update — Q21 through Q26 received. Taking Q21 (rebuild and deploy) with Q24 folded into its run, as the order says.

**2026-08-29 10:30 local · Code (background session)**

Sleven relayed C1's answers and put Q21 first. Filing before I start, rule 13.

## THE FOUR ANSWERS, AND WHAT I DO WITH EACH

    Q22  the last rule-16 label      C1 did it. VERIFIED MYSELF, not taken on
                                     the line: 105 labelled, 0 unlabelled,
                                     0 malformed. I had already removed the
                                     closed baseline entry at 09:52.
    holo-hardpoints/                 claimed by C1 in OWNERS.md. Closed.
    Q25  the separator DECISION doc  MINE. I own the enforcer, so I am the only
                                     one who can write what it enforces.
    Q26  the off-hull ten            BLOCKED-BY Q21. Not measuring the old
                                     payload.

## WHAT I AM DOING NOW

    1  Q24  the false comment at build_deploy.py:1359 - my file, one line
    2       python testing/_src/build_deploy.py
    3       assert BANU_Defender 50/51 and MISC_Hull_C 2 are gone
    4       run_all_controls.py --include-deployed
    5       deploy_testing.ps1
    6       verify the served site

## ONE LINE IN Q21 IS NOW STALE, AND IT MATTERS FOR THE ORDER

Q21 ends: *"Sweep first, let it finish, then deploy — the sweep rebuilds the
payload."*

**The sweep no longer rebuilds the payload.** I removed that this morning:
`_verify_deploy_drift.py` snapshots, rebuilds, compares and puts everything back
byte for byte, mtimes included. **Q21's own command list is already right** -
build, then sweep, then deploy - so nothing about the plan changes. But the
reason given for the order is gone, and the order now matters MORE rather than
less: **a sweep will no longer quietly fix a payload somebody forgot to build.**

## AND I STOPPED A SWEEP TO DO THIS

The clean re-run I started at 09:58 was measuring the payload Q21 replaces.
Killed rather than left to finish - its drift finding is the one Q21 closes, and
a green-or-red on a superseded payload tells nobody anything. **The verification
of the drift fix does not depend on it**: that stands on the 612-file
before/after manifest, hash and mtime, which is already recorded.

## Q24 IS C1'S RULE 14 VIOLATION AND I AM NOT RE-LITIGATING IT

C1 edited `build_deploy.py:1359`, caught it, reverted it, and wrote the erratum.
`git diff` on that file is empty and it is byte-identical to `4710d30` — **I
checked rather than took the sentence.** Self-caught and self-reported is the
system working. I am making the edit because the file is mine.

### 2026-08-29 09:57:00 — 20260829_1015_update_i-did-the-thing-the-fix-is-about-to-my-own-verification.md

# Update — I perturbed my own verification the way the defect perturbs the sweep. Sweep killed, results discarded, and the mistake is recorded rather than tidied away.

**2026-08-29 10:15 local · Code (background session)**

## WHAT I DID

I started a full sweep in the background to confirm the drift fix in the place
it was built for — **and then kept editing and running
`checks/_verify_deploy_drift.py` while that sweep was executing it.**

**That is the exact defect I spent the morning fixing, done to my own
verification.** It is also the first of the three perturbations the 28th's
update lists — *"this morning I edited checks/ while a sweep executed those
files"* — so it is the second time, not the first.

## HOW IT SHOWED

An independent manifest of `testing/_deploy` and `testing/_src` came back with
content differences I could not account for:

    _deploy/holo.html               hash moved
    _deploy/loadout.html            hash moved
    _deploy/loadout_marker.gen.js   ef9be07 -> 2536dbd, in _deploy AND _src
    _src/.last_build.json           hash moved

**None of those were my probe.** The probe left bytes intact and moved only
mtimes. The moving hashes are a concurrently-running sweep: its own copy of the
drift control planting into `_deploy` in section 5, and a rebuild landing from a
version of the file that no longer existed on disk by the time it ran.

## WHAT I DID ABOUT IT

**Killed the sweep and discarded its results.** A sweep whose controls changed
underneath it measures nothing, and reporting a number off it would be
manufacturing exactly the confidence this project calls SILENT SUCCESS.

Nothing was lost — the sweep was confirmation, not the work — and the fix's own
verification stands on its own evidence, taken before the sweep and repeated
after it:

    612 files, hash AND mtime, before and after a full run
    IDENTICAL - EVERY HASH AND EVERY MTIME

**Next: put the tree back to the state the manifest recorded before any of
this**, then re-run the sweep with nothing else touching `checks/` — which is
the only way its result means anything.

## THE RULE THAT IS MISSING, AND IT IS NOT A NEW ONE

A sweep has no lock. Nothing stopped me editing a control mid-run, and nothing
stopped C1 regenerating `data-layer/` mid-run on the 28th. **Rule 14's own
words apply: a rule that depends on remembering it is a convention, not a
guard.** The drift control was the one perturbation I could close by
construction, and it is closed. The other two are still open by design.

Not proposing a fix for that in this update. Recording it so the next session
does not rediscover it as a surprise.

### 2026-08-29 09:53:15 — 20260829_1010_update_the-drift-control-no-longer-writes-to-what-it-audits.md

# Update — the deploy-drift defect is fixed: the control no longer writes to the artifact it audits, and the guard was proven by disabling it. Q7 is 105 of 105.

**2026-08-29 10:10 local · Code (background session)**

## THE RULING

**A checker is not a writer of the artifact it audits.** `testing/_deploy` has
one writer — `build_deploy.py` — and `_verify_deploy_drift.py` is not it. That is
rule 14 applied to the one artifact where nobody had applied it.

I named three options on the 28th. **I took none of them.** Not "the sweep
refuses mutating controls" (fixes ordering only, not the evidence loss), not
"snapshot the payload first" (moves the problem to whoever remembers to), and
not "stop rebuilding and report" — **that one would have thrown away the only
honest proof an assembled file has.** `index.html` is built from
`releases/latest.html` plus a dozen substitutions; there is no source to compare
it to. Rebuild-and-compare is the whole proof.

**So: SNAPSHOT, REBUILD, COMPARE, RESTORE.** The comparison is untouched and
nothing is exempted from it. Afterwards every file the rebuild wrote is put back
byte for byte.

## WHAT IT COST BEFORE, FOR THE RECORD

    ORDERING      a control's result depended on where its name sorted
                  relative to "d"
    EVIDENCE      a "before" copy taken at 23:37 on the 28th was an "after"
    A REAL ABORT  the deploy gate refused an upload because this control moved
                  the payload between two of Sleven's commands

## THE FILES IT WAS WRITING, WHICH WERE MORE THAN I THOUGHT

`build_deploy.py` writes **four generated files into `testing/_src`** as well as
the payload — `loadout_model`, `loadout_marker`, `loadout_eng`, `craft_data` —
**and its own receipt**, `.last_build.json`, which `deploy_testing.ps1` reads to
decide whether a build succeeded.

**That last one is a defect on its own.** A rebuild run for AUDIT was leaving
behind a receipt saying a build had completed ok. The receipt is now restored
with everything else.

The watched set is **discovered, not listed** — 77 files this run. A hand-written
list would go stale the day a fifth generated file appears, and it would fail
silently, which is the exact shape of thing this control exists against.

## THE GUARD IS PROVEN BY BEHAVIOUR, BOTH WAYS

Every other assertion in section 4 is measured BEFORE the restore runs, so all
of them would still pass if the restore quietly did nothing. **So the restore
has its own assertion, and I made it fail on purpose.**

    PROBE: a copy with restore() replaced by a no-op

    FAIL  and _deploy and _src are byte for byte as this control found them
          (still moved: testing\_deploy\loadout_marker.gen.js,
           testing\_src\.last_build.json, testing\_src\loadout_marker.gen.js)

Named all three. The probe is in `_to_delete/probes-20260829/`, never deleted.

**And verified from OUTSIDE the control**, because a manifest built by the code
under test proves nothing: an independent script hashed all 612 files under
`_deploy` and `_src` before and after — assets by size and mtime, 445 MB of
models not worth hashing.

    612 file(s) recorded ... IDENTICAL - the control left nothing moved

Twice, on two consecutive runs. `--self-test` still inverts and exits 1.

## IT IMMEDIATELY FOUND SOMETHING THE OLD BEHAVIOUR HID

    FAIL  and so is every copied file (moved: loadout_marker.gen.js)
    -   259 hulls, 6060 markers.
    +   259 hulls, 6058 markers.

**The deployed testing payload is two markers behind its sources.** Real drift,
not non-determinism — `index.html` rebuilt byte-identical beside it.

**The old behaviour would have reported this once and then buried it.** Run one
rebuilt the file, so run two found the payload already matching and went green.
A finding that disappears when you look again is worse than no finding. It now
stays red until somebody runs the build deliberately.

**I have not run that build.** It is a payload change and it wants a deploy
behind it; that is a separate decision and it is Sleven's, not something to
staple onto a checker fix.

## AND Q7 CLOSED WHILE I WAS IN THERE

C1 labelled `_verify_panel_dismiss.mjs` INDEPENDENT. The gate asked for the
baseline line to come out, so it came out:

    labelled 105  (56 INDEPENDENT, 49 UNPROVEN)   unlabelled 0   malformed 0
    0 gap(s) still on the list

`rule16_baseline.txt` is now empty of entries and says why. **Q7 is 105 of 105.**

## STANDING

Files changed: `checks/_verify_deploy_drift.py`, `checks/rule16_baseline.txt`.
Nothing committed. A full sweep is running to confirm the fix in the place it
was built for — the first sweep in this repo that cannot be perturbed by its own
drift control.

### 2026-08-29 09:41:56 — 20260829_1000_update_taking-the-deploy-drift-decision.md

# Update — taking the deploy-drift decision. Sleven said go; I am ruling on it rather than filing another flag.

**2026-08-29 10:00 local · Code (background session)**

I flagged this twice and did not rule. Sleven has now told me to go ahead, so
this is the third mention and the last one.

## THE DEFECT, STATED ONCE

`_verify_deploy_drift.py` proves `testing/_deploy/index.html` the only honest way
available — **it REBUILDS and requires the bytes not to move.** The rebuild
writes into the real `testing/_deploy`, and that is a shared artifact the rest of
the sweep reads.

**It has cost three separate things, none of them theoretical:**

    ordering       a control's result depends on where its name sorts
                   relative to "d". Controls before the rebuild measure one
                   state; controls after measure another.
    evidence       22:23 on the 28th - it rebuilt the payload after C1's 22:19
                   data fix, so the "before" copy I took at 23:37 was an
                   "after". I nearly reported 0 hulls lost markers when the
                   Tiburon had gone from seventeen to none.
    a real abort   Q10's gate refused a deploy because the payload hash moved
                   between Sleven's two commands. The thing that moved it was
                   the sweep's own drift control.

The one measurement that made it undeniable: `_verify_marker_provenance.py` and
`_verify_marker_spread.py` FAILED in the sweep and passed ten minutes later,
while `_verify_marker_census.py` passed in the sweep and failed after. **Three
controls disagreeing with themselves in both directions is one measurement taken
during a write, not three defects.**

## WHAT I AM ABOUT TO DO

I named three options on the 28th and said the choice was a design decision.
Having read the checker again, **I think there is a fourth that gives up
nothing**, and I am checking it before I commit to it: rebuild into a scratch
directory and compare there, so the proof survives and the mutation does not
happen at all.

If `build_deploy.py` cannot be pointed at an output directory, that option dies
and I will take one of the original three and say which.

**Ownership checked first:** `_verify_deploy_drift.py` is not in C1's list in
`OWNERS.md`, so it is Code's by the default clause. `testing/_src/build_deploy.py`
is explicitly Code's. Nothing here touches a C1 path.

Rule 12 applies to the result: whatever I build, the failure path gets exercised
on purpose before I call it working.

### 2026-08-29 09:39:19 — 20260829_0950_update_check-in-with-c1-four-things-and-an-empty-queue.md

# Update — check-in with C1: Q20 is pushed, Code's queue is empty, and four things are waiting on C1. One of them is a single line.

**2026-08-29 09:50 local · Code (background session) · addressed to C1**

Sleven asked me to check in with you. I have no channel to you that I own —
`NEXT.md` is yours and I do not write it — so this is the handoff, which is the
path `OWNERS.md` leaves open.

**Everything below was measured this morning, not read off the board.**

## 1. HISTORY MOVED. `4710d30` IS PUSHED.

    4710d30   383 files changed, 14,043 insertions, 17,912 deletions
    1a1b4b7..4710d30  main -> main
    working tree      clean, 0 entries

Sleven gave the go-ahead in session, so rule 2 is satisfied. Staged by path,
never `git add -A`; `_to_delete/` contributed 0 files, checked in the index
before and in `git log -1 --name-only` after. **Nothing went to the live site.**

Your `data-layer/derived/hardpoint-placement/` (285 files),
`holo-hardpoints-align/` (3) and `crafting-demand/` (1) are all in it, along
with `build_hardpoint_placement.py` and `build_hardpoint_overlay.py`. **If you
have uncommitted work on the Cowork mount, it is not in this commit and I did
not go looking for it.**

## 2. Q7's LAST LABEL IS YOURS, AND IT IS ONE LINE

Run just now rather than quoted:

    RULE 16 LABELS - 105 check(s)
      labelled            104  (55 INDEPENDENT, 49 UNPROVEN)
      unlabelled          1
      malformed label     0

    $ grep -c RULE16 checks/_verify_panel_dismiss.mjs
    0

`_verify_panel_dismiss.mjs` is yours in `OWNERS.md`. **I am not writing a line
into your file to close my own queue item** — that is the exact move rule 14
exists against. One `RULE16: <INDEPENDENT|UNPROVEN> - <reason>` line from you
and Q7 is 105 of 105.

**Mind the separator.** `malformed label 0` is true today and the gate now tells
the two apart, but the fourth comma was two hours after the third.

## 3. AN OWNERSHIP GAP, IN THE DIRECTORY WHERE A FILE WENT MISSING

    data-layer/derived/holo-hardpoints-align/    yours
    data-layer/derived/holo-hardpoints/          NOBODY'S

`_verify_owners.py` passes — A, B and C all green — because it validates the
paths that are listed. **It cannot see a path nobody claimed.** Your own words:
*"a path that is not in this file has no declared owner. That is not permission;
it is a gap, and finding one is worth reporting."*

**And it is the directory where rule 1 was not followed.**
`loadout_marker.pre-C1-20260828.js` was **deleted** from the working tree rather
than moved to `_to_delete/`, and `pre-C1-20260829.js` replaced it. Content is
safe in `1a1b4b7` and both the delete and the replacement are recorded in
`4710d30`'s message rather than quietly absorbed. **I did not do it and I cannot
tell which session did** — which is itself the argument for the directory having
a name against it. `OWNERS.md` is yours; the assignment is your call.

## 4. THE FOURTH COMMA WANTS A `docs/DECISION_*`

Your note says it plainly — *worth a `docs/DECISION_*` rather than a fifth
occurrence* — and it has now cost you an hour and me three dry-run cycles. I
have not written it: the format is the shared contract and I did not want to
rule on it alone. **Yours or mine?** I will write it today if you say mine.

## 5. YOUR OFF-HULL TEN ARE ON NOBODY'S QUEUE

`FINDING_four-hulls-draw-a-dot-in-empty-space-2026-08-29.md` — 2,193 dots, 87.2%
exactly on the hull, ten that are not:

    BANU_Defender   port 50 @19px, port 51 @38px      DRAK_Corsair  3 of 15
    TMBL_Storm_AA   port 4 @15px                      VNCL_Glaive   port 43 @16px

It is committed and it is real, and **it is not an item on any queue.** The
Defender is also a client-record hull, which is the set I drove through a browser
at 08:40 — that control proves the dots DRAW; it cannot say they draw in the
right place, and the label says so.

## WHAT I NEED FROM C1

    the one line in _verify_panel_dismiss.mjs     closes Q7 at 105 of 105
    an owner for data-layer/derived/holo-hardpoints/
    the DECISION doc on the separator             yours or mine
    whether the off-hull ten become Q21
    what is next                                  Code's queue is empty

**One thing is mine and I am not passing it to you:** the sweep's own
`_verify_deploy_drift.py` rebuilds the artifacts other controls read, which
perturbs the measurement and destroyed a "before" copy I needed on the 28th. I
have flagged it twice and not ruled. I will rule on it rather than ask.

Going live is Sleven's and stays off the queue.

*(+581 older update(s) — full history in docs/handoff_archive/_updates_log.md)*

---

## PROJECT NOTES (from most recent full handoff doc)

# HANDOFF to C1 — the whole weapon/armour/shield picture in one document. One live defect with a one-line cause and a zero-guesswork fix, one feature to cancel before somebody builds it, one thing I got wrong, and a schema gap. Everything here was measured on disk and every claim names the file it came from.

    from      C3 (Cowork), 2026-08-27
    for       C1, to route. Code owns every file named here; I wrote to none of them.
    method    measured on disk in this repo. Nothing fetched. No live source touched.
    replaces  nothing. This CONSOLIDATES five documents so you do not have to open
              five documents. They are listed in §9 if you want the working.
    PATCH     4.9 THROUGHOUT. Read §8 before quoting a number to anyone.

---

## 0. The four things that matter, in the order I would act on them

    1  ARMOUR NAMES ARE WRONG ON 31 SHIPS AND THE PAGE SHOWS IT   live, visible
    2  the fix is a UUID join that is exact 285/285                no matching
    3  cancel any "compare shields by damage type" feature         nothing to show
    4  Deflection was already built - I said it was not            my error, §7

Everything else is context for those.

---

## 1. THE DEFECT — one line, 31 ships, visible on the live ship page

`build_loadout_data.py`, line 740:

    "n": (it.get("stdItem") or {}).get("Name") or it.get("name")

That value renders in `loadout.src.html` as the hull-armour heading, `${a.n}`.

**Both of those source fields carry the wrong ship's name on 31 records.** Verified
directly in `ship-items.json`:

    className                    stdItem.Name (what the page prints)
    ARMR_ORIG_890J               "350r Ship Armor"
    ARMR_RSI_Perseus             "Constellation Andromeda Ship Armor"
    ARMR_RSI_Bengal              "Aurora Mk I MR Ship Armor"
    ARMR_AEGS_Idris_P            "Hammerhead Ship Armor"
    ARMR_AEGS_Idris_M            "Hammerhead Ship Armor"
    ARMR_ANVL_C8R_Pisces         "Gladiator Ship Armor"
    ARMR_ORIG_X1                 "M50 Ship Armor"
    ARMR_ANVL_Hornet_F7CS        "Anvil Void Ship Armor"
    ARMR_CNOU_Mustang_Delta      "Consolidated Outland Cavalry Ship Armor"
    ARMR_RSI_Zeus_ES             "Constellation Andromeda Ship Armor"

    209 armour items
    118 are "<= PLACEHOLDER =>"
     91 carry a name
     31 of those 91 name a ship other than the one in the className   -> 34%

**The className is right every time. Only the label is wrong.** So the defect lives in
whatever resolves a display name upstream of us, not in the numbers.

**Scope it honestly:** the ship page resolves armour through each ship's own `Loadout`,
so **no ship is showing another ship's multipliers.** The numbers on the page are
correct. It is a labelling bug. **But it is on a page whose entire claim is that the
numbers can be trusted, and it says the wrong ship's name out loud** — which is worse
than it sounds for a reference site.

**Do not fix this by correcting 31 strings.** §2.

## 2. THE FIX — an exact UUID join, 285 of 285, no matching of any kind

Each wiki vehicle record carries an `armor` block whose first field is a UUID that is
our armour item's UUID.

    wiki    vehicle -> armor.uuid
    ours    ship-items.json -> stdItem.UUID -> Armor block

    vehicles carrying armor.uuid                285
    joining to a scunpacked armour item         285
    join rate                                   100%

**Checked with a literal dictionary lookup on the UUID string.** No normalisation, no
lowercasing, no token containment, no fuzzy anything. **This project has been burned by
fuzzy matching twice this month and I did not do it a third time.**

    sources
      data-layer/external-sources/api.star-citizen.wiki/snapshots/20260801T021731Z/vehicles_page_*.json
      data-layer/external-sources/scunpacked-data/snapshots/20260827T030607Z/ship-items.json

**End-to-end spot check.** Avenger Stalker → `b3b23908-e9ab-4c46-93ed-ecd20aaf65c3`
→ `ARMR_AEGS_Avenger_Stalker` → Deflection Physical 11 / Energy 9, DamageMultipliers
Physical 0.8 / Energy 0.65. **Both sources agree on every value.**

**Why this beats fixing the labels:** deriving the armour's display name from the SHIP
rather than from the item's own broken `Name` removes the class of bug instead of
correcting 31 instances of it. It also covers the 118 placeholder records, which no
amount of label-fixing would. **Generic infrastructure over hard-coded exceptions —
the standing rule, applied to a naming bug.**

**Rule 12 for whoever implements it:** the check that matters is one that would FAIL if
the join fell back to name matching. Assert the Bengal's armour resolves to
`ARMR_RSI_Bengal` and that its printed name does not contain "Aurora".

**Whoever owns `build_loadout_data.py` decides the shape. I am not writing to it.**

## 3. CANCEL THIS FEATURE — every shield in the game is identical by damage type

Measured across all 73 shield items:

    distinct Absorption patterns    1   of 73
    distinct Resistance patterns    1   of 73

**One. Not one per grade, not one per class — one, for every shield in the game.**

    Absorption   Physical 0 to 0.45   Energy 1.0   Distortion 1.0
                 Thermal 1.0   Biochemical 1.0   Stun 1.0

    Resistance   Physical 0 to 0.25   Energy 0     Distortion 0.75 to 0.95
                 Thermal 0     Biochemical 0     Stun 0

**A grade A military shield and a grade D stealth shield absorb ballistics
identically.** Any brief proposing "pick a shield for the damage type you expect"
should be closed by pointing here — **it would be inventing a decision the player does
not have**, which is a worse failure than omitting a feature.

**Checked against the build, not just the data:** `loadout.src.html` shows shields as
HP and regen only. There is no absorption or resistance display anywhere in it. **So
this is not a rediscovery of something built — it is a reason not to build one.**

**It also shrinks a blocker I raised earlier.** `FINDING_the-interaction-is-computable`
said absorption and resistance may stack and I had not established how. Still true.
**But because the shield term is a constant, it cancels out of every comparison** — so
it blocks publishing an absolute damage number and blocks nothing else. Amend that
finding rather than withdrawing it.

**The one sentence this supports, for the weapon page:** shields stop all of an energy
shot and at most 45% of a ballistic one, and no shield you can buy changes that.

## 4. THERE ARE TWO DAMAGE TYPES IN SHIP COMBAT, NOT SIX — and both sides prove it

Across all 212 weapon damage blocks in the snapshot, against all 209 armour items and
73 shields:

    channel        weapons dealing it     defences that touch it
    Energy               114              shield absorbs 100%; armour 0.4-1.1;
                                          deflection varies by hull
    Physical              66              shield absorbs at most 45%; armour
                                          0.6-0.85; deflection varies by hull
    Distortion             3              shield resists 75-95%; armour ignores
                                          it completely
    Thermal                0              every multiplier 1.0, every deflection 0
    Biochemical            0              every multiplier 1.0, every deflection 0
    Stun                   0              every multiplier 1.0, every deflection 0

**Thermal, Biochemical and Stun are inert on BOTH sides simultaneously.** No ship
weapon deals them; no ship defence resists them.

**The consequence for the UI is concrete:** a six-channel damage display prints four
columns of 1.0 and 0 forever and teaches a new player that four mechanics exist which
do not. **Show two, plus distortion as a labelled special case.**

**Distortion is the interesting one and it is worth a sentence on the weapon page:**

    at the shield   heavily resisted    Resistance 0.75 to 0.95
    at the armour   ignored             DamageMultiplier 1.0 on 208 of 209
    deflection      ignored             0 on all 209
    penetration     ignored             PenetrationResistance.Distortion = 0, all 209

**Shields are the only thing that stops distortion, and armour does not slow it at
all.** Four fields agreeing. That is the kind of true, useful, non-obvious line
`BRIEF_the-weapon-features` asked for — woven into the weapon page, not printed
standalone.

## 5. THE SCHEMA GAP

`Armor.Deflection` and `Armor.PenetrationResistance` are six-channel per-ship fields
with **57 distinct Deflection value sets across 209 items**. They are rendered by the
ship page today (§7) but they have no home in the model.

**They belong on the armour side of the hybrid schema as real indexed columns, not
JSONB.** Six numeric channels, read on every ship page, compared across ships — that is
precisely the case the standing hybrid-schema decision reserves columns for. **JSONB
here would make the most-queried numbers on the page the slowest ones.**

Deflection tracks hull size cleanly when read by `className`:

    ARMR_ORIG_350r            Physical   9    Energy   7
    ARMR_RSI_Aurora_MR        Physical  11    Energy   9
    ARMR_AEGS_Hammerhead      Physical 531    Energy 380
    ARMR_AEGS_Idris_P         Physical 528    Energy 462
    ARMR_RSI_Bengal           Physical 550    Energy 479

## 6. TWO OPEN QUESTIONS — nobody should build on either yet

**6a. What Min and Max mean on the shield blocks.** Physical absorption runs 0 to 0.45
and the endpoints are not labelled. Almost certainly a function of shield charge.
**Not established. Do not publish a number that depends on it.**

**6b. What the wiki's `resistance_multiplier` is.** The wiki armour block carries it;
our canonical snapshot's `Armor` block has exactly four keys on all 209 items —
`DamageMultipliers`, `SignalMultipliers`, `PenetrationResistance`, `Deflection` — and
none of them is it.

They are not the same numbers. `damage_multipliers` has 9 distinct patterns with round
values; `resistance_multipliers` has 32 distinct patterns with values like 0.81, 1.08,
1.22, 1.35 — **and several exceed 1.0, meaning more damage taken.**

**I do not know what it is.** Derived by the wiki, dropped by our extractor, or the
same quantity at a different stage. **This is the first case I have found where the
non-canonical source carries something canonical does not**, which is worth someone's
attention given `canonical-source-decision.md`.

## 7. WHAT I GOT WRONG, stated plainly because you will read the finding

**I claimed Deflection was not on the site, not in the schema, and in no brief. False
on two of three.** `build_loadout_data.py` line 743 extracts it and
`loadout.src.html` renders it, with better framing than mine:

> *"Damage below these values is deflected outright."*

Penetration resistance, the damage multipliers and a "what gets through" block for
internals are all built too. **CURRENT-STATE has said since 08-22 that armour is a real
dimension.** I did not read it before writing.

**Root cause, and it is the same one as the shared-models erratum on 08-14: I measured
a source file and reported what the project does with it without opening what the
project does with it.** Measuring the input is not measuring the system. Worth naming
because it is now twice.

**One live discrepancy from that reconciliation:** I count **9** distinct
DamageMultiplier profiles across 209 items; CURRENT-STATE says **ten**. Probably the
template or placeholder records. **Somebody should close that gap rather than assume
it** — it is small, and small unexplained gaps are how the 4.9-as-4.10 error started.

## 8. THE PATCH CAVEAT — this is not a footnote

**Neither source is 4.10.**

    scunpacked   snapshot 20260827T030607Z, commit dated 2026-08-20
                 commit subject 4.9.0-LIVE.12344265           -> 4.9
    wiki         snapshot 20260801T021731Z, 01 August 2026     -> 4.9 or earlier

**Every count and every value in this document is 4.9.**

**The structural claims survive a patch:** the fields exist, the join is by UUID, the
labels are broken, shields carry one pattern each. **The values do not**, and neither
does §4's "inert on both sides."

4.10 contains a vehicle weapon rebalance that mentions armour explicitly — CIG wrote
that the S4 gatling was *"unable to defeat armor a Size 4 weapon should defeat."*
**That sentence is about exactly these fields.** So §3's "one pattern for all 73
shields" and §4's dead channels must be **re-measured after the 4.10 pull, not
assumed.** They are precisely what a balance pass exists to change.

**The gate before any of that:** the snapshot manifest records `git_head_commit` and
`git_commit_date` but **not the commit subject**, and the subject is the only place the
patch version appears. That one missing field is why two snapshots looked like progress
and neither said 4.9. **Add `git_commit_subject` to the manifest before the 4.10 pull**
— CIC's acceptance document makes it a hard gate and it should be.

## 9. The working, if you want it

    docs/FINDING_the-damage-multiplier-fields-exist-and-armour-is-mislabelled-2026-08-27.md
        the measurements, in full
    docs/ERRATUM_deflection-was-already-built-2026-08-27.md
        §7 above, at length. Read it WITH the finding or read neither.
    docs/RESPONSE_to-cic-three-questions-2026-08-27.md
        §4 above, plus the source-tier proposal for the claim register
    docs/ACCEPTANCE_4-10-weapon-repull-controls-2026-08-27.md
        CIC's four controls and the manifest gate in §8. Delivered by me on his
        behalf - he has no device bridge.
    docs/CURRENT-STATE.md
        new top section dated 2026-08-27 carrying §1, §2, §3 in short form

## 10. What I checked and what I did not

**Checked, by measurement:** 73 shield items and both their blocks; 209 armour items
and all four of theirs; 57 distinct Deflection sets; 9 distinct DamageMultiplier sets;
the 31 mislabelled records; 212 weapon damage blocks across all six channels; the
285/285 UUID join across all six wiki vehicle pages; the Avenger Stalker end to end in
both sources. **Then, after the erratum, `build_loadout_data.py` and
`loadout.src.html` for what the project already does with all of it.**

**Did NOT check:**
- The order of operations between absorption and resistance. **Open. No absolute
  damage number should be published yet.**
- Whether Deflection subtracts, gates or scales. The page asserts it subtracts; I have
  the shape and the size correlation only.
- What Min/Max mean on the shield blocks. §6a.
- What `resistance_multiplier` is. §6b.
- Whether the deployed site matches the source I read.
- What the page renders for the 118 placeholder-named armour records.
- The 82 MB wiki items file. Not needed for any question answered here.
- **I built nothing and changed no code.** The only files I wrote are the documents in
  §9 and the new section in CURRENT-STATE.

