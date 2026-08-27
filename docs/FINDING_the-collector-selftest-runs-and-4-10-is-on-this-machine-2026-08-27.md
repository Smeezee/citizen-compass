# FINDING — the collector selftest runs, passes 575 checks, and caught my build mistake in the first minute. And 4.10 is sitting on this machine.

**Written by Code, 2026-08-27. Q6 of `NEXT.md`.**
**"~190 checks have never been executed once… If they cannot run, the reason is
the deliverable."**

They can run. They did. Here is what came out, and one thing that came out
sideways and matters more than the answer.

---

## 1. It builds and it passes

    go build -ldflags "-H=windowsgui" -o collector.exe .     exit 0
    collector.exe --selftest                                 exit 0

    575 checks, 0 failed, 0 void
    selftest PASS

**575, not ~190.** The estimate in the order is low by a factor of three. The
suite has grown well past what anybody last counted.

`capture_keys` — the defect the order names as having shipped dead in every
build — **is covered now, with a negative control**:

    [ok] keys: the startup line says what it understood
    [ok] NEGATIVE CONTROL: capture_keys still produces tap keys

## 2. It caught my mistake before I could report a false result

The first run I did was `go build` with no flags. It failed, on exactly one
check:

    [FAIL] CONSOLE: this binary is a GUI build (PE subsystem 2)
           subsystem is 3; 3 is CONSOLE, which opens a black terminal window on
           every launch and kills the collector when closed

**That failure was mine, not the collector's.** `build.ps1` passes
`-ldflags "-H=windowsgui"` and I had not. Its own comment records that this
exact defect shipped once before: *"Seven source files said this program is
built `-H windowsgui`. No build command anywhere passed it."*

So the first thing 575 never-executed checks did was catch a live regression in
the build they were handed, one minute after being run for the first time. That
is the strongest evidence available that this suite is real and not decoration —
better evidence than the 575 passes.

**Rebuilt with the flag: PASS.** Reported this way round deliberately, because
"the selftest fails" and "the selftest caught me" are different sentences and
only the second one is true.

## 3. THE GAP — the selftest's output is invisible in the build that ships

`-H=windowsgui` sets the PE subsystem to GUI, and **a GUI binary has no
console**. So the shipping collector, run as `collector.exe --selftest`, prints
**nothing at all**. No pass line, no fail line, no check names.

    console build  ->  575 lines on screen, and the wrong subsystem
    GUI build      ->  silence, and the right subsystem

The results are written to `<out>/collector-selftest-results.txt`, defaulting to
the captures directory. So the information exists — but the operator's only
signal at the terminal is an exit code, and **an exit code is exactly what
nobody reads.**

This is the shape this project already has a name for. It is not a check that
cannot fail; it is a check whose failure cannot be seen from where it is run.
A tester told "run `--selftest`" watches a window appear and vanish with no
output and has no reason to think anything happened.

**Not fixed here.** The collector is not on my queue beyond running this, and
the fix is a judgement between several options — attach a console for this one
flag, write to stderr, or print the transcript path to a message box. Recording
it as the deliverable the order asked for.

## 4. THE THING THAT CAME OUT SIDEWAYS — 4.10 is installed on this machine

The selftest prints its environment. It said:

    [note] Game.log  C:\Program Files\Roberts Space Industries\StarCitizen\LIVE\Game.log
                     (2241 lines, patch 4.10.191.2241)

Checked directly, not taken from the note:

    Game.log   504,437 bytes   2026-08-26   build 4.10.191.2241
    Data.p4k   150.6 GB        2026-08-26

**Every data source this project holds is 4.9.** C3's handoff §8 is explicit —
scunpacked is commit `4.9.0-LIVE.12344265`, the wiki snapshot is 4.9 or earlier,
*"every count and every value in this document is 4.9"* — and CIC has written an
acceptance document gating the 4.10 re-pull.

**The 4.10 game data is on the machine, current as of yesterday.**

### What that does and does not mean

**It does not mean the 4.10 pull is done, or easy, or authorised.** A 150.6 GB
p4k is a container; extracting it is C1's lane (`extract_p4k_entry.py`), the
split order says CODE-3 is *"NOTHING. Do not start the p4k work"*, and
`decode_cga_nodes.py` and the rest are on the NOT CODE'S list. **I have not
opened it, and I am not going to.**

What it means is narrower and still worth having: **the prerequisite everyone
has been treating as a future step is already satisfied on this machine.** The
4.10 weapon rebalance that C3 flagged — CIG writing that the S4 gatling was
*"unable to defeat armor a Size 4 weapon should defeat"* — is measurable from
data that is already here.

Anyone planning the 4.10 re-pull should know that before planning around a
download.

---

## What I did not do

- Did not run the collector for real, only `--selftest`.
- Did not touch the p4k.
- Did not write another collector check — the order says not to until these
  run, and now that they have, whether to add more is a decision rather than an
  obligation.

---

*Code, 2026-08-27.*
