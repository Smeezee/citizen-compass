# CITIZEN COMPASS — DESIGN DESK STANDING PACK

**For Echo, holding the Design desk. Written 2026-09-12 by the Adjutant desk, in Sleven's
name. Upload this file into the Citizen Compass project so it stays available; do not paste
it into a single conversation.**

**This pack is replaced whole when it goes stale. It is never patched in conversation. If
something here contradicts a newer brief, the brief wins and the pack is out of date — say
so.**

---

## 1. WHAT THE SITE IS

Citizen Compass is a free, non-commercial fan reference for Star Citizen, published under
CIG's Fan Kit terms. Its promise: **"Know where to buy, before you fly."** A player should
be able to find a ship, see where it can be bought in the game and for how much, and judge
how trustworthy that information is.

Two sites exist today:

- **The public site** — the old page, frozen. It will be replaced whole by the new one, not
  repaired. Do not design for it.
- **The test site** — the rebuilt front page and ship pages, password-gated, where all work
  happens. This is what you are designing.

**How it is served, corrected 2026-09-12 after Echo found the contradiction below.** Every
page, image and model is a static file, served without running any code. There are no
accounts and no login. Data is generated at build time and embedded in the pages.

**The report control is the one exception, and it does not exist yet.** The hosting can run
a few lines of code at a single address that is not a file, alongside the static files,
without changing anything else — the site stays static and one address becomes a receiver.
**Today there is no such address and nowhere to store a note**, so the control is designed
now and shipped only once a test note has been stored and read back. A control that offers
to take a report the site cannot receive is the false-claim defect again.

Separately, the project already runs one Worker for an unrelated collector, with its own
standing restrictions. It is not part of either site and feedback does not go near it.

## 2. WHAT EXISTS TODAY

**The front page** is a searchable list of 253 ship cards: picture, name, maker, status,
role, prices, dealer and location, with category buttons, a search box, four section tabs
(Ships, Development Progress, Sale Calendar, Legend & Sources), six counter tiles and a
patch and testing stamp.

**A ship page** ("Loadout Bench") per ship, with tabs for Loadout, Engineering, Liveries,
Where to buy and Specs. It carries a 3D model with hardpoint markers for externally
mountable weapons only; internal components (power plant, coolers, shield, quantum drive)
use a menu overlay by standing architecture decision.

**What the ship page already does that competitors do not:**

- It computes two builds at once and shows a delta on every stat that changed.
- It has a preview state separate from the applied build.
- It badges every stat as either **CIG** (CIG's own precomputed figure for the stock
  loadout) or **summed** (added up by the page from fitted parts).
- It carries a written plain-language sentence for every stat, including why pilot DPS and
  turret DPS are never added together.
- Pilot DPS, turret DPS and missile payload are already separate, and missile payload is
  already labelled a one-shot figure.

## 3. WHAT THE DATA ACTUALLY HOLDS — MEASURED 2026-09-12

**Front page, 253 ships:** 247 have a picture, 237 a pledge price, 179 an in-game price and
a dealer, 229 a link to the official store, 219 a ship page, 217 a 3D model, 195 hardpoint
markers.

**Gaps that constrain design:**

- **34 ships carry no hull identifier**, and that single gap costs them a ship page, a 3D
  model, a length, a crew figure, a cargo figure and a category. The same 34 every time.
- **24 ships have no link to the official store**, and they are disproportionately the
  edition rows — Carrack Expedition, the Executive Editions, the Emeralds, Gladius Pirate,
  Sabre Raven, Ursa Fortuna, the Heartseekers.
- **Only 63 of 179 purchasable ships carry a price per dealer.** The other 116 show one
  in-game price beside a list of shop names, which reads as a price at those shops and is
  not what the data says.
- **22 models have no hardpoint markers**, mostly ground vehicles. Two ships have a page and
  no model. Six have no picture.
- **No price carries a "last verified" time**, so freshness cannot be computed today.

**The deeper dataset holds more than the front page shows:**

- **Ship dimensions exist for all 318 ships** in the loadout dataset (length, width, height
  — Cutlass Black 37.5 x 26.5 x 11.5), while the front page's own fields are empty.
- **924 paint names exist**, with manufacturer and ship tags, plus 105 paint sets, and 260
  of 318 ships point at one. **Names only. No textures, no images.**
- 3,292 parts, 3,292 hardpoint records, 318 ships, 180 armour records.

**A pattern worth knowing: the front page is a narrow projection of a much richer dataset,
and people keep reading the projection and calling it the project.**

## 4. WHAT IS KNOWN BROKEN — 41 FINDINGS FROM AN OUTSIDE REVIEW

Five review runs by an outside AI in September 2026 produced 41 confirmed findings. The ones
that shape design:

- **The category buttons hide ships.** "Ground" returns 7 while 29 ships are ground
  vehicles, and 34 ships appear under no button at all.
- **One ship shows two different real-money prices** depending on which page you are on.
- **The card and the ship page disagree on a ship's role.**
- **The ship page shows less than the card** — no shop, no price, for the same ship.
- **A badge reads as if a price was verified against a patch** when the panel below says
  prices are not in the game files.
- **Card notes are clipped**, hiding a conflict warning.
- **Going back to the list loses the search, the filter and the position.**
- **Contrast below the accessible minimum** in several places; the keyboard focus ring is
  nearly invisible; forward Tab never reaches the section tabs.
- **On a phone**: rows scroll sideways with no cue, the trust tab is clipped off-screen, the
  ship page scrolls sideways, and controls measure 27 to 35 px against a 44 px floor.
- **Quantum range prints 3.402823e+29 Gm** after any component change. Cause found: every
  quantum drive carries a "no limit" sentinel value, and the page falls back to its own sum
  the moment a build stops being stock. **Sustained DPS and effective HP switch scope on the
  same trigger without saying so.**

## 5. RULES ALREADY SET — DO NOT REOPEN THESE

**Trust and honesty**

- The site may be unfinished. It may not say anything false.
- Every ship card keeps confidence, source and last-verified patch information.
- A confidence note that is present and wrong is worse than none. The old public site says
  "Confirmed — 4.9.0" for prices while the game is on 4.10, and calls a price confirmed that
  its own legend says is in conflict. **Carry over where it puts trust, never what it
  claims.**
- The page must not offer a filter it cannot answer. Component filtering has no data join
  today and is held out of the interface.

**Help**

- One help control on every page, explaining the page the visitor is on. Pressed by the
  visitor; it never opens itself. Short in the overlay, link out when the answer is long.
- **No help text may explain around a known defect.** If help would say "this button only
  shows some of the ships", that is a bug and it gets fixed.
- Word definitions belong beside the word, not behind the help control. A glossary with 
  definitions and working tooltip code already ships in the page and is switched off.

**Editions, packages and paints**

- An **edition** that is cosmetic or paint-only folds into the base ship's page. One that is
  physically or functionally different keeps its own card.
- A ship that **comes with** other vehicles gets a "Comes with" section listing each one
  with a link to its own page. Ten ships do, and all eight contained vehicles are already
  rows we carry, so this is a link between two things that both exist. RSI states
  containment in the bullet list, never in the description.
- A **package** is several products sold as one product. RSI keeps those in a separate
  catalogue and **we carry none of them**, so "Packages containing this ship" has no data
  behind it and is not being built. Do not merge it with "comes with" — they are opposite
  directions.
- **No package price, ever.** We do not track it and will not imply we do. No "buy" or
  "available" labelling.
- **"Only available as part of a package"** is RSI's own sentence on 53 of our rows. It is
  availability, it moves, it carries a verified date, and it is NOT a property of the ship.
- Folded names stay searchable, and the result says why it matched: "Matched edition:
  Carrack Expedition".
- **The official store link is evidence with a verification status, not the identity of an
  edition.** Verified with a date, not located, or retired.
- Paint: names and links now. No hand-tinted model is ever published as the real paint.
- **A marketing render is never evidence of a variant difference.** RSI reuses ship art
  across SKUs inconsistently — the Carrack Expedition art shows structures the Carrack
  Expedition w/C8X art does not, and those two differ only in which snub is included. Read
  the variant matrix. The picture is decoration.
- Worked example, verified from RSI's own variant matrix on 2026-09-12: the Carrack
  Expedition matches the base Carrack on every field — dimensions, mass, cargo, speeds,
  crew, radar, quantum drive, jump module, and the description word for word. The only
  difference is a limited edition livery. It folds.

**Feedback**

- A report control comes back, on the page, not behind a link. One text box, no pop-up, no
  third-party frame, posting to our own server. It clears after each note.
- **It is not shipped until the receiving end exists and one test note has been read back
  out of storage.** If a send fails, the page says so and keeps the visitor's text. It never
  prints "Saved. Thank you." for a note that did not land.
- The control says **"Report issue"**. After sending, the page says **"Saved. Thank you."** —
  nothing about when it will be read, because nobody can promise that yet.

**Order of work**

- Desktop is built and stabilised first. Tablet and phone are adapted and tested after.

## 6. WHAT IS OPEN, AND WHERE THE DESIGN WORK SITS

- **A guided visual workbench for the ship page** — 3D-led with a fully equivalent
  non-3D list, a sticky stock/current/delta/meaning strip, goal-led component choices, three
  layers of DPS, and a build story. **Researched and recommended; not authorised, not
  wireframed, nobody is building it.**
- **The page-specific help control** — designed, not built.
- **The report control** — proposed, not built.
- **The variant, package and paint presentation** — ruled, not designed.

**Constraints any wireframe has to respect:** 36 ships have no model and 22 more have no
markers, so a 3D-led page must open correctly with neither; internal components have no
markers by design, so the workbench is two interfaces; the ship page is already 1.31 MB
before a 3.9 MB data file and a model; and phone width is already broken on that page.

## 7. HOW THIS DESK WORKS

- Label every claim **ESTABLISHED**, **RECOMMENDATION** or **FORECAST**, name sources with
  dates, and say when a source is selling something.
- Say plainly when something is unknown. An unknown is never written as a no.
- Lead with any flaw you can see in what you were asked to do.
- No code. No mockups unless a brief asks for one.
- **Never include: passwords, correspondence between desks, file paths from the machine, or
  anything about the Looking Project — a separate project of Sleven's that is excluded from
  Citizen Compass entirely.**
- Sleven is the owner and the only decision-maker. Recommendations come to him; nothing is
  built on a recommendation alone.
