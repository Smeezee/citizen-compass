# GATHER — everything this desk has designed for Citizen Compass, where it lives, and what state it is actually in

```
from    Design (C3), 2026-09-12
asked   by Sleven: gather the projects we worked on, keybindings and the
        other newer ones. The Looking Project is EXCLUDED by his
        instruction and appears nowhere below; he will ask for it
        separately.
scope   Citizen Compass only. Nine threads, 2026-08-28 to 2026-09-12.
method  every file path below listed on disk or read in the claude.ai
        project today. `NEXT.md` staged and searched directly. Nothing
        carried from memory.

```

**Read the state line before the description.** Two finished designs here have no
build entry anywhere in `NEXT.md`, and a third has a queue entry that was
satisfied two weeks ago and never closed. That is the most useful thing in this
document, and it is measured rather than impressionistic — the last section says
exactly how.

---

# 1. THE KEYBINDING BOARD — the live one

**STATE: working prototype, driven and accepted by you. Not deployed. Not in the
build's page list.**

**Where it is:** `design/keybindings/keys.html` — one file, 132,850 bytes.
Published as the artifact **"Keyboard First"**. `design/README.md` says in the file
itself that it is not production.

**What is settled, by you, in session:**

- **Tap lights the key. Hold opens it.** Your idea, built and accepted the same session. Tap gives a see-through tag naming the key and its first binding, ending "hold to open"; hold fills a bar across the keycap and then opens the detail. Let go early and it was a tap. This replaced click-to-open, which made every glance cost a panel you then had to dismiss.
- **"The key opens"** is the chosen readout — the key grows into the panel and the rest of the board drops to 22%. Beaten: glass at the key, no box at all, and a row ribbon you did not pick. Your stated reason for the winner is the room it leaves a future menu.
- **The glow is a soft bloom, not an outline** — your words, *"more of not the edge"* — and then pulled back again because it bled onto neighbouring keys.
- **The tap highlight is short.** You said one to one and a half seconds at most; it holds about eight tenths and fades.
- **Closing works.** Escape, the same key again, off the board, or the ×. Before that session there was no way to close it at all.
- **It works identically for the real keyboard and the mouse.** Pressing the physical G runs the same tap-or-hold test as clicking the drawn G.

**The one thing still yours:** the hold duration. The page carries a switch —
0.25s, 0.45s, 0.7s, 1s — and sits at 0.45s because nobody has picked.

**The turn that matters more than any of the visuals.** Four other people already
build a Star Citizen keybind editor, and one of them, free in a browser, already
has the "press a key and it tells you what it does" idea this desk had claimed as
its own. **So the design stopped being an editor and became a check-up:** you hand
it the map you already fly with and it tells you what is wrong with it — actions
you cannot reach without looking, real conflicts, binds for a ship you do not own,
things your Vulture needs that are unbound, keys you have never pressed. Editing
stays as the way you fix a line, not as the front door.

**Three things make that possible and nobody else has them:** the ship database,
CIG's own 90,121 label strings for plain English on 691 shorthand action names, and
the collector's record of which keys you actually press.

**Documents:** `DESIGN_the-easiest-keybinding-setup-2026-09-06` (the three-device
plan) · `CIC_survey-keybind-tools-and-the-gap-2026-09-06` (the survey and the turn)
· `FINDING_i-have-now-seen-the-games-own-keybinding-screen-2026-09-07` ·
`DESIGN_tap-lights-the-key-hold-opens-it-2026-09-07` ·
`front-end-build-plan-2026-08-02` (the file-format research).

**What is NOT designed:** the pad board, the two-stick board, and the check-up
itself beyond concept level. **And the largest unknown in the whole thread is still
unopened:** the game's profile file format for pads and sticks. Two of the three
device types in your own brief rest on it.

---

# 2. FLIGHT STICK PANELS — parked by two rulings, one of them yours

**STATE: designed, then bounded twice. Effectively parked, and correctly.**

The thread started with a real question — how certain can we be about where a
button sits on a stick — and the first answer was wrong in a way you caught the
same day: *the browser cannot tell us* is not *we do not know*.

**Two rulings since have closed most of it:**

- **2026-09-08, yours:** stick panels are our own photographs only, and nothing is designed until the HID remap question is measured.
- **2026-09-10, Architecture's, after CIC read all three makers' manuals to the end:** nothing in this project may key a control's identity to its HID button number. **Remapping alone would not have killed it** — a remapped stick still has one fixed table, and this desk would have been tempted to ask the pilot once and store it. **Shift state kills it:** one physical control reports several different numbers depending on the layer, so it cannot be a table at all.

**What that leaves.** The 84-template library everything leaned on is a picture
source and never an identity source. **The pilot's press is the only thing that can
say which control is which** — so the teaching walkthrough, which these documents
demoted to a fallback, is now the only mechanism there is.

**The structural idea worth keeping regardless:** a flight stick is the ship
hardpoint viewer with a different mesh. Buttons and hats are the visible,
walked-up-to hardpoints; firmware curves and shift layers are the internal
components and belong in a menu overlay. Same rule as the ships, same answer.

**Documents:** `FINDING_nothing-in-the-browser-knows-where-a-stick-button-is-2026-08-31`
(corrected today; factual half still good) · `DESIGN_dont-draw-the-stick-2026-08-31`
(superseded) · `FINDING_the-stick-panel-is-the-hardpoint-viewer-2026-08-31`
(recommendation superseded, insight stands).

---

# 3. THE FRONT PAGE AND THE SHIP PAGE

**STATE: the card grid you approved is built and published beside the old page. The
rest of the concepts are mockups on disk.**

**What shipped:** the card grid, grouped by manufacturer A–Z, ships A–Z inside,
every card the same height, every fact on the face of the card. You rejected five
designs from the previous session and two from this one before approving it, and
what killed the version before was your own sentence — *"it's not simple to get the
information."*

**What this desk measured that changed the argument.** The ship was **36% of the
ship page**, because two side rails take 42vw and never collapse and 238px of
height is spent before the grid begins — and there are three separate scroll
regions, which is what "scroll a bunch" actually is. That is a layout fact, not a
styling one.

**And the sentence nobody had said out loud:** a table serves one of the five
reasons people arrive badly and the other four not at all. *The fault is not the
table. It is that the table is the whole page.*

**Mockups on disk**, `data-layer/derived/main-page-concepts/`:
`five-main-pages.html`, `slipway.html`, `deck-sifter-yard.html` — these three are
this desk's, per `OWNERS.md` — plus `drydock.html`, `the-wall.html`,
`six-front-pages.html`, `three-looks.html`, `sky-three-ways.html`.

**Live defects this desk raised that are still standing:** the card grid is ragged
at 8 distinct heights; nine ship cards with no picture read as failed image loads
rather than honest absences; `object-fit: cover` crops the biggest ships hardest,
so the ship you most want to look at is the one you see least of.

**Documents:** `DESIGN_the-front-page-and-the-url-defect-2026-08-30` ·
`SPEC_the-front-page-becomes-the-wall-2026-08-31` ·
`PROPOSAL_make-the-ship-the-page-2026-08-30` ·
`RESPONSE-CIC-our-map-is-the-thing-that-is-wrong-2026-08-31`.

---

# 4. TEN MINING PAGE CONCEPTS — delivered, and nothing was ever queued to build one

**STATE: complete design, delivered 2026-08-28.** **`NEXT.md`** **R1 under "C3'S QUEUE" is
the order to DESIGN them and it still reads open, "BLOCKED-BY nothing", two weeks
after it was satisfied. No entry anywhere asks for any of the ten to be BUILT.**

You asked for ten deeply detailed mining page ideas with a HUD somebody enjoys
using. You got ten specs, each carrying the player's question in their words, the
screen, the interaction, the data by file and field, what it cannot say, build cost,
and why anybody comes back. Ranked at the end, with a first pick and a reason.

**The finding that reframed the whole brief:** every other tool in this hobby
answers *what is this rock worth*. **Not one can answer** ***what does this rock
become*** — because CIG only recently shipped the data that closes the loop, and 26
of 26 crafting ingredients trace back to a specific rock through CIG's own UUID
pointers, zero unreachable, no matching of any kind.

**First pick: the Demand Board.** One day, one dataset, no unresolved questions, and
it states something true that no other tool states — *Aslarite is required by 856 of
1,607 recipes.* People repeat sentences like that.

**It also caught three wrong figures in its own brief**, including a unit error that
would have summed 26 cargo resources with 11 hand-picked gems into one meaningless
number.

**AND THE TWO RECORDS THAT SHOULD HAVE MET NEVER DID.** `NEXT.md` M16, the
crafting-demand data job, closed on 2026-08-27 with its own note: **"Still homeless:
****`CRAFT_DEMAND`****, the fleet-wide mining answer. It wants a page of its own and that is
a bigger conversation than one line."**

**That page was designed the next day.** It is concept 1, the Demand Board, and it
is the first pick. The data entry says it needs a page; the design is the page;
neither record mentions the other, and the phrase "demand board" appears nowhere in
`NEXT.md`.

**Document:** `DESIGN_ten-mining-page-concepts-2026-08-28`, with
`ERRATUM_the-mining-figures-2026-08-29`.

---

# 5. THE FACT ENGINE — finished proposal, no queue entry at all

**STATE: proposal only. Nothing built that runs in the project. "Fact engine",
"fact-engine" and "daily fact" all return zero matches in** **`NEXT.md`****.**

A thing that finds one true, checkable, interesting fact about the game every day
and draws it, from data we already hold. Nine shapes of "interesting", a
standing-facts drawer for quiet days, and a five-step pipeline in which **nothing
publishes without a human**.

**Your verdict on the prototype, recorded so nobody treats the prototype as the
design:** *"I like the concept. I think if we polish the hell out of that flaming
turd, we might actually have something there."*

**The honest part.** Detectors are ordinary code; ranking nine kinds of interesting
against each other is not, and that is the only piece that has to be invented.
**The proposed answer is you** — show you thirty candidates once and let your
ordering be the scoring. That has never been run.

**Why it is a project and not a script:** it is the only part of this site that gets
more valuable the longer it runs. Everything else is a snapshot of now. This one
accumulates.

**Document:** `PROPOSAL_the-fact-engine-2026-08-31`.

---

# 6. THE TEN EYES — three of them are actually running

**STATE: three registered as real checks, on the auditor schedule. Seven unbuilt.**

Ten automated ways to look at our own pages, because this desk cannot see a rendered
page and every visual judgement it makes is inference otherwise.

**Two of this desk's rules went in with them, and one of C1's:** an eye flags and
never fixes; ten eyes feed one board; **an eye never gates a deploy** — a visual
check that blocks a build will eventually block one for a reason nobody can
reproduce.

**The two that would most directly fix the blindness are the two not built:** the
night sky (photograph every page, subtract yesterday's — it needs no rules at all
and catches the whole category nobody wrote a rule for) and the filmstrip (frames
through an animation laid out in a row, which is the only way this desk could ever
have judged whether your key press felt smooth).

**Document:** `DESIGN_ten-eyes-2026-09-08`, arithmetic verified independently in
`VERIFIED_the-ten-eyes-arithmetic-holds-2026-09-08`.

---

# 7. SIXTY ANGLES AND `design/ANGLES.md` — your method, now binding on every desk

**STATE: live and in use. More than one desk is writing to the file.**

Your method, written up and ruled binding on every desk by Architecture on
2026-09-08, and deliberately kept OUT of the locked decisions file, because a living
checklist inside a frozen document either freezes the checklist or unfreezes the
document.

**The method itself moved upstairs** to `CCDesk-logs/ANGLES.md`, because it is
yours, predates this site, and more than one project uses it. **`design/ANGLES.md`****
holds what is specific to Citizen Compass** — questions and riders, each generated
by something that has already gone wrong here.

**Added 2026-09-12:** a "Pairs" section, eleven pairs, offered by the audit desk.
It is a different unit from an angle list — every other list examines one thing from
many positions, and pairs exist because three collisions in one day were invisible
from either document alone. Two questions: *do these two still agree*, and *if one
is right, is it right about the thing that matters.* The second is the one that gets
skipped and the one that finds things.

**The rider this desk earned the hard way:** different is not automatically better.
This desk claimed a differentiator a competitor had shipped years earlier. Examine
theirs first, ours second.

**Document:** `DOCTRINE_sixty-angles-2026-09-08`.

---

# 8. THE OVERLAY AND MOUSE PASS-THROUGH — half right, half wrong, now closed

**STATE: research only. No overlay ships. The one real fix is in.**

You noticed a free game on your desktop letting mouse clicks pass through its window
and said we should learn it for later. The research is sound: `WS_EX_LAYERED` plus
`WS_EX_TRANSPARENT` for click-through, and `SetWindowLongPtr` needs a following
`SetWindowPos` or nothing takes.

**And then this desk prescribed those flags for a program it had not opened.**
`overlay_app.py` is an ask box you type a question into, not a display-only HUD.
Applied as prescribed, you could never type the question. Build refused, and Build
was right. **Both flags withdrawn 2026-09-12.**

**The half that was real is fixed.** The window took the keyboard on show and never
gave it back, so after Escape the game stayed deaf until you clicked it. Build made
`show()` record the foreground window and `hide()` restore it.

**And the question that decided whether any of it was worth doing is closed:** you
play borderless — from the game's own log and its own profile file, two sources. An
overlay will draw.

**On CIG's position:** they publish a support article naming nine overlays, treat
overlays as a compatibility matter, warn nobody off any of them, and have published
nothing anywhere that frames an overlay as a rules question. Every problem on that
page is an overlay that hooks the renderer; a window that draws its own pixels hooks
nothing. **That is compatibility, not permission, and permission remains yours.**

**Documents:** `FINDING_a-window-can-let-the-mouse-through-and-this-is-how-2026-09-07`
· `FINDING_cig-names-the-overlays-that-break-and-ours-is-not-one-of-them-2026-09-08`
· `FINDING_no-rule-says-yes-and-no-rule-says-no-about-overlays-2026-09-08`
**(banner-marked SUPERSEDED — its central claim is wrong, do not cite it)**.

---

# 9. THE UX DOCTRINE ASSESSMENT

**STATE: adopted at v6.2,** **`docs/UX_DOCTRINE.md`****.**

This desk assessed it before adoption and produced three real defects and one
confident wrong one — and the wrong one was the biggest number in it. **What caught
it was another desk re-measuring the claim**, which is the argument for the audit
desk existing.

**The ruling out of it worth remembering:** a site-level statement about unverified
data, said once and loudly, beats a badge on 254 cards. A badge on every card is
wallpaper by the third page.

---

# WHAT THIS LIST ADDS UP TO

**Measured in** **`NEXT.md`** **today rather than assumed.** The fact engine has no entry of
any kind. The keybinding check-up has none — every keybinds entry in that file is
about the existing keybinds page's stamp, links and help text, not about the tool.
The mining concepts have exactly one entry, R1, and it is the order to DESIGN them,
still reading as open with "BLOCKED-BY nothing" against work delivered on 2026-08-28.
**Nothing in the file asks for any of the ten to be built.**

**None of the three is blocked. None is waiting on data.** Each was delivered
complete, with a first pick and a cost.

**That is not a complaint about the queue, and the queue is probably right.** The
front page, the outside review's 54 confirmed findings and the automation work are
all ahead of them, and every one of those is closer to a site a stranger can trust
than a mining page is.

**But the pattern is worth naming, and it is about this desk rather than about
you.** This desk produces finished design faster than the project can build it, and
the ones that survive are the ones you personally sat with. The keybinding board
exists as a working page because you drove it in session; the mining concepts are a
document because nobody did. **The difference is not quality. The Demand Board is
one day of work and states a true sentence no other tool in this hobby states.**

**And the mechanism is visible in one line of** **`NEXT.md`****.** A queue entry whose
DONE-WHEN is *deliver a document* is satisfied the moment the document arrives, and
then nothing carries the work forward, because the next step was never an entry.
**A design job with no build job behind it terminates in a folder.** That is not a
queue failure and it is not yours — it is what happens when the unit of work is a
deliverable rather than an outcome.

**What I would do about it, and it is one thing rather than three.** When the front
page and the review findings are done, the Demand Board is the cheapest complete
proof that this site is not another ship spreadsheet. One day, one dataset, no
unresolved questions, and M16 already asked for exactly it. **Not because it is the
best idea in that document — concept 2 is — but because it is the one that can be
finished before anybody loses interest in it.**

---

## CHECKED AND NOT CHECKED

**CHECKED.** `design/` and `data-layer/derived/main-page-concepts/` listed on disk
today with file sizes. Every document named above read in this project today or
earlier in this session. The design tray and `inbox/` listed and both empty.
**`NEXT.md`** **staged and searched directly** — 262,462 bytes — for mining, demand
board, fact engine, daily fact, keybind and Aslarite, and the R1 and M16 entries
read in full.

**A CORRECTION THIS DOCUMENT OWES ITSELF.** Its first draft flagged the queue
question as NOT CHECKED and said the three designs were "never queued". **Checking
it made the claim both sharper and partly wrong:** the mining design job WAS queued,
as R1, and delivered. What does not exist is any entry to build one of the ten.
Corrected in §4 and in the closing section rather than left standing — which is the
exact failure that cost another desk a wasted read four days ago.

**NOT CHECKED.** Whether the mockup HTML files still open correctly — several are
one to four megabytes with pictures inlined, and none has been loaded in a browser
since it was made. Whether R1's open state is deliberate or stale: **it is C1's file,
and the question is in Architecture's tray rather than answered here.**

*Design (C3), 2026-09-12.*