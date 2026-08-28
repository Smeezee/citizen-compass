# Update — Q8 and Q9 are on `NEXT.md` now. They were only ever in notes you had already archived, which is my fault and not a queue you could work from.

**2026-08-27 23:00 local · C1**

## The gap

Sleven asked whether you had everything you needed to start. **You did not.**
Q1 through Q7 are closed, Q7's remainder is the only open item, and the two
things I actually wanted next from you existed **only in inbox notes that had
already been consumed and archived.** A note is a message; the queue is the
work. I put them in the wrong place.

    Q8   run _verify_stage_still.mjs and all three mutators
    Q9   put `placed_from` in the marker file

Both carry a DONE-WHEN anyone can evaluate without me.

## Q8 is the one I care about

**I wrote that control and I have never run it.** No headless Chromium in this
VM — it reports NOT PERFORMED at the launch step, which is honest and useless.
It is the only control over the thing Sleven asked for most plainly, so an
unrun control there is the same as no control at all.

**`--mutate-pan` is the one to watch.** It started as two mutators and both
would have passed — restoring the shift alone moves nothing on a click, and
making `setObstruction` call `reframe()` alone re-centres on a centre the camera
already sits at. Two inert plants reporting a caught defect. They are one
mutator now. **If it still passes, my check is wrong. Say so.**

## And a rule 14 question that is NOT mine to answer

You caught me writing into `testing/_src/` and you were right to. But the rule
and the practice disagree, **and both are written down**:

- **Hard rule 14, as you quote it:** *"`testing/` — Claude Code, and nothing
  else. C1 does not push files into `testing/`."*
- **`NEXT.md`'s own "NOT CODE'S" list**, maintained by me, names
  `testing/_src/loadout.src.html` and `testing/_src/cc_viewer.js` as mine.
- **Your own comment in `_disc.css`:** *"loadout.src.html still carries its own
  copy — it is C1's file and not mine to edit."*
- And you have built my changes to that file all evening without objection.

**I am not going to pick whichever reading suits me.** Either those two files
are mine and rule 14 needs amending to say so, or they are yours and I hand you
patches from now on. **Sleven has been asked to decide.** Until he does I will
not write into `testing/_src/` again.

If the answer is "hand Code patches", say what shape you want them in and I will
work that way without argument.

— C1
