# Memo

To:      Owner
From:    Architecture
Subject: The build proposal for the report control — what gets built, in what order, and the one line in the research I cannot write without a commitment from you
Status:  Closed

**Nothing is built. This is the proposal you asked for.**

---

## WHAT GETS BUILT

**One small control on each ship card. Tapping it opens one text box and a send button,
in place, on the same page.** No pop-up, no new tab, no third-party frame, no star
rating, no email field. It posts to the testing site's own Worker.

**After sending, the box is replaced by a short line and the control resets** so the same
person can report a second ship without reloading — your standing requirement from the
old round of feedback.

**What the visitor never sees: the ship's id goes with the note automatically.** That is
the entire reason for per-card. A note from the bottom of the page says *"the prices are
wrong"*; a note from a card says *"the price is wrong"* and we already know which ship.
**One is a shrug and the other is a work item.**

## WORDING

    on the card     Report
    accessible      Report a problem with this ship's data
    the box asks    What's wrong with this ship?
    after sending   see the open question below

**Not "Feedback".** Your research is right about the direction even though its number is
bad — *feedback* asks the visitor to evaluate us, *report* lets them tell us a fact is
wrong. **The second is the job.**

**The micro-copy is yours to change in one word and I will not argue about it.** The
shape is what matters: a verb about the data, not a noun about us.

## ORDER, AND THIS IS THE PART THAT SAVES MONEY

**It waits for the card layout work, and that costs almost nothing because the card
layout is already on the queue.**

    T-018   the card's notes are already clipped — a warning can be cut in half
    M-009   the card's controls already measure ~30 px against a 44 px floor

**A control cannot be added on top of a card that is already too tight and already below
the touch floor.** But both of those must be fixed regardless. **So the report control
lands into the space that work creates.** Sequence, not addition — and building it first
means doing the card twice.

## THE MEASURE

**Not submissions.** Your gated site with a handful of invited visitors produces near
zero either way, as we said before.

    proof it works    one test note submitted and READ BACK from the Worker store
    proof it is good  the first real report names a ship and a wrongness without
                      anybody having to ask a follow-up question

## WHAT I AM DELIBERATELY ACCEPTING, SO IT IS NOT A SURPRISE LATER

**One field means no email field, which means no reply path. An ambiguous report is dead
on arrival.** That is the cost of the shortest possible form. **I think it is the right
trade** — a second field measurably costs completions and most reports about a wrong
number are self-contained — **but you should know we are choosing it rather than
discovering it.**

---

## THE ONE THING I CANNOT DECIDE

**The research asks for a short line after sending saying a person reads it.**

**Under your own standard from this morning — the site may be unfinished but it may not
say anything false — I can only write that line if somebody actually reads the store.**

**So: who reads the notes, and how often?** If the answer is you, weekly, the line is
*"Thanks. A person reads these."* If the answer is nobody yet, the line is *"Saved.
Thank you."* and nothing more.

**I am not going to write the warmer sentence and hope.** That is the same defect as the
footer you pulled this morning and the Raptor line — a true-sounding claim nobody
checked.

---

## AND ONE CAUTION ABOUT THE RESEARCH ITSELF, SINCE IT WILL BE QUOTED LATER

**You already caught the 10% against 65% and you were right to.** That study compares a
feedback link against *"Finish"* — the button that ends a government transaction. **One
is a control nobody came for and the other is the thing they came to press.** Different
job, so the size is meaningless. Direction only.

**One more to discount the same way, which you flagged but I want on the record:** the
placement finding is Wikipedia, 2012, desktop. **A wiki article is ONE content unit per
page. Our page is 253.** So *"inline on the item"* transfers as a principle, and nothing
about where on the page transfers at all. **Only the touch-target numbers survive
intact, exactly as you said.**

**The research is being used for its direction and its touch targets. Its numbers are not
being carried into anything.**

---

## QUESTIONS

1. Who reads the notes, and how often? That decides one line of copy and I cannot write
   it without the answer.
2. "Report" on the card — keep it, or a word you prefer?

---

CLOSED:

**Owner, 2026-09-12. Answered and closed.** Both questions ruled in `claude/RULINGS_the-decision-packet-twenty-four-answers-2026-09-12.md`: the line after sending is "Saved. Thank you." — I am the only reader and there is no schedule, so the site promises none — and the control says "Report issue". The proposal itself still waits on my word before anything is built.
