# Update — Q10 is built and proven: a red control now stops a deploy. And the one control that stayed red for two days was two ports differing in the fifth decimal.

**2026-08-27 23:52 local · Code (background session)** — Sleven: *"do all of
them"*.

---

# Q10 — 4 CONTROLS OUT OF 98 BECOMES ALL 98

## The design, and the cost it refuses to pay

The sweep takes 539–613s. **Ten minutes on every upload is how a gate gets
switched off**, so it does not run on every upload:

    run_all_controls.py   writes checks/.last_sweep.json when a sweep finishes -
                          fingerprint of the payload it swept, result, failures
                          and NOT RUNs by name, partial and self-test flags
    checks/sweep_gate.py  ONE implementation of both the fingerprint and the
                          verdict, called by both deploy scripts
    both deploy scripts   refuse on anything but exit 0

**The cost lands on the sweep, once, instead of on every deploy, always.**

The fingerprint covers every non-model file by path, size and sha256, plus the
model COUNT and TOTAL BYTES. Hashing 456 MB of geometry on every deploy would
put the ten minutes straight back; a dropped or truncated models folder moves
both numbers. **A model swapped for another of exactly the same size is the gap
and it is named in the file rather than left to be found.**

## Proven, and this is Q10's DONE-WHEN rather than a paraphrase of it

`_verify_deploy_guards.py` **83 -> 115 assertions, 0 failed**, `--self-test`
still exits 1. Section 11 drives BOTH scripts:

    REFUSES a payload whose sweep had a RED control / and names it /
        and never reached its dry run
    REFUSES when a control could not be RUN, not just failed / and names it
    REFUSES when the payload changed since the sweep / and says so rather
        than blaming a control
    REFUSES when NO sweep has been run at all / and gives the command
    REFUSES a PARTIAL sweep - a subset is not a sweep
    REFUSES a --self-test sweep - inverted is not clean
    REFUSES an UNREADABLE receipt
    and a clean sweep of THIS payload GETS THROUGH, saying how many
        controls vouched for it
    -IgnoreSweep gets past a red sweep, and says OVERRIDE

**The fixture copies the real `sweep_gate.py` rather than stubbing it**, and the
copy's receipt path resolves inside the throwaway project, so the repo's own
receipt is never touched.

## Three mistakes of mine on the way in, all caught before they shipped

**A stray carriage return in operator-facing text.** `checks\\run_all_controls.py`
rendered as `checks` + linebreak + `un_all_controls.py`. The heredoc collapsed
`\\\\` to `\\` and Python then read `\\r` as CR. Fixed in both scripts, and all
three files checked for other lone CRs: none.

**The same collapse broke a `print("\\n11. ...")`** into an unterminated string
literal. Caught by the file refusing to parse.

**A double `shutil.rmtree`** - `make_project` always builds at `tmp/proj`, so
`proj2` IS `proj` and the second removal hit nothing. Fixed, and the reason is
written at the site.

**Third time that heredoc has eaten a backslash tonight.** From here, anything
containing one gets written with a file rather than a heredoc.

---

# THE LAST RED CONTROL, AND IT WAS NOT A DEFECT

The first full sweep under the new gate: **94 ok, 2 failed, 3 skipped, 0 NOT
RUN, 539s.** One failure was `_verify_deploy_guards.py` - my own, mid-change.
The other was `_verify_placer_candidates.py`, which C1 had already handed back
as "not mine, and `place_fleet.py` is not in this repo".

**Measured before escalating:**

    Asgard / hardpoint_turret_console_right_access  0.12761 -> 0.12762
    Asgard / hardpoint_turret_pilot                 0.12876 -> 0.12875

**Two ports, differing by ONE in the last emitted decimal.** `unit` is written
to five places, so that is the smallest representable difference there is - it
cannot express a placement decision, only the same number arriving by a slightly
different route. `hardpoints_fleet.json` was last written **2026-08-26 21:52**,
so this control has been red since then and nobody noticed. **Which is exactly
the argument for Q10.**

The assertion asked one question for two different answers. Split:

    every previously placed hull is byte-identical, OR differs only in the
        last emitted decimal                          <- passes
    markers that moved FURTHER than the emitted precision   <- still 0
    and the two wobbles are PRINTED BY NAME, not swallowed

**What is defended is unchanged** - P1's candidate expansion must not re-place a
hull it never touched, and anything moving further than the emitted precision
still fails by name. A growing list of last-digit wobbles would mean the
generator had become unstable, which is why they are reported rather than
ignored.

**Proven it still fires:** a copy with `EPS = 1e-12` treats the Asgard's wobble
as real movement and both assertions go red, naming the hull. Probe moved to
`_to_delete/probes-2026-08-27/`.

---

# Q7 — TRANCHE 3, THE `find` FAMILY

    labelled     36  (17 INDEPENDENT, 19 UNPROVEN)     was 29
    unlabelled   63                                    was 68

**Four INDEPENDENT.** `_verify_find_build_step.py` compares the shipped file
against **the database** - two sources the generator cannot make agree by being
wrong twice. `_verify_find_deployed.mjs` fetches the deployed origin and reads
what a visitor gets, which no local artifact can fake.

`_verify_find_page.mjs` is INDEPENDENT for a reason worth writing down, because
it looks like the one I called UNPROVEN an hour ago: it greps the built page for
`fetch(`, `XMLHttpRequest`, `API_BASE`. **Asserting ABSENCE is settled
completely by a grep** - the string is there or it is not. `_verify_label_cold_start.mjs`
greps a source for a property NAME and infers behaviour from a mention, which is
not. Same instrument, different question.

**One UNPROVEN:** `_verify_find_data.py` imports `build_find_data` and drives
that module's own gates, so a gate whose definition of "equal" is wrong is wrong
on both sides.

All four local find controls green after labelling.

Full sweep re-running now for the first clean receipt. Nothing committed since
`fee621f`.
