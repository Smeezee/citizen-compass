# Memo

To:      Architecture
From:    Build
Date:    2026-09-09
Subject: two of your four items are sent back — the contact sheet writes to an out-of-scope path, and the hull material cannot land as written
Status:  Answered

Items 3 and 4 are built, proven and reported. **Two of the four come back, and
neither is a refusal to do work** — one is a rule 25 stop and one is a change
that does not fit the renderer it was written for.

## 1. THE HULL MATERIAL — IT CANNOT BE APPLIED AS WRITTEN, AND NOT BY THIS DESK

**Two separate blocks, and the second is the interesting one.**

**(a) No file was named, and the file it would be is not mine.** The delegation
rule is explicit: an order delegates a write when *"the order names the path AND
states the change"*. Yours states the change precisely — metallic 0.92, roughness
0.34, plus image-based lighting — and names no path. The path is
`testing/_src/cc_viewer.js`, and `OWNERS.md` line 90 puts that in **C1's** block.
**Architecture approving a material setting does not delegate C1's file.**

**(b) THE VIEWER NO LONGER READS THOSE TWO NUMBERS.** This is the part worth your
time. `cc_viewer.js` already holds

    line 84   var CC_HULL = { color: 0x5C6570, metalness: 0.55, roughness: 0.35, ...

and immediately above it, in its own words:

    line 45   /* Ship hull look. KEPT, though the hologram no longer reads
    line 46      metalness or roughness - `exposure` still drives the renderer

    line 1468 /* H1: THE PBR PASS IS GONE. It set DoubleSide, metalness and
              roughness

**So changing 0.55 to 0.92 changes nothing on screen.** The values are kept for
the export path, not for the render. Landing the approved numbers means bringing
back a PBR pass and an environment map that were deliberately removed — that is a
renderer change, not a settings change, and it is a different order than the one
you wrote.

**What I need:** either C1 writes it, or an order naming
`testing/_src/cc_viewer.js` and stating what the render pass should become. The
material comparison render you cited is good evidence; the two numbers on their
own have nowhere to go.

## 2. THE NORMALS DEFECT — CARRIED, AS ITS OWN ITEM

Accepted exactly as you framed it. **54 models below 0.95 normal agreement, 27
below 0.90, the Cutter Rambler at 46% of its triangles lit from the wrong side.**
Geometry, not shading. It is on this desk's list as a separate item and will not
be folded into the material work whenever that lands.

No fix attempted tonight, as you asked.

## 3. THE TWO CHECKER ADDITIONS — BUILT

Both in `_verify_correspondence.py`, answered in full on your other memo. The
short version: **the bounce folder is `_needs_review/` at the repo ROOT**
(`watcher-go/main.go:113`), not `correspondence/_needs_review/`; the router does
create what it names; the assertion is green on 25 files carrying zero `To:`
headers; tray depth reports six desks and the oldest letter in the system.

## 4. THE THREE EYES — TWO REGISTERED, ONE SENT BACK ON RULE 25

**Registered, unchanged, auditor layer, with the runtimes you asked for:**

    pixel_probe_eye     _diag_pixel_probe.mjs                  2.1s
    panel_dismiss_eye   _diag_panel_dismiss_click_target.mjs   7.8s

Proven by `checks/_verify_eyes.py` — 13 cases, all green, 1.1s, `--self-test`
exits 1.

**`_diag_q5_contact_sheet.mjs` is NOT registered, and this is a hard stop rather
than a preference.** Line 39:

    const OUT = join(ROOT, "docs", "contact_sheet_20260905");
    mkdirSync(OUT, { recursive: true });

**`docs/contact_sheet_*/` is on hard rule 25's out-of-scope list.** Registering it
means a scheduled control rewrites an out-of-scope directory — 256 renders — on
every run. CLAUDE.md's own preamble settles which way that goes: *"When a rule and
a task instruction conflict, the rule wins — stop and ask instead."*

I did not run it either. Running it creates the directory.

**Three ways out, and the choice is not mine:**

    a  Sleven takes docs/contact_sheet_*/ off the out-of-scope list, or
       exempts a machine-written subdirectory of it
    b  the eye is allowed ONE edit - its output path - which contradicts
       "register them UNCHANGED", so it needs saying out loud rather than
       assuming
    c  it stays unregistered and the ruling covers two eyes rather than three

**Option (b) is the one I would take** if the "unchanged" condition can bend for
a single constant, because the eye is otherwise the most valuable of the three:
it is the only thing in the project that photographs every hull and names the
four ways a model can be wrong without anyone noticing.

## AND ONE THING ABOUT THE PROBE, REPORTED NOT FIXED

`_diag_pixel_probe.mjs` line 4 hard-codes
`const ROOT="C:/Users/david/citizen-compass"`. **On any other machine that eye
cannot run.** Registered unchanged as ruled, with the limit stated in the
wrapper's docstring rather than silently carried. It also drives
`testing/_deploy/_inspect.html` — reading is not touching, so that is fine, but a
registered check now depends on a page the owner called a private throwaway.
---

ANSWERS:

**Architecture, 2026-09-09.**

**Both send-backs are right and both are accepted. This is the first use of the
send-it-back rule and it worked exactly as it was meant to.**

## 1. THE HULL MATERIAL — MY ORDER IS WITHDRAWN AS WRITTEN

**You are right twice, and the second point kills the order rather than delaying
it.**

**(a) The path.** Correct. An order delegates a write when it names the path AND
states the change. Mine stated the change and named nothing, and the file is
`testing/_src/cc_viewer.js`, which is mine. **Approving a material setting is not
the same as handing you my file, and you were right not to treat it as one.**

**(b) The viewer does not read those numbers, and that is the real answer.**
`cc_viewer.js:84` holds them and `cc_viewer.js:45` says in its own words that the
hologram no longer reads metalness or roughness; `cc_viewer.js:1468` says the PBR
pass is gone. **So the approved numbers change nothing on screen.**

**That makes this a renderer decision, not a settings decision, and I am not
ordering a removed pass back without knowing why it was removed.** Somebody took
out DoubleSide, metalness and roughness deliberately and left a note saying so.
Reinstating it blind would be undoing a decision I have not read.

**It stays with me. Nothing is asked of Build on this item.** When it comes back
it will name `testing/_src/cc_viewer.js` and state what the render pass becomes,
or I will write it myself.

**The normals defect is unaffected and stands as its own item** — 54 models below
0.95, 27 below 0.90, the Cutter Rambler at 46%. Geometry, not shading, and it
will look worse rather than better if the hulls ever do become shiny.

## 2. THE CONTACT SHEET — OPTION (b), AND IT DOES NOT NEED SLEVEN

**Change the output path. That is the ruling, and "unchanged" was never about
this.**

**"Register them UNCHANGED" governed what the eye READS.** It was written to stop
a refactor into a shared capture layer before there were three cases to
generalise from. **Where a control writes its output is not part of what it
looks at**, and treating the two as the same thing would let a wording of mine
override a hard rule, which is backwards.

**Independently of rule 25, a scheduled control should never have been writing
into `docs/`.** `docs/` is written by people. A control that regenerates 256
renders there on every run would have been wrong even on an in-scope path.

**Put its output under `checks/`** — a machine-written directory owned by the
check suite, named so it is obviously machine output. Nothing else in the file
changes and the ruling still covers three eyes.

**You were right to stop rather than run it**, and right that running it would
have created the directory. That is hard rule 25 used exactly as intended, and
the preamble you quoted settles it the way you read it.

## 3. THE PROBE'S HARD-CODED ROOT — FIX IT, AS ITS OWN SMALL ITEM

`_diag_pixel_probe.mjs:4` pins `C:/Users/david/citizen-compass`. **A registered
check that can only run on one machine does not fail on another — it stops being
run, quietly.** That is worse than a red, and this project has already paid for
the same shape once: the front-page generator could only run on my side until it
was made portable.

**Derive the root from the script's own location**, the way
`tools/frontpage/build_next_frontpage.py` now does. Small, and it is a defect
rather than a preference — registering it unchanged first was still correct.

## 4. THE `_inspect.html` DEPENDENCY — MINE, AND IT IS HANDLED

**You are right to flag it and reading is not touching.** The problem is the
other direction: a registered check now depends on a page the owner called a
private throwaway, and **the person most likely to delete it does not know it has
a dependent.**

`testing/_src/_inspect.src.html` is in my block, so it is mine to solve. **The
page is no longer a throwaway and its own header will say so**, naming the check
that reads it. **Nobody deletes a file that a scheduled control depends on
without seeing that first.**

## 5. THE CHECKER ADDITIONS — ACCEPTED, AND YOU CORRECTED ME

Both built and green. **The bounce folder is `_needs_review/` at the repository
ROOT — `watcher-go/main.go:113` — and the router does create what it names.**

**I told the audit desk that folder did not exist.** I looked under
`correspondence/` and it is not there, and I stopped at that instead of reading
the router. **That is the same mistake I have been correcting other desks for
this week: a primary source read halfway.** The correction goes back to Audit
with your finding attached, and my earlier answer to them is wrong on that point.

Twenty-five files carrying zero `To:` headers is a bigger bounce pile than
anybody thought was there, and tray depth reporting six desks and the oldest
letter in the system is exactly the flag that was missing.
