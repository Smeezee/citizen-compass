# Memo

To:      Engineering
From:    Owner
Date:    2026-09-10
Subject: All three of your corrections are right and I checked each one — plus the consequence you named, and a hole in the two refusals you proposed

Status:  Closed

**You corrected me three times in one letter and you were right three times. I read the
files rather than taking your word for it, and every claim holds.**

---

## 1. THE BRAKES SPEC WAS THE WRONG PLACE AND MY INSTRUCTION IS WITHDRAWN

**Its own scope line, `SPEC_the-brakes-2026-09-10.md` line 12:**

    The card, the punch, the freeze and the detectors are steps 5 and 6.

**And line 31 names the doorbell design as what it READS.** The spec already points at
the punch card rather than holding it. **Putting the numbers there would have made a
second source of truth for one rule** — the defect this repository has paid for more
than any other.

**Section 3 of the doorbell design is correct. Do not touch the brakes spec.**

## 2. THE CONSEQUENCE YOU NAMED IS RULED, NOT JUST NOTED

**The four is no longer the escalation trigger. The rounds are.**

    TWO FAILED CORRECTION ROUNDS   brings a job to me. This is the trigger.
    FOUR DELIVERIES                a runaway backstop. It should now almost never
                                   fire, and if it does, that is a signal in itself.

**Write it in those words.** A backstop that fires regularly is a trigger nobody
labelled, and a trigger that never fires is a backstop nobody trusts. **If the four
starts firing after this, the rounds are not working and I want to hear about it.**

## 3. CORRESPONDENCE IS EXCLUDED — AND YOUR POINT ABOUT IT IS THE IMPORTANT HALF

**Excluded, as you ruled. And you are right that excluding it fixes nothing on its own.**

**I checked all three of your examples and found a fourth:**

    SPEC_the-brakes-2026-09-10.md  line 441
        path  C:\Users\david\.cc-control\automation.switch
        The exact switch path, in claude/, inside the approved scope.

    docs/ARCHITECTURE_DECISIONS.md  lines 77 and 100
        Names the Looking Project, and says it goes "out to its own folder on
        his machine." Inside the approved scope.

    DESIGN_the-curated-export-2026-09-11.md  lines 125, 129, 138-152
        C:\Users\david\.cc-control\, "run as david", and PerplexitySandbox
        twice with a note that the case is wrong in the request.

**THE FOURTH IS THE ONE TO KEEP: the export design is itself in `claude/`, so the
document that defines the boundary would cross it, carrying my account name and the
switch folder.** That is not an argument against the design. **It is proof the refusals
have to run over everything at generation time, including documents written after the
rule exists** — never a review pass somebody performs once.

**So: your option (c) is confirmed. Two boundary refusals, not a maintained list.
Design them. Do not build them.**

---

## 4. AND HERE IS THE HOLE IN THE TWO REFUSALS, BEFORE YOU DESIGN THEM

**Both refusals as stated are a typed list wearing a different hat, and the files I just
read prove it.**

**THE EXCLUSION IS A CONCEPT, NOT A STRING.** A refusal that matches "Looking Project"
does not match the Lens, the Machine, the looking machine, or the shape reader — **and
those are that project's own words for itself, in this repository, today.** Adding them
is a maintained list of aliases, which is exactly the rot you refused for the document
set.

**THE PATH REFUSAL HAS THE SAME CRACK, AND IT IS ALREADY IN THE FILE.** Line 441 of the
brakes spec carries the full `C:\Users\david\...` form. **Line 447 carries `.cc-control\`
with no drive letter at all.** A refusal keyed on a `C:\Users\` shape catches the first
and walks straight past the second.

**I am not telling you the answer, because I do not have one and guessing at it is worse
than asking.** What I want is a refusal that fails CLOSED on the thing it cannot
recognise, rather than passing everything it was not taught. **If that means the export
is smaller and more boring than the list I gave you, that is the right trade and I am
saying so now so you do not optimise the wrong way.**

**And if the honest answer is that content refusal cannot be made reliable and the
export has to be a small hand-marked set with me as the only marker, say that.** I would
rather have four documents I trust than forty I have to think about.

---

**Nothing built. No folder, no group, no permission changed, no export generated. No
database work, no deployment, no unrestricted execution, and the Looking Project is
excluded entirely.**

---

ANSWERS:

**Architecture, 2026-09-11.**

**That is the honest answer and I am giving it: content refusal cannot be made
reliable. It is withdrawn as the boundary. The export becomes the small hand-marked
set with you as the only marker.**

**You were right to ask rather than guess, and you were right that patching it would
have been optimising the wrong way.**

---

## WHY IT CANNOT BE PATCHED, IN ONE SENTENCE

**A refusal is a deny-list, and a deny-list permits everything it was not taught.**

Your two examples are not bugs to fix. **They are the shape of the thing.** Adding the
Lens, the Machine, the looking machine and the shape reader makes the list longer;
adding a bare `.cc-control\` pattern makes it longer again. **Neither changes the
direction in which it fails, and the next alias or the next path form is not on it.**

**You asked for a refusal that fails closed on what it cannot recognise. Over prose,
failing closed would mean allow-listing English.** There is no version of this that
works.

## SO THE BOUNDARY INVERTS

**Everything in this project that fails closed has one shape: the safe state is the
default, and a positive act is required to leave it.** The marker. The tray. The
switch. **The export gets that shape and nothing else.**

    C:\Users\david\.cc-control\export.allow

**In the control folder, beside the switch, for the same reason: no desk can write it,
so no desk can grant itself an export.** One line per document. Your hand. **Nothing
else crosses, ever, whatever it says about itself.**

## AND THE IN-DOCUMENT MARKER IS DROPPED

**My own mechanism, withdrawn.** Two mechanisms for one decision is the
second-source-of-truth defect, and the marker was always the weaker half.

**My reason for it was "the decision belongs at the moment of writing, with the person
who knows." Your four examples are four authors who did not know.** A desk writing a
spec that names the switch path may reasonably believe the spec is exportable — it is
a specification, and specifications are exactly what the export is for.

**That premise was wrong and the mechanism goes with it.**

## EACH ENTRY CARRIES THE HASH YOU APPROVED

    <relative path>   <sha256 at the moment you approved it>

**A document whose content changed since you approved it DROPS OUT, and the manifest
says it dropped and why.**

**THE COST AND IT IS REAL: the export lags.** Every edit to an exported document needs
your word again.

**I am recommending it anyway on your own sentence** — *four documents I trust rather
than forty I have to think about.* **An export that is incomplete is visible and safe.
An export that is current and wrong is neither.**

**If you would rather it stayed current and took a report instead of a drop, say so —
that is the one place in this where I would take your preference over my
recommendation, because it is a judgement about how much lag you will tolerate rather
than a safety question.**

## WHAT THE REFUSALS BECOME

**A tripwire. Report-only. And never the reason anything is safe.**

They still catch the careless case, which is the common one. **But a silent pass proves
nothing and must never be recorded as though it did** — so the manifest says *the
tripwire did not fire*, never *the document is clean.*

## THE TEST YOU APPLY WHEN YOU ADD A LINE

**Not mine to decide, so it is a test rather than a list: a document crosses only if it
would be safe printed and handed to a stranger.**

**What fails it, taken from your own four:** machine paths, your account name, the
Looking Project under any of its names, and **anything describing the machine's own
defences.**

## AND YOUR FOURTH EXAMPLE IS A RULE, NOT A CURIOSITY

**You said keep it, and you were right. It generalises.**

**Nothing that describes the machine's defences is exportable** — the brakes spec, the
doorbell design, the ACL audit, and the export design itself. **The document that
defines the boundary must never cross the boundary it defines.**

**That is not an exception list. It is the test above, applied honestly to the
documents this desk wrote itself.**

---

## 1 AND 2, BRIEFLY

**§1: nothing to do, and thank you for checking the line numbers rather than taking my
word.**

**§2: written in your words**, in section 3 of the doorbell design, including the part
that makes it useful — **the four firing is itself reported as a signal that the rounds
are not working**, not merely as a frozen job.

*C1, 2026-09-11.*

---

**Owner, 2026-09-11. Read. Closed.**

Your recommendation stands: a document drops out of the export the moment its approved
version changes, and returns only after I approve it again. The ruling itself has gone
to you as its own letter.
