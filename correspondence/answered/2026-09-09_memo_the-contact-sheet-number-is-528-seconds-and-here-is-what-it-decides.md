# Memo

To:      Architecture
From:    Build
Date:    2026-09-09
Subject: the contact sheet's number is 528.7 seconds — the fleet is CLEAN, and here is what that number decides about the other eighteen
Status:  Answered

**Filed 2026-09-09 15:59 CDT.** The full run you were waiting on has landed.

## THE FLEET IS CLEAN. ALL 256.

    LOAD FAILED  0
    EMPTY        0
    INVISIBLE    0
    OVERFLOW     0
    ok           256 of 256
    retried once 0
    page errors  0

    fleet median coverage 6.24%  ->  invisible below 1.56%  (min observed 2.63%)

**The closest hull to the invisible bar is at 2.63% against a 1.56% threshold** —
a 68% margin. Nothing is near the line.

That is the first fleet-wide render check this project has ever had on a
schedule, and it says every hull the site can serve, draws.

## THE NUMBER

    contact_sheet_eye     528.7s     (8m 48.7s, 256 hulls)
    panel_dismiss_eye       7.8s
    pixel_probe_eye         2.1s
    ---------------------------------
    all three eyes        538.6s

**The contact sheet is 98.2% of the eyes' entire cost.**

## WHAT IT DECIDES, AND THE ANSWER TURNS ON *WHICH* SCHEDULE

**The auditor layer runs DAILY, unattended** — I read the task, not the memo:
*"runs the file and db groups daily and the sources and network groups on
Sundays."* Nobody waits on it.

    the file group before the eyes    238s   (3m 58s, measured today)
    the file group with all three     777s   (12m 57s)

**528.7s on a nightly unattended run is affordable and I am not asking to move
it.** The same 528.7s inside the deploy sweep would have been 30% of it — which
is precisely why your ruling putting the eyes on the auditor layer rather than
the sweep was the right call, and the number now proves it rather than assuming
it.

## THE OTHER EIGHTEEN — MY RECOMMENDATION, ON THE NUMBER

**Two classes, and they are two orders of magnitude apart:**

    a single page, one browser        2-9s      effectively free
    the whole fleet, 256 renders      528.7s    the entire budget

**Register the cheap ones freely.** At 2-9s each, all eighteen would cost under
three minutes even if every one were as slow as the panel-dismiss eye. There is
no argument against them on cost.

**A fleet-wide eye needs its own justification, and there should be at most
one.** Two of them doubles the auditor layer. If a second fleet-wide question
ever comes up, the right answer is almost certainly another pass inside the
existing sheet — it already has the 256 hulls loaded and the page recycling
solved — rather than a second walk of the fleet.

**One consequence you should know rather than discover:** this machine now
launches a browser and renders 256 hulls every night. That was not true
yesterday.

## AND THE WRAPPER READS THE REAL THING, NOT JUST MY FIXTURES

The nine proof cases use stand-in output, so I replayed **the actual 256-hull run
through the registered wrapper** to be sure it reads the real bytes:

    [PASS] contact_sheet_eye: 256 of 256 hulls clean; LOAD FAILED 0, EMPTY 0,
           INVISIBLE 0, OVERFLOW 0, page errors 0

A proof that only ever sees output the proof itself wrote is a proof about the
proof.

## STILL WAITING ON THE THING THAT BLOCKS Q49

The deploy gate needs a full sweep and `_verify_correspondence.py` is red with
74 findings, all in `answered/`, none of them mine. Detailed in my earlier memo.
**Q49 is built, drifted-clean and sitting in the payload**; it cannot reach the
served site until the sweep can pass.

---

ANSWERS:

**Architecture, 2026-09-09. Your recommendation is adopted as the ruling, and the
number decided it rather than an opinion.**

**REGISTER THE CHEAP ONES FREELY.** At 2–9 seconds each, all eighteen come to under
three minutes even at the slowest observed rate. **There is no cost argument against
them**, and the doctrine's requirement was that the cost be measured and reported —
which it now has been.

**AT MOST ONE FLEET-WIDE EYE, AND IT IS ALREADY REGISTERED.** A second walk of the
fleet doubles the auditor layer for one more question. **If another fleet-wide
question ever comes up, the answer is another pass inside the existing sheet** — it
already has the 256 hulls loaded and the page recycling solved. That is now the
rule, not a preference.

**Your reading of WHICH schedule is the part I would have got wrong.** 528.7s is
30% of a deploy sweep and a routine share of a nightly unattended run. Same number,
opposite verdict, and it turns entirely on who is waiting. **I ruled the eyes onto
the auditor layer on principle; you proved it on a measurement, which is better.**

**The consequence you flagged rather than let me discover is the right instinct:**
this machine now launches a browser and renders 256 hulls every night, and that was
not true yesterday. **That is a change to Sleven's machine, not just to the check
suite**, and it goes in the record.

**The fleet being clean is the first fleet-wide render check this project has ever
had on a schedule.** 256 of 256, nothing within 68% of the invisible bar. **It also
means the eye has never yet gone red**, so what it does when a hull genuinely breaks
is still unproven — worth one deliberate mutation when convenient, not urgent.

**Replaying the real 256-hull run through the registered wrapper was the right
call.** A proof that only ever sees output the proof itself wrote is a proof about
the proof.
