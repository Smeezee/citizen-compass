# DESIGN — THE HELP CONTROL. Design only. NOTHING AUTHORISED.

**His ruling 15 and his clarification of 2026-09-12: one control on every page, explaining
the page the visitor is standing on. Pressed by the visitor, never opening itself.**

**The Adjutant desk's first research pass is
`claude/RESEARCH_page-specific-help-what-the-work-already-says-2026-09-12.md` and this
design is built on it rather than repeating it.** His four gaps are answered at the
bottom — two filled, one judged not worth filling, one deferred with a reason.

---

## 1. THE CONTROL BELONGS TO THE PAGE FRAME, NOT TO ANY PAGE

**`testing/_src/_layer.src.html` is injected into every page already.** It is how the
disclosure bar, the glossary table and the device panel reach every page today.

**So: the frame provides the control and the overlay. Each page provides its own
content.** One mechanism, N contents.

    the frame supplies    the control, the overlay, open/close, focus handling,
                          Escape, and the "one open at a time" rule
    each page supplies    its own help content, declared in the page source

**That is his "one control, different content per page", expressed as an architecture
rather than as N copies of a panel.** A second implementation on any page is the defect
this structure exists to prevent — rule 14.

## 2. THE GLOSSARY IS THE SAME SYSTEM AT A SMALLER SIZE, AND IT SHIPS FIRST

**His words: design it with the glossary, not beside it.**

    a glossary tooltip    a pull revelation at the WORD
    the help control      a pull revelation at the PAGE

**Same overlay, same dismiss behaviour, same keyboard handling, same one-at-a-time
rule.** The difference is what opens it and how much is inside.

**SEQUENCE, AND IT IS NOT NEGOTIABLE: the glossary is switched on FIRST.** `next.html`
already carries the definitions and the working tooltip code and nothing calls it
(Q62.M-014). **Building the help control while that stays switched off would leave two
half-built help systems**, which is exactly the collision the Adjutant desk named.

**The glossary is also the cheapest possible proof of the overlay** — it is already
written, so switching it on tests the mechanism against real content before any help text
exists.

## 3. WHAT IT DOES AND DOES NOT DO

    pressed by the visitor         always
    opens by itself                NEVER. No arrival tour, no timed prompt, no
                                   first-visit tutorial.
    moves the page while open      never
    closes on                      the control again, Escape, and a close affordance
    short in the overlay           yes, with a link out where the answer is genuinely
                                   long — the keybinds setup is that case
    one open at a time             a glossary tooltip and the help overlay never
                                   both stand open

**The no-arrival-tour rule is measured practice, not taste:** tutorials shown on arrival
are closed unread, and people want to use a thing rather than study it first. **It rules
out an opening walk-through for the keybinds page specifically**, which is the page most
likely to tempt one.

## 4. THE RULE THAT MATTERS MOST, AND IT IS A REFUSAL

**NO HELP TEXT MAY BE WRITTEN THAT EXPLAINS AROUND A DEFECT ON THE REVIEW LIST.**

The research's own warning: *contextual help "shouldn't be relied upon to solve design
problems"*. **We are holding forty-one review findings, and a large share of them are
controls that need fixing rather than describing.**

    if the help would say     "the Ground button shows only some ground vehicles"
    then the entry is         Q62.T-003, and it gets FIXED

**Any help sentence that would make a listed defect tolerable is a defect report, not
help.** It goes back to the queue and the help text is not written.

**This is the line that decides whether the help control is worth building at all.**
Without it, a help system becomes the place bad controls go to be excused, and it would
arrive at exactly the moment this project has a written list of bad controls.

## 5. WHAT EACH PAGE'S HELP IS ABOUT — HIS WORDS

    front page      what the front page is and how to find a ship on it
    a ship page     that ship's screens, INCLUDING THE DPS SIDE
    keybinds        getting the visitor's controls connected

**Not written here. Content is written when each page is stable**, and two of the three
pages are mid-repair.

## 6. WHAT IS NOT DESIGNED, DELIBERATELY

**The keybinds help.** It is gated on research item 2 — where that page lives, how
finished it is, and whether its content is current. **Designing help for a page that may
be describing a patch the game left in August is backwards**, and if it turns out to be
stale the help question changes shape entirely.

---

## THE GAPS — ANSWERED BY ECHO 2026-09-12, AND IT BROKE MY PREMISE

**Echo read all three sites in a real browser. Its verdict on this design: *"the proposed
design is sound."* The design does not change. The sentence it rested on does.**

### THE PREMISE WAS WRONG AND THIS IS THE CORRECTED ONE

**WITHDRAWN: *"this category leaves explaining to third parties, so a help control is a
difference rather than a catch-up."*** Too broad, and built on three search results and a
docs subdomain.

    Erkul        HAS first-party help — a purpose line, descriptive labels,
                 hover and focus explanations on statistics
    SPViewer     HAS first-party help — plain labels, filter cues, a reset-filter
                 explanation, About, Changelog, "News & Tips"
    Fleetyards   its documentation site is API DOCUMENTATION FOR DEVELOPERS.
                 Calling it their visitor manual was wrong.

**WHAT NONE OF THEM HAS IS A BEGINNER PATH: no tour, no glossary, no help centre in the
public interface.**

**So the position inverts. We are BEHIND the category on small in-place explanations, and
ahead of it only on the beginner path.**

**Echo's stated limit: these are logged-out public interfaces. Account-only help could
exist in any of them.**

### AND THE HALF WE ARE BEHIND ON IS ALREADY ON THE QUEUE UNDER OTHER NAMES

**This correction does not create a workstream. It re-labels one.**

    Q62.M-014   the glossary, built and switched off
    Q55.P5      confidence, source and patch on every card — Echo's
                "what does verified mean" in our own words
    Q62.T-022   the (*) marker in notes with no key in the legend
    Q62.T-008   a badge that claims a verification that did not happen

**Every one of those is a small in-place explanation, already ordered.** The help control
is the other half — the beginner path — and that is the part nobody in the category has.

### THE GLOSSARY IS PROMOTED. IT IS NOT THE OVERLAY'S TEST ANY MORE.

**Echo's strongest instruction, and it changes an order we already had: put definitions
next to the terms. Do not make a visitor open Help to find out what aUEC, SCU, DPS,
pledge price, patch status or "confidence" mean.**

**So the glossary stops being "the cheapest proof of the overlay" and becomes an answer in
its own right.** It still ships first — for a better reason than before.

### THE TWO MEASUREMENTS, AND MY REASON FOR REFUSING TO LOOK WAS WRONG

**I judged this gap not worth filling and said any figure would come from a company
selling help widgets. Two non-vendor academic measurements exist and Echo found them.**

    Cool & Xie 2004, n=50    help considered important; 66% used it rarely or never.
                             Criticised as too general, unclear, and unrelated to the
                             immediate problem.
    Jansen 2004, n=30        about half requested assistance during a real search;
                             OVER 80% OF THOSE ACTED ON IT. Acceptance was stronger
                             once the need was concrete.

**They look opposed and they are not. The difference is TIMING: help at a concrete moment
gets used; help sitting there in general does not.** That is the push-versus-pull line
from a different field with numbers attached — **and it is the strongest single argument
for putting definitions beside the terms rather than behind a control.**

**My conclusion survives and my reason does not.** No trustworthy modern non-vendor
benchmark exists for *"what share of visitors press Help"*, Echo agrees, and **no success
target may be set from an industry percentage.** But "there are no non-vendor numbers" was
wrong, and the numbers that exist are the ones that justify promoting the glossary.

**AND THE FORECAST TO KEEP:** most visitors will never open Help if the page is working.
**That is not evidence the control failed** — its value is concentrated in new visitors
and people who hit an unfamiliar term. **A low click count is ambiguous three ways: the
page is clear, Help is hard to find, or they gave up.**

---

## 7. WHAT EACH OVERLAY COVERS — ECHO'S SHAPE, TAKEN

    front page   how search and filters combine, what the price and patch labels
                 mean, what "verified" means, where a card link goes.
                 NO SITE TOUR.
    ship page    the current view and its unfamiliar measures, linking to the
                 relevant section rather than describing it
    keybinds     "Start here", prerequisites, and the next immediate action —
                 then a link OUT to the guide below

## 8. THE KEYBINDS GUIDE HAS A SHAPE NOW — STILL DEFERRED

**Still behind the keybinds currency research, for the reason in section 6.** Shape
recorded so it is not re-derived later.

**GOV.UK's step-by-step pattern**, which is for journeys with a clear start and finish
best done in order — *connect the hardware, confirm Windows sees it, confirm the game sees
it, bind the controls, test* — **and explicitly not for browsing ship cards.**

    one action per numbered step
    a small image beside the exact control or screen
    a plain "what you should see"
    a "did that work?" branch — continue, or targeted troubleshooting
    a final input TEST before the visitor starts assigning many bindings

**Picture-plus-text beat text-only on errors in a 108-person study (2016), and pictorial
instructions were processed faster than text.** An earlier assembly study found
**functional explanations — what a step accomplishes — more useful than describing
structure.**

**Video only where movement or timing cannot be shown in a still. NEVER as the only route
— always the same steps in text, with captions and a transcript.**

**Keep the instructions beside the work.** A guide the visitor has to memorise and then
switch away from is the tutorial failure in a different costume.

## 9. ECHO ENDORSED THE REFUSAL IN SECTION 4

**Independently, and against the same Home Office warning: help must not substitute for
fixing the design.** The rule stands and now has a second source behind it.

## 10. ONE THING THAT IS NOT THIS DESK'S — FILED AS A PROPOSAL, NOT WORK

**Echo's alternative to click counts: ask a few real Star Citizen players to do concrete
tasks and watch where they hesitate.** Whether they succeed, where they pause, whether
Help resolves it, and whether the same confusion repeats.

**That is people, not analytics, and it is Sleven's to authorise.** In his tray as a
proposal. **No work is planned around it and none should be.**

---

**Nothing built. The glossary is not switched on. No help text is written. No control
exists.**

*C1, 2026-09-12. Design only. Premise corrected by Echo the same day; the design itself
unchanged.*
