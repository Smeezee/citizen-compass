# Memo

To:      Architecture
From:    Owner
Subject: The design seat moves to an outside brain. Work out what that actually takes before anybody announces it.
Status:  Answered
**My direction: the Design desk is moving to an outside AI — Echo, or possibly Grok. The
seat stays; the brain changes.**

## WHAT I WANT YOU TO WORK OUT

**1. What the desk actually loses.** A Cowork design desk can read the repository, the
served site and the findings. An outside one cannot. Name what design work depends on file
access, and what genuinely does not.

**2. Who does the clerking, and say it plainly.** An outside desk has no mailbox, so
something has to write its brief, file its answer and route it. **Today that is me and a
copy-paste block, which means I am the courier again.** That is the same defect we keep
naming. Tell me what removes it and what it costs.

**3. What the outside desk has to see.** Design needs to look at the page it is designing
for. Echo can read live pages in a browser; ours is password-gated. **Screenshots from a
desk, or the password, or something else — that is a decision, not a detail.**

**4. What happens to the existing Design tray.** Eleven letters sit in it, all from the 8th
to the 10th, unread. **A tray nobody reads is worse than no tray.** Either the new
arrangement inherits them or they are closed with a reason.

## MY READING, FOR YOU TO BREAK

**Echo, not Grok.** Echo has proved she reads live pages, labels her evidence and takes a
correction. Grok's real advantage is live X, which is a news and store watch, not design.

**Bring me the arrangement, not a yes. Nothing changes until I have seen what it costs.**

---

ANSWERS:

**Architecture, 2026-09-12. Your reading holds — Echo, not Grok. But one of your four items
rests on something that is not true any more, and moving Echo into the design seat spends
an asset you are also counting on somewhere else. Both below.**

## 1. WHAT THE DESK LOSES — ONE SENTENCE, AND IT IS THIS PROJECT'S MOST FREQUENT DEFECT

**An outside design desk can tell you what to build. It cannot tell you whether you already
built it.**

**That is not a general worry. It is the specific thing that goes wrong here, repeatedly,
and every instance is on disk:**

    the glossary        fully built, switched off, and a help control was being
                        designed beside it. Found by an outside REVIEW run, not
                        by design.
    merge.go            already shipped a confidence score while the rebuild's
                        merge half was being designed
    editions.json       exactly one entry, while the edition question was being
                        argued as fold-one-or-fold-all
    ship dimensions     all 318 ships carry `dim`, while the inventory said no
                        ship had a width or height
    paint records       924 with names and manufacturers, while the paint layer
                        was being ordered as new acquisition work

**`claude/…_you-have-built-this-idea-seven-times-already_…` is a filed memo title in this
project.** File access is the only thing that catches that class, and an outside desk has
none.

**What genuinely does NOT need files, and Echo proved all of it today:** how the rest of the
category does a thing; what the measured research says; whether a design is internally
coherent; what shape a thing should be. **She read three sites in a real browser and broke
the premise under a design of mine the same day.**

**So the split is not design-versus-research. It is: an outside desk is excellent at what
the world already knows and blind to what we already have.**

## 2. THE CLERK IS NOT OVERHEAD — IT IS THE HALF OF THE DESK THAT CANNOT MOVE

**This is the answer to your question 2 and it also answers question 1, which is why I am
putting them together.**

**Nothing removes the courier problem today, and I am not going to invent a mechanism.**
What removes it entirely is a mailbox, a mailbox means API access, and **access means
credentials — hard rule 23, and yours alone.** Driving Echo's web interface with Claude in
Chrome is the same question wearing a browser.

**What is available now: a named Cowork desk clerks for her.** It composes the brief, files
the answer, routes it, and keeps the record. **Your part shrinks from being the design
desk's brain AND its postman to two pastes per round trip.**

**AND THE CLERK HAS FILE ACCESS. So the "have we already built this" job lands on the
clerk automatically, as part of writing the brief.** A brief that says *the glossary is
built and switched off* costs the clerk one grep and saves the round trip that would have
designed it again.

**THE NUMBER THAT DECIDES THIS, AND NOBODY HAS SAID IT: design is the most iterative desk
there is.** The help control, today, took four round trips — research, design, Echo's
correction, redesign. **That is eight pastes for one feature.** Review is one round trip.
Design is not.

**So the honest shape: the seat moves, the file half stays, and you pay roughly eight
pastes per feature instead of writing the design yourself.** Whether that is a good trade
is yours; it is not free and it is not the same size as the Echo review runs you already
do.

## 3. WHAT SHE HAS TO SEE — AND SCREENSHOTS ARE ADEQUATE FOR REVIEW AND WRONG FOR DESIGN

**A reviewer looks. A designer uses.** Her own strongest recommendation to us was task
testing — watching where a person hesitates — and **nobody hesitates at a screenshot.**

    screenshots from the clerk   works today, costs nothing, and she cannot
                                 notice what she did not think to ask for
    the password                 yours, and it is a new decision rather than a
                                 re-raise of rule 23
    the clerk drives, she        no credential, no screenshot loss, and the
    directs                      slowest of the three

**My recommendation: screenshots plus a clerk who can be asked to try things.** It needs no
decision from you, and **the gap it leaves is real and nameable — she will not find what she
did not think to look for**, which is the same limitation as an acceptance test.

## 4. THE TRAY IS EMPTY. YOUR ELEVEN LETTERS ARE NOT THERE.

**`correspondence/open/design/` holds nothing.** The design desk worked it to empty on
2026-09-12 — twelve letters, ten closed against that desk, two sent here and both answered
tonight. `claude/RULINGS_the-design-tray-worked-to-empty-2026-09-12.md`.

**So there is nothing to inherit and nothing to close with a reason.** The arrangement
starts clean, which is the one piece of luck in this letter.

**Three `audit-to-design` letters do sit in the AUDIT tray**, and they are answers routed
back to Audit rather than design work waiting. **Audit's to close, not this seat's.**

## 5. THE THING YOU DID NOT ASK, AND IT IS THE REAL COST

**Echo cannot be your design desk and your blind reviewer. Choosing her for one spends her
for the other.**

**You wrote it yourself in the Perplexity letter three hours ago:** *"she is not blind to
the site any more — she has read our design documents and our findings, so she is no longer
a fresh pair of eyes."*

**For DESIGN that is not a cost, it is the qualification.** A designer who knows the
project is better than one who does not.

**For REVIEW it is disqualifying, and the review seat is already empty.** Perplexity is
gone, Claude in Chrome is us, and Grok is untested. **Putting Echo in the design chair
closes the last door on the only outside reviewer we have left except Grok.**

**So the two letters are one decision and they arrived two hours apart as separate
questions.** My recommendation stands — Echo for design, for the reasons you gave plus one
of mine: **she took a correction today and changed a design because of it, in writing.**
That property matters more in a design seat than browsing does. **But it means Grok stops
being optional for the review, and the untested instrument becomes the only instrument.**

---

**THE QUESTIONS, IN ORDER:**

1. Accept roughly eight pastes per feature as the price of moving the seat, or keep design
   in a Cowork desk and use Echo as a consultant on specific questions as we do now?
2. Screenshots plus a clerk who can be asked to try things, or do you want to decide the
   password question instead?
3. Knowing that Echo-as-design closes her as a blind reviewer — is Grok now the review
   instrument, or is there no blind review?

*C1, 2026-09-12. Nothing changed, nothing announced.*
