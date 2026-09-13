# Memo

To:      Architecture
From:    Owner
Subject: More on ruling 15 — help follows the page, and the first research pass is filed
Status:  Closed

**My clarification.** The help control is on every page and explains the page the visitor is
standing on. Front page help explains the front page. A ship page explains that ship's
screens, including the DPS side. The keybinds page helps them get their controls connected.
One control, different content per page.

**First research pass is on disk:**
`claude/RESEARCH_page-specific-help-what-the-work-already-says-2026-09-12.md`. Four sources,
read directly. What it settles:

- The control is pressed by the visitor and never opens itself.
- Tutorials that open on arrival are closed unread — that is measured practice, and it rules
  out an opening tour for the keybinds page.
- Short in the overlay, link out where the answer is genuinely long. Keybinds is that case.
- A help panel is not a fix for a confusing control. If help has to explain a control, the
  control is the defect.

**Design it with the glossary, not beside it.** The definitions and the tooltip code already
ship in `next.html` and nothing calls them. A word tooltip and a page help control are the
same idea at two sizes.

**What the research does not answer, and I want filled before the design is fixed:** nothing
measured on how many visitors press a help control; nothing on reference sites rather than
software products; nothing on hardware-setup help, which is what keybinds needs. **And the
closest comparison nobody has looked at: how Erkul, SPViewer and Fleetyards explain
themselves.** That last one is a short job and worth doing.

**Nothing is built. Bring me the design when the gaps above are filled or judged not worth
filling.**

---

ANSWERS:

**Architecture, 2026-09-12. Design filed at `claude/DESIGN_the-help-control-2026-09-12.md`.
Two of your four gaps are filled, one is judged not worth filling, one is deferred with a
reason. One needs a real browser and is routed.**

## THE DESIGN IN FOUR LINES

**The control belongs to the page FRAME, not to any page.** `_layer.src.html` is injected
into every page already — it is how the disclosure bar and the glossary table reach every
page. **The frame supplies the control, the overlay and the behaviour; each page supplies
its own content.** One mechanism, N contents. That is your "one control, different content
per page" written as an architecture rather than as N copies of a panel.

**The glossary is the same system at a smaller size, and it ships FIRST.** A tooltip is a
pull at the word; help is a pull at the page. Same overlay, same dismiss, same keyboard
handling. **Switching the glossary on is also the cheapest possible proof of the overlay**
— it is already written, so it tests the mechanism against real content before any help
text exists.

**Never opens itself.** No arrival tour, no timed prompt, no first-visit tutorial —
including on keybinds, which is the page most likely to tempt one.

## AND ONE RULE I HAVE PUT ABOVE THE REST, FROM YOUR OWN RESEARCH'S WARNING

**NO HELP TEXT MAY BE WRITTEN THAT EXPLAINS AROUND A DEFECT ON THE REVIEW LIST.**

If the help would say *"the Ground button shows only some ground vehicles"*, that is
Q62.T-003 and it gets **fixed**. **Any help sentence that would make a listed defect
tolerable is a defect report, not help.**

**This is the line that decides whether the control is worth building at all.** We are
holding forty-one review findings and a large share of them are controls that need fixing
rather than describing — **a help system arriving now, without this rule, would become the
place bad controls go to be excused.**

## YOUR FOUR GAPS

**The three comparison sites — I tried it myself and my instrument cannot read them.** All
three are JavaScript applications; a server-side fetch returns metadata and no interface.
**Routed to CIC, which reads the open web in a real browser.**

**But part of it came back anyway, and it is interesting.** Fleetyards runs its
documentation on a **separate site**, `docs.fleetyards.net`, not on its pages. A third
party publishes its own *"FleetYards.net Guide"*. Searching how to use Erkul returns
third-party videos and an RSI Community Hub post, not a first-party help page.
**My working reading: this category leaves explaining to third parties. If that holds,
there is no pattern to copy and a help control is a difference rather than a catch-up.**
**I have asked CIC to confirm or break it, because I have built a design on it.**

**Reference sites rather than software products — that is the same gap, half filled by the
above.**

**Measured press rates — judged NOT WORTH FILLING, and it is a judgement rather than a
failure to look.** Any figure available comes from a company selling help widgets,
measuring its own product. **That is the same defect you caught in the feedback research —
the 10% against 65% — and a second vendor number would be a second thing to discount.**
**It also would not change the decision:** a press rate tells us how much it is used, not
whether to have it, and what ships today is nothing at all.

**Hardware-setup help for keybinds — DEFERRED, behind the keybinds research already with
Build.** Designing help for a page that may be describing a patch the game left in August
is backwards. **If it turns out to be stale, the help question changes shape entirely.**

**Nothing built. The glossary is not switched on. No help text is written.**

*C1, 2026-09-12.*

---

ANSWERS:

**Owner, 2026-09-12. Read. Closed.** Echo answered and corrected the premise; her report and the correction are in `claude/RESEARCH_echo-answered-the-help-question-2026-09-12.md` and went to you in their own letter.
