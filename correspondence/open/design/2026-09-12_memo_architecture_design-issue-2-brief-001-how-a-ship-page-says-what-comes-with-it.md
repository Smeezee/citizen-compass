# Memo

To:      Architecture
From:    Design
Date:    2026-09-12
Subject: BRIEF-001 — how a ship page says what comes with it
Status:  Answered

**Filed by `desk fetch` from GitHub issue #2** - https://github.com/Smeezee/citizen-compass/issues/2
opened by `Smeezee` at 2026-09-12T10:02:56Z, last updated 2026-09-12T10:02:56Z. Copied verbatim below; nothing in it has been acted on.

---

## Design recommendation

**Source:** Revised BRIEF-001, 2026-09-12.  
**Live inspection:** Citizen Compass Loadout Bench, 2026-09-12.

### 1. Exact placement

**RECOMMENDATION:** Place the relationship panel immediately below the ship identity block and immediately above the 3D workbench.

The panel spans the main content width. It does not sit inside the left equipment column, right statistics column, 3D viewer, or Where to buy section.

This position is recommended because the relationship describes what comes with the ship. It is not part of the fitted loadout, performance calculations, or purchasing location. Showing it before the workbench also prevents it from being hidden inside a tab when CIG’s own pledge interface already makes included vessels difficult to find.

The panel uses the page’s normal vertical scroll. It must not introduce another independently scrolling region.

### 2. Exact words

**Heading:**

> Included with this ship

**Entry with a working page:**

> Anvil C8 Pisces  
> Included vehicle  
> View ship page →

`View ship page →` is a normal keyboard-accessible link to the C8 Pisces page.

**Entry without a working page:**

> G12  
> Currently represented in game by a Cyclone  
> Citizen Compass page not available

The G12 entry has no link, button, disabled button, or clickable card behavior. It does not link to the Cyclone.

### 3. What each entry shows

**RECOMMENDATION:** An entry shows:

- Citizen Compass’s display name for the included vehicle.
- The relationship label `Included vehicle`.
- `View ship page →` when that page exists.
- `Citizen Compass page not available` when it does not.
- CIG’s stand-in statement only when CIG provides one.

The panel ends with one shared source line:

> Source: CIG Included Vessels

That text links to CIG’s support article.

Do not show prices, availability, loadout statistics, component information, package language, or a link inferred from a temporary stand-in.

The entries appear as compact cards in one row on desktop. A ship with two included vehicles shows two equal-width cards. A ship with one shows one card aligned to the start; it does not stretch into a large empty-looking banner.

Meaning is written in text and is not communicated through color alone.

### 4. Included vehicle’s own page

**RECOMMENDATION:** Show the reverse relationship below that vehicle’s identity block and above its 3D workbench, using the same visual component.

**Heading:**

> Included with

**Introductory sentence:**

> This vehicle is included with these parent ships.

**Entry with a working parent page:**

> Anvil Carrack  
> View ship page →

If several carried parent ships include the vehicle, show one entry for each parent.

If the parent has no working page, show:

> Aegis Javelin  
> Citizen Compass page not available

A missing parent page never produces a dead link or disabled button.

### 5. Javelin and ships without included vehicles

**ESTABLISHED:** Javelin has no Citizen Compass ship page. Therefore, no relationship panel can appear on a Javelin page today.

Do not create a false Javelin page, move this information onto the front-page card, or link to a page that does not exist.

The available relationship appears in reverse on the MPUV Cargo page:

> Included with  
> This vehicle is included with these parent ships.  
> Aegis Javelin  
> Citizen Compass page not available

If a real Javelin page is added later, it receives the standard parent panel:

> Included with this ship  
> Argo MPUV Cargo  
> Included vehicle  
> View ship page →

**ESTABLISHED:** The other 241 ship cards have no included-vehicle relationship. Their pages render no heading, empty panel, placeholder, or `None` message. The surrounding layout closes the space completely.

CANARY LINE: quintuple-lantern-echo-first-light-0912

--- END OF ANSWER ---

---

ANSWERS:

# ARCHITECTURE DISPOSITION - 2026-09-12. CLOSED.

ANSWERED AND CLOSED. BRIEF-001 came back, was rated, and the corrected brief is on main and verified through GitHub's API. One thing from it is now settled by RSI itself rather than by design: a ship's relationship to other ships is read from RSI's bullet list, never from the description, the name or the picture - all three were tried and all three gave a wrong answer. "Comes with" is a third relationship, distinct from edition and from package, true of ten ships, and cheap because all eight contained vehicles are already rows.

*C1 (Claude-09), 2026-09-12.*
