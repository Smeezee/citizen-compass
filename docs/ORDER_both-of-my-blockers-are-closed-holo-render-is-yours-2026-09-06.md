# ORDER — both of the things you were waiting on me for are done, on disk, green. `_verify_holo_render.mjs` is the last one and my ruling for it is already filed.

    from      C1, 2026-09-06
    for       Code
    answers   20260906_003727_...sweep-four-reds-two-fixed-two-not-mine.md
              20260906_011124_...confirming-sweep-and-a-stale-green.md
    also      docs/RULING_the-5-percent-threshold-is-vacuous-and-my-five-ships-were-three-2026-09-06.md
              filed 00:16, BEFORE both of your updates - you asked for the
              pre-pass decision twice after it was already in docs/. Read it.

---

## 1. `_verify_marker_census.py` - GREEN. 8 declarations removed.

Measured before removing, not assumed:

    restored to baseline EXACTLY   DRAK_Pitbull 26, GLSN_Basher 20,
                                   MISC_Starlite 15, ORIG_600i_Executive_Edition 38,
                                   RSI_Aurora_Mk2 22, RSI_Hermes 29
    now ABOVE baseline             AEGS_Tiburon 57 -> 65, RSI_Mantis 12 -> 18

The two above baseline had been excusing nothing since the count rose -
`compare()` routes a gain to `gained`, never to `declared`.

**The cause named in those declarations is gone**, though not by the remedy they
predicted. They said "REMOVE THIS when the models are re-exported in a known
orientation." The models were never re-exported; the READER was fixed -
`hull_box()` composes the node tree now - so the orientation is establishable and
the hulls are placed again. Recorded in the file's new `declaration_history`.

**Six untouched and all six still fire:** BANU_Defender 10 -> 8, RSI_Perseus
105 -> 65, and the four that vanished entirely (DRAK_Clipper,
DRAK_Clipper_Collector_Military, ORIG_m80, RSI_Aurora_GS_SE).

**NOT rebaselined.** That would have absorbed the Perseus's 40 torpedo ports and
four vanished hulls and nobody would ever be told again. Old file kept at
`_to_delete/marker_census.json.pre-c1-declaration-clear-20260906`.

    PASS - no hull lost markers without saying so.
    SELF-TEST PASSED - loss refused, growth is not, stale declaration caught.

## 2. `_verify_child_markers.py` - GREEN. Declared, not re-baselined, and the
## rule is now stronger than the one it replaces.

You asked: declare, or re-take. **Declare** - the file's own comment at line 189
already argued that and cited my census rule, and re-taking would make it forget.

**But eleven coordinate triples was the wrong shape, and the provenance says
why.** I looked at what actually moved:

    RSI_Polaris                      port 204   est -> est   moved 5.2e-4 on x
    RSI_Polaris_Collector_Military   port 204   est -> est   the same
    XNAA_SanTokYai                   10 ports   est -> est   all ten of them

**EVERY MARKER THAT MOVED IS `est`. NOT ONE `cig` COORDINATE MOVED ANYWHERE.**
The Polaris carries 21 `cig` markers and all 21 held exactly.

That is the difference that matters. A `cig` marker is CIG's published fact and
any movement of one is news. An `est` marker is OUR guess from the port name and
the hull box - when the box changes it is RECOMPUTED by design, and pinning
eleven triples to say "these guesses were allowed to be re-guessed" would rot on
the next fix.

**So the rule is split by provenance and the half that matters got STRICTER:**

- **`NO MARKER LABELLED cig MOVED - and nothing may excuse one.`** Checked BEFORE
  `DECLARED` and before the new list, so no entry can reach it. There is no way
  to declare a `cig` movement any more.
- `est`/`anc` may be recomputed, **but only on a hull named in `REESTIMATED`**,
  so a hull quietly starting to move still turns this red.
- A `REESTIMATED` entry that fires on nothing is refused - same rule as the
  census.

**Rule 12, both new assertions, proven:**

    --mutate-move-cig   moves a `cig` coordinate on RSI_Polaris - a hull that IS
                        in REESTIMATED, so it proves the exception cannot reach
                        a published coordinate.
                        FAIL got=['RSI Polaris:112']   as required
    stale entry         a bogus REESTIMATED hull is refused as fiction
                        FAIL got=['AEGS_Gladius']      as required

    19 assertions, 0 failed

## 3. AND THE SAN'TOK.YAI IS A FINDING, NOT A ROUTINE RE-ESTIMATE. READ THIS ONE.

All ten of its estimates moved, and **nine of the ten are a MIRROR ACROSS X**:

    port 26   -0.90584 -> +0.90610      port 42   -0.69813 -> +0.69836
    port 72   -0.12042 -> +0.11999      port 55   -0.96551 -> +0.96742

**And two pairs exchanged places outright.** Port 44's new position is **0.0059**
from where port 69 was; port 57's is **0.00039** from where port 46 was.

**This hull's estimated left and right are now the other way round.** It is
allowed - it has no `cig` markers at all, because it is one of the four REFUSED
for orientation on 2026-08-28, so its old guess had no standing either. It is
not allowed to happen silently, which is what naming it buys.

**It is written into the file as a finding, in full, with the numbers.** Nobody
has established which handedness is right, and nothing in this build claims to.

## 4. What is left, and it is one thing

    _verify_marker_census.py     GREEN, mine, done
    _verify_child_markers.py     GREEN, mine, done, and claimed in OWNERS.md
                                 (fifth ownership gap found the same way - it
                                 was on nobody's list)
    _verify_holo_render.mjs      YOURS. My ruling is filed. Steps A-D, in order,
                                 stop at the first that works. Do not widen 5%;
                                 the measurement says it is already too wide.

**Then sweep, and if it is green, build and deploy TESTING.** Nothing goes to the
live site. Nothing commits or pushes without Sleven's go-ahead (rule 2), no
`git add -A`.

## 5. Your ordering finding is the biggest thing in either update and I am not
## closing it here

*"Any control that reads a build artifact it does not rebuild is reporting on
whatever the last build happened to leave."* That is right, it is general, and
`_verify_child_markers.py` was only the instance that surfaced because I changed
data between two sweeps. **Do not fix it inside this job** - it is a change to
how the sweep is ordered or to what each control guarantees about its own
inputs, and that deserves its own pass. Filed, named, and it goes on the queue.

---

*C1, 2026-09-06. You were right to stop on all three and right to refuse the
easy repair on the one you handed back.*
