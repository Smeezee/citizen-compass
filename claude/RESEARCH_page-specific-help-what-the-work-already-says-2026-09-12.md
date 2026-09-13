# RESEARCH — page-specific help: what the existing work already says

**Filed 2026-09-12 by the Adjutant desk, at Sleven's order, after his ruling 15 (site-wide
contextual help). First pass, read directly from the sources named. Nothing built.**

## HIS CLARIFICATION, WHICH THIS IS BUILT AROUND

Help follows the page the visitor is standing on. On the front page it explains the front
page. On a ship page it explains that ship's screens, including the DPS side. On the keybinds
page it helps them get their controls connected. One help control, different content per page.

## WHAT THE SOURCES ACTUALLY SAY

**1. Help splits into two kinds, and ours is the second.** Nielsen Norman Group divides help
into *proactive* (shown before a problem) and *reactive* (available when the visitor goes
looking). Proactive splits again into *push* — shown whether you wanted it or not — and
*pull* — there when you reach for it. Their guidance: "Favor pull over push revelations. Make
help content accessible, but don't force users into it."
(Alita Kendrick, NN/g, 13 December 2020.) **A help control the visitor presses is a pull. That
is the shape Sleven described, and it is the shape the guidance supports.**

**2. Tutorials up front do not work.** NN/g reports that tutorials "interrupt users, don't
necessarily improve task performance, and are quickly forgotten", because people want to use
the thing rather than study it first — what they call the paradox of the active user. Their
"most important guideline" is help at the moment it is needed.
(Page Laubheimer, NN/g, 12 February 2023.) **This matters for the keybinds page: a
walk-through that opens on arrival will be closed unread; the same content behind a help
control, next to the step it explains, will not.**

**3. Help the visitor asks for beats help the system decides to show.** NN/g: user-initiated
overlays are "far less jarring and annoying to users than system-initiated pop-ups", and help
should be "available without interfering". They also note people distrust a system's guess
about what they need. (Katie Sherwin, NN/g, 15 March 2015 — old, and the principle is about
interruption, which has not changed.)

**4. A government design system reaches the same place and adds a warning worth keeping.**
The UK Home Office pattern recommends "small overlays containing help content for complex
interactions", easy to close and minimise, with a link to fuller help if the overlay does not
answer the question. Its research line: "Users find side-by-side guidance more helpful and
easier to use." Its warning: contextual help "shouldn't be relied upon to solve design
problems - services should always be simple and intuitive". **That page also says the pattern
needs improving and asks for evidence, so treat it as practice rather than proof.**

## WHAT THE DESK TAKES FROM IT

- **One control, same place on every page, pressed by the visitor.** Never opens itself.
- **Content is about the page you are on**, in Sleven's terms.
- **Short in the overlay, with a link to more** where the answer is genuinely long — the
  keybinds setup is the case where that will happen.
- **Easy to close, and it does not move the page around** while it is open.
- **A help panel is not a fix for a confusing page.** If the help has to explain a control, the
  control is the defect. That line should be in the entry, because we already have a review
  full of controls that need fixing rather than explaining.

## HOW IT MEETS WHAT WE ALREADY HAVE

**The glossary is the same family and is already built.** `next.html` carries term definitions
and working tooltip code that nothing calls (M-014). A term tooltip is a pull revelation at
the word; a help control is a pull revelation at the page. **They should be designed as one
system with two sizes, not two systems.**

## WHAT THIS PASS DOES NOT ANSWER

- **No measured numbers.** None of the four sources gives a figure for how many visitors press
  a help control, or whether page-specific help beats one help page. The guidance is
  consistent and the evidence behind it is qualitative.
- **Nothing found yet on reference sites specifically** — the sources are software products
  and government services, not catalogues someone browses for two minutes.
- **Nothing found yet on hardware-setup help**, which is what the keybinds page needs and is
  closer to a manual than to a tooltip.
- **Not searched yet:** how the game's own community tools (Erkul, SPViewer, Fleetyards) handle
  explaining themselves, which is the closest comparison we have.

## SOURCES

- NN/g, Help and Documentation (Usability Heuristic #10), 2020-12-13:
  https://www.nngroup.com/articles/help-and-documentation/
- NN/g, Onboarding Tutorials vs. Contextual Help, 2023-02-12:
  https://www.nngroup.com/articles/onboarding-tutorials/
- NN/g, Pop-ups and Adaptive Help Get A Refresh, 2015-03-15:
  https://www.nngroup.com/articles/pop-up-adaptive-help/
- UK Home Office Design System, Help users to get more details (undated):
  https://design.homeoffice.gov.uk/design-system/patterns/help-users-to/get-more-details
