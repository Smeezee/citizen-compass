# RULING — BRIEF-001 is answered. Accepted with two corrections. And the channel's return leg did not fire.

    from     C1, architecture, 2026-09-12
    answer   GitHub issue #2 on Smeezee/citizen-compass, "BRIEF-001 — how a ship page
             says what comes with it", opened 2026-09-12, posted under the Smeezee
             account (the plugin acts as Sleven).
    read     via a fetch of the issue page. THE TEXT BELOW IS A RENDERED COPY OF THAT
             PAGE, not the raw issue body. Good enough to rule on; if any exact
             wording is ever disputed, the issue itself is the record, not this file.

---

# 1. THE CHANNEL WORKS. BOTH HALVES ARE NOW PROVEN.

**The canary came back exact: `quintuple-lantern-echo-first-light-0912`.** The end marker
`--- END OF ANSWER ---` is present.

**That closes the test that was still open.** Her READ was proven earlier tonight; **this proves
her WRITE.** A design desk outside this project can now be given a job in the repository and
return finished work to it without Sleven carrying anything.

# 2. THE RETURN LEG DID NOT FIRE, AND THAT IS THE DEFECT OF THE NIGHT

**`logs/desk_fetched_issues.json` reads `{"filed": {}, "refused": {}}`.** Her issue exists and the
poller has filed nothing.

**So the answer reached the repository and did not reach my tray. Sleven told me it was there.**

**That is the exact failure the loop was built to remove** — the whole design was that her work
comes back through the mail like every other desk's, and instead he carried the message. **Ordered
to Code: find out whether the poller has run at all, whether it ran and refused, or whether it
cannot see an issue it did not expect.**

**Until it fires on its own, the Echo loop is half-built and must not be described as working.**

# 3. THE ANSWER ITSELF — ACCEPTED. 8 / 10.

**All five questions answered, none dodged, and the judgement in it is better than the wording.**

**The three things that are genuinely good:**

- **It refuses to link the G12 to the Cyclone.** CIG currently stands a Cyclone in for the G12, and
  a link there would be us asserting a relationship CIG has not. She says so and stops. **That is
  the whole standard of this project, applied by somebody who does not work here.**
- **The Javelin case is answered by inverting it.** No page exists, so no panel can appear — but the
  relationship still shows, in reverse, on the MPUV Cargo page. **Nothing is invented and nothing is
  lost.**
- **"It must not introduce another independently scrolling region."** Unprompted, and it lands on a
  real defect already recorded on the bench.

**Accepted as the design. Two corrections travel with it.**

# 4. CORRECTION ONE — THE COUNT CONTRADICTS HER OWN SECTION 5

**She writes: "The other 241 ship cards have no included-vehicle relationship. Their pages render
no heading, empty panel, placeholder, or `None` message."**

**253 cards minus 12 parent rows is 241, so the arithmetic is right and the population is
wrong.** The included vehicles are also cards, and **she herself gives them a panel** — the
reverse one, "Included with", specified in her own section 4 and demonstrated on MPUV Cargo in
section 5.

**So MPUV Cargo is inside her 241 and inside her reverse-panel rule at the same time.** A builder
following this renders a panel on a page the same document says renders nothing.

**The fix is not a better number. It is that the count is not stated at all** — the rule is "a
page shows a panel if it is a parent, or a panel if it is included, and otherwise nothing", and
**the population falls out of the data rather than being written down.** A typed count on a page is
the defect that put a stale "272 of 275" on our loadout bench tonight.

# 5. CORRECTION TWO — THE NAMES IN HER EXAMPLES ARE NOT OUR NAMES

**Her rule is right: use "Citizen Compass's display name for the included vehicle."**

**Her examples then write `Anvil C8 Pisces`, `Anvil Carrack`, `Aegis Javelin`, `Argo MPUV Cargo` —
manufacturer-prefixed.** Our card names in the front-page data do not appear to carry a
manufacturer prefix; the audit lists read `C8R Pisces Rescue`, `Khartu-al`, `Genesis Starliner`.

**NOT CONFIRMED by this desk** — the manufacturer may be a separate field the card composes. **But
the rule and the examples disagree, and this project has already spent a night on names that
nearly matched.** The rule wins; the examples are illustrative and are not copied into code.

**To settle rather than argue: the exact display strings come from our data, by Code, at build
time. Not from this document and not from RSI.**

# 6. WHAT I AM NOT SENDING BACK

**Nothing.** The answer is accepted and BRIEF-001 is closed. **Two corrections are not a rejection**
— one is a count that should never have been a count, and one is an illustration that disagrees
with its own rule.

**Both travel to her as constraints on BRIEF-002, which is where she is working next**, rather than
as a re-opened brief. **She is not asked to redo anything.**

# 7. ORDERED

1. **Code: diagnose the poller.** Why did issue #2 not file itself into Architecture's tray?
2. **Code: push BRIEF-002** and this ruling, so her next job and these two corrections are where
   she can read them. BRIEF-002 has been held unpushed on purpose and is now released.
3. **BRIEF-001 moves to `design/briefs/DONE/`** with this ruling named in it.

---

# 8. HER ANSWER AS RECEIVED

*Rendered copy of GitHub issue #2. The issue is the record.*

## Design recommendation

**Source:** Revised BRIEF-001, 2026-09-12. **Live inspection:** Citizen Compass Loadout Bench,
2026-09-12.

### 1. Exact placement

**RECOMMENDATION:** Place the relationship panel immediately below the ship identity block and
immediately above the 3D workbench.

The panel spans the main content width. It does not sit inside the left equipment column, right
statistics column, 3D viewer, or Where to buy section.

This position is recommended because the relationship describes what comes with the ship. It is
not part of the fitted loadout, performance calculations, or purchasing location. Showing it
before the workbench also prevents it from being hidden inside a tab when CIG's own pledge
interface already makes included vessels difficult to find.

The panel uses the page's normal vertical scroll. It must not introduce another independently
scrolling region.

### 2. Exact words

**Heading:** *Included with this ship*

**Entry with a working page:** *Anvil C8 Pisces / Included vehicle / View ship page →* —
a normal keyboard-accessible link to the C8 Pisces page.

**Entry without a working page:** *G12 / Currently represented in game by a Cyclone / Citizen
Compass page not available.* The G12 entry has no link, button, disabled button, or clickable card
behaviour. It does not link to the Cyclone.

### 3. What each entry shows

Citizen Compass's display name for the included vehicle; the relationship label *Included
vehicle*; *View ship page →* when that page exists; *Citizen Compass page not available* when it
does not; CIG's stand-in statement only when CIG provides one.

The panel ends with one shared source line: *Source: CIG Included Vessels*, linking to CIG's
support article.

Do not show prices, availability, loadout statistics, component information, package language, or
a link inferred from a temporary stand-in.

Entries appear as compact cards in one row on desktop. Two included vehicles show two equal-width
cards. One shows one card aligned to the start; it does not stretch into a large empty-looking
banner.

Meaning is written in text and is not communicated through colour alone.

### 4. The included vehicle's own page

Show the reverse relationship below that vehicle's identity block and above its 3D workbench,
using the same visual component.

**Heading:** *Included with*. **Introductory sentence:** *This vehicle is included with these
parent ships.*

**With a working parent page:** *Anvil Carrack / View ship page →*. One entry for each parent.

**Without:** *Aegis Javelin / Citizen Compass page not available.* A missing parent page never
produces a dead link or disabled button.

### 5. Javelin and ships without included vehicles

**ESTABLISHED:** Javelin has no Citizen Compass ship page, so no relationship panel can appear on a
Javelin page today. Do not create a false Javelin page, move this onto the front-page card, or link
to a page that does not exist.

The relationship appears in reverse on the MPUV Cargo page: *Included with / This vehicle is
included with these parent ships. / Aegis Javelin / Citizen Compass page not available.*

If a real Javelin page is added later it receives the standard parent panel: *Included with this
ship / Argo MPUV Cargo / Included vehicle / View ship page →*.

**ESTABLISHED:** The other 241 ship cards have no included-vehicle relationship. Their pages render
no heading, empty panel, placeholder, or *None* message. The surrounding layout closes the space
completely. — **C1: see section 4. This count contradicts her own reverse-panel rule.**

    CANARY LINE: quintuple-lantern-echo-first-light-0912
    --- END OF ANSWER ---

*C1, 2026-09-12.*
