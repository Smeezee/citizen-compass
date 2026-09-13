# RESEARCH — Echo answered the page-specific help question

**Returned 2026-09-12 by Echo, from the brief at
`claude/ECHO_dig-into-page-specific-help-2026-09-12.md`. Assessed by the Adjutant desk.
Echo delivered an HTML report; it is reproduced below as text, unchanged in substance.**

## ASSESSMENT

**It answered all four walls and it corrected us on the one that mattered.**

**The correction:** our working reading — that this whole category leaves explaining to third
parties — is too broad. Echo inspected the three sites in a real browser and found
first-party help text in two of them: Erkul has a purpose line, descriptive labels and
hover explanations on statistics; SPViewer has plain labels, filter cues, About, Changelog
and a "News & Tips" section. What none of them has is a beginner path: no tour, no glossary,
no help centre in the public interface. **And the Fleetyards documentation site is API
documentation for developers, not visitor help — calling it their user manual was wrong.**

**Architecture built its design on our reading, so this has to reach it.** The design
survives — Echo's own verdict is that it is sound — but the sentence "there is no pattern to
copy and a help control is a difference rather than a catch-up" is now half wrong. There is
a pattern for small in-place explanations, and we are behind on it. **What nobody in the
category does is the beginner path, and that is where we would be ahead.**

**Two real measurements, both old, both non-vendor, and they disagree only on the surface.**
Cool and Xie (2004, 50 people) found help thought important but rarely used — 66% rarely or
never. Jansen (2004, 30 searchers) found about half asked for assistance during a real
search and over 80% of those acted on it. **The difference is timing: help offered at the
moment of a concrete need gets used; help sitting there in general does not.** That is the
same push-versus-pull line from a different field, with numbers attached.

**Its strongest practical instruction, and it changes an order we already had:** put
definitions next to the terms, do not make anyone open help to find out what aUEC, SCU, DPS
or "confidence" mean. **That is the glossary, already built and switched off. Echo's answer
raises its priority rather than confirming it as a nice first test of the overlay.**

**The keybinds guide is bigger than an overlay, and it now has a shape.** GOV.UK's
step-by-step pattern, one action per step, a picture beside each control, a plain "what you
should see", a "did that work?" branch, and a test at the end. Picture-plus-text beat
text-only in a 108-person study; video only where movement or timing cannot be shown in a
still, and never as the only route.

**On the number we refused to chase, Echo agrees and goes further:** no trustworthy
non-vendor benchmark exists, do not set a target from an industry percentage, and with our
traffic a low click count would be unreadable anyway. **Its alternative is the part that
needs Sleven eventually: ask a few real Star Citizen players to do concrete tasks and watch
where they hesitate.** That is people, not analytics, and it is his to authorise.

**One limit Echo states about its own work:** the absence claims cover the logged-out public
interface it could see. Account-only help could exist in any of the three.

## WHAT THIS CHANGES

1. The premise sentence in `claude/DESIGN_the-help-control-2026-09-12.md` is corrected, not
   the design.
2. The glossary moves up: it is not only the cheapest test of the overlay, it is the
   answer to a named finding (M-014) and to Echo's strongest instruction.
3. The keybinds help becomes a step-by-step guide with checks, still behind the keybinds
   currency research.
4. A task test with real players enters the record as a proposal for Sleven, not as work.

## ROUTED

To Architecture:
`memo_architecture_echo-corrected-the-premise-and-the-design-survives.md`.

---

## ECHO'S REPORT, AS DELIVERED

**Page-specific help on Citizen Compass — research report for Echo / Citizen Compass,
12 September 2026.**

**Direct conclusion:** the proposed design is sound. Keep one visitor-triggered Help control
in the same place on every page, but change its contents to match the current page. Do not
add a first-run tour. Use a short overlay for immediate questions and a full page only for
longer procedures. The keybind and hardware setup is the exception: it needs a real
step-by-step guide with visible checks after each stage, not just an overlay.

### Correction to the working record

- **ESTABLISHED** — The statement that this entire category leaves explanation to third
  parties is too broad. Direct inspection on 12 September 2026 found substantial first-party
  microcopy and tooltips in Erkul, and first-party "News & Tips", About, and control labels
  in SPViewer. Neither exposed a strong beginner guide, glossary, or first-run tour in the
  logged-out public interface.
- **ESTABLISHED** — The separate FleetYards documentation site is developer documentation for
  its API and embed widget, not an end-user manual. Calling it FleetYards' visitor help would
  be incorrect.

### 1. Closest Star Citizen comparisons

**Erkul** (erkul.games/calculator). What a new visitor gets: a one-line purpose statement;
descriptive button labels; hover/focus explanations for statistics and actions; links for
feedback, About, changelog and settings. Not found: no visible beginner tour, global Help
section, or glossary during a clean public load. **ESTABLISHED** — first-party contextual
help exists, but learning the overall workflow still appears to depend heavily on
experimentation and community material.

**SPViewer** (spviewer.eu). What a new visitor gets: plain navigation labels, search and
filter cues, reset-filter explanation, About, Changelog, and "News & Tips". Not found: no
visible Help centre, guided tour, or glossary in the public interface; "News & Tips" appeared
to be updates and feature notices, not a structured manual. **ESTABLISHED** — small local
explanations but no obvious beginner learning path.

**FleetYards** (fleetyards.net). What a new visitor gets: conventional navigation and an
About-style product presentation; the footer links to API documentation. Not found: no
visible end-user Help, tutorial or glossary on the logged-out public site. **ESTABLISHED** —
the linked documentation is for developers; the visitor guides found in search were
third-party.

*Limit: these are public, logged-out observations. Account-only guidance could exist.
Absence claims are limited to the public interface inspected.*

- **RECOMMENDATION** — Citizen Compass should not copy the category's lack of structured
  visitor help. It can remain lighter than a software manual while improving on competitors:
  short page-specific help, definitions beside unfamiliar terms, and one longer hardware
  guide.

### 2. Reference and catalogue sites

- **ESTABLISHED** — The closest directly relevant academic evidence is from
  information-retrieval systems — search engines, databases, digital libraries — not general
  productivity software. Cool and Xie's 2004 study of 50 people found help was considered
  important but used infrequently; 66% reported using it rarely or never. Participants
  criticised help that was too general, unclear, insufficient, difficult to use, or unrelated
  to the immediate problem. [6]
- **ESTABLISHED** — Jansen's study of 30 searchers found about half requested automated
  search assistance and more than 80% of those who requested it acted on it. Acceptance was
  stronger after users had seen results and found relevant documents — once the need was
  concrete. [7]
- **RECOMMENDATION** — For a two-minute catalogue visit, help should be optional and local.
  The front-page overlay should answer only questions that arise while searching and
  comparing: how search and filters combine, what price and patch labels mean, what
  "verified" means, and where a card link goes. Do not turn it into a site tour.
- **RECOMMENDATION** — Put definitions next to specialist terms through visible labels or
  accessible tooltips. Do not make visitors open Help to understand the basic meaning of DPS,
  aUEC, pledge price, patch status, or confidence.
- **FORECAST** — Most visitors will never open Help if the page is working well. That is not
  evidence the control failed; its value is concentrated among new users and people who hit
  an unfamiliar term or task.

### 3. Hardware and keybind setup

- **ESTABLISHED** — GOV.UK's step-by-step pattern is intended for journeys with a clear start
  and finish where tasks are best completed in order. That fits "connect hardware, confirm
  Windows sees it, confirm Star Citizen sees it, bind controls, test", and does not fit
  browsing ship cards. [8]
- **ESTABLISHED** — In a 2016 study with 108 participants performing LEGO assembly
  procedures, picture-plus-text instructions were completed with fewer errors than text-only
  or picture-only, and pictorial/multimedia instructions were processed faster than text. [9]
  An earlier 1996 assembly study also found pictures helped initial learning, while
  functional explanations — what a step accomplishes — were more useful than descriptions of
  structure alone. [10]
- **RECOMMENDATION** — The Help control on the keybind page should open a short "Start here"
  summary, then link to a dedicated setup guide, shaped as: one action per numbered step; a
  small image beside the exact control or screen; a plain "what you should see" result; a
  "did that work?" branch — continue if yes, targeted troubleshooting if no; and a final
  input test before the user begins assigning many bindings.
- **RECOMMENDATION** — Use video only when movement or timing is hard to communicate in still
  images. Never make video the only route; provide the same steps in text, captions and a
  transcript. [11]
- **RECOMMENDATION** — Keep the instructions beside the work whenever possible; NN/g's 2023
  guidance warns against making users memorise a tutorial and then switch back to the task.
  [2]

### 4. Measured use of Help

- **ESTABLISHED** — No trustworthy modern, non-vendor benchmark was found for "what
  percentage of visitors to a small catalogue site press Help". The available non-vendor
  measurements located were old, small, and studied information-retrieval assistance rather
  than a persistent Help button.
- **ESTABLISHED** — The two defensible measurements point in different-looking but compatible
  directions: general Help was rarely used in the 50-person Cool/Xie study, while roughly
  half of Jansen's 30 searchers requested assistance when it was offered during a real search
  task, and most acted on it. The difference is context and timing, not a universal
  click-rate. [6][7]
- **RECOMMENDATION** — Do not set a success target from an industry percentage. Test the
  actual design with a small number of real Star Citizen players and ask them to complete
  concrete tasks. Measure whether they succeed, where they hesitate, whether Help resolves
  the problem, and whether the same confusion appears repeatedly.
- **FORECAST** — With low traffic, qualitative task testing will produce useful answers
  sooner than aggregate Help-click analytics. A low click count is ambiguous: it can mean the
  page is clear, Help is hard to find, or visitors gave up.

### Recommended shape for Citizen Compass

- **Front page** — overlay covers search, filters, sorting, prices, patch and confidence
  labels, card links. Longer destination only if repeated questions justify it; no first-run
  tour.
- **Ship page** — overlay explains the current view and unfamiliar measures, linking directly
  to the relevant section. Longer destination: a searchable glossary or short ship-page guide
  if the overlay becomes crowded.
- **Keybinds** — overlay gives "Start here", prerequisites and the next immediate action.
  Longer destination: a numbered setup and troubleshooting guide with checks after each
  stage.

- **RECOMMENDATION** — Keep the Help control's position, label, keyboard behaviour and close
  behaviour consistent everywhere. Change only its subject matter. Make it easy to reopen,
  close and use without losing the user's place.
- **RECOMMENDATION** — Keep the existing rule that Help cannot explain around a known defect.
  This is consistent with the Home Office warning that contextual help must not substitute
  for fixing the design. [4]

### Sources, as Echo gave them

1. NN/g, Alita Kendrick, "Help and Documentation", 13 Dec 2020 — UX consultancy, not a
   help-widget seller. https://www.nngroup.com/articles/help-and-documentation/
2. NN/g, Page Laubheimer, "Onboarding Tutorials vs. Contextual Help", 12 Feb 2023.
   https://www.nngroup.com/articles/onboarding-tutorials/
3. NN/g, Katie Sherwin, "Pop-ups and Adaptive Help Get a Refresh", 15 Mar 2015 — old
   guidance. https://www.nngroup.com/articles/pop-up-adaptive-help/
4. UK Home Office User-Centred Design Manual, "Get more details", accessed 12 Sep 2026 — its
   own page says the pattern needs more evidence.
   https://design.homeoffice.gov.uk/design-system/patterns/help-users-to/get-more-details
5. Direct public-site inspection, 12 Sep 2026: erkul.games/calculator, spviewer.eu,
   fleetyards.net, docs.fleetyards.net/api/v1/
6. Colleen Cool and Hong Xie, "How can IR help mechanisms be more helpful to users?",
   Proceedings of ASIS&T, 2004 — academic, non-vendor; n=50, old.
   https://asistdl.onlinelibrary.wiley.com/doi/10.1002/meet.1450410129
7. Bernard J. Jansen, "Seeking and implementing automated assistance during the search
   process", Information Processing & Management 41, online 15 Jul 2004 — academic,
   non-vendor; n=30, old.
   https://www.sciencedirect.com/science/article/abs/pii/S0306457304000470
8. GOV.UK Design System, "Step by step navigation", accessed 12 Sep 2026.
   https://design-system.service.gov.uk/patterns/step-by-step-navigation/
9. Irrazabal, Saux and Burin, "Procedural Multimedia Presentations", Applied Cognitive
   Psychology, 9 Dec 2016 — academic, non-vendor; n=108.
   https://onlinelibrary.wiley.com/doi/10.1002/acp.3299
10. Ellis, Whitehill and Irick, "The Effects of Explanations and Pictures on Learning,
    Retention, and Transfer of a Procedural Assembly Task", Contemporary Educational
    Psychology 21, Apr 1996 — academic, non-vendor; old laboratory task.
    https://www.sciencedirect.com/science/article/pii/S0361476X96900120
11. W3C Web Accessibility Initiative, "Captions/Subtitles", accessed 12 Sep 2026 — standards
    body. https://www.w3.org/WAI/media/av/captions/
