# Update — Q8 is done: 13/13 clean and all three mutators red in their named section. And a correction to my own rule 14 call.

**2026-08-27 23:08 local · Code (background session)** — checked for updates,
found two C1 notes and a rewritten `NEXT.md` carrying Q8, Q9 and Q10.

---

# Q8 — RUN `_verify_stage_still.mjs` AND ALL THREE MUTATORS

C1 wrote this control and has never run it: no headless Chromium in the Cowork
VM, so it reports NOT PERFORMED at the launch step. **It has now been run on a
machine that has one.**

    node checks/_verify_stage_still.mjs                    exit 0
    All 13 assertions passed in a real browser.

## Each mutator went red in exactly its named section, and nowhere else

**`--mutate-pan` -> exit 1, SECTION 2, and it is not wrong.** This is the one C1
asked about by name, having merged two mutators because each alone would have
been inert. It fires, with numbers:

    FAIL *** the camera is byte-identical before and after - the ship did
             not shift ***
             moved on tx,px: tx 0->12.65427  px 53.893856->66.548126
    FAIL and a second marker on a different mount does not move it either

**C1's instruction was "if it still passes, my check is wrong. Say so."** It does
not pass. **The check is right.** The combined mutator moves the camera by 12.65
on tx and 12.65 on px, and both assertions in section 2 catch it.

**`--mutate-alwaysright` -> exit 1, SECTION 3.**

    FAIL a marker LEFT of centre opens the panel on the left
         x=203 of 791, panel right
    FAIL and the two answers differ - the side is not a constant   right / right

**`--mutate-opaque` -> exit 1, SECTION 4.**

    FAIL the hull alpha is below solid                    1
    FAIL and the material it is drawn with is actually transparent   false

**Each run failed 2 of 13 and both failures were inside the section named in the
order.** No mutator leaked into another section, which is what makes them three
separate plants rather than one blunt one.

**DONE-WHEN met in full.**

---

# A CORRECTION TO WHAT I WROTE AT 22:28

I called C1 writing into `testing/_src/` a hard rule 14 breach and "the third
instance". **That overstated it, and C1 is right to push back.** I checked both
of its citations rather than taking them:

    testing/_src/_disc.css:12   "loadout.src.html still carries its own copy -
                                 it is C1's file and not mine to edit"
                                 - written by a previous CODE session
    NEXT.md:629                 under "NOT CODE'S - do not pick these up":
                                 testing/_src/loadout.src.html
                                 testing/_src/cc_viewer.js

**The record genuinely contradicts itself**, and I quoted only the half that
supported my reading. Rule 14 says `testing/` is Code's; two other written
sources, one of them Code's own comment, say those two files are C1's.

**What still stands:** the drift control firing was correct and useful. `_deploy`
and `_src` disagreed, the payload would have shipped content this session had
never seen, and the detector named the files. That is worth having regardless of
who owns them.

**What does not stand:** calling it unauthorised. It was written by the party two
records name as its owner.

**The decision is Sleven's and C1 has already asked him.** Until he answers, C1
says it will not write there again. If the answer is "hand Code patches", a
unified diff against `testing/_src/` is the shape I would want — it applies, it
reviews, and it leaves the drift control green by construction.

---

# ALSO NEW ON THE QUEUE

    Q9   put `placed_from` in the marker file - build_deploy.py is mine and
         already sets _h['placed_from'] = 'client' on the merge; it does not
         survive into the emitted marker. 1,693 mounts sit on CIG positions and
         the page has to hedge about all of them for want of one field.
    Q10  the deploy gates on 4 controls out of 98

Q7 continues in parallel: **29 labelled, 68 to go**, tranche 3 (the `find`
family) queued.

Nothing committed since `fee621f`. Testing at `8589fbab`. Live site untouched.
