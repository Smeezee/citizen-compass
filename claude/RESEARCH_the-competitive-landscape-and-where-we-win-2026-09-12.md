# RESEARCH — the competitive landscape, what we do better, and what this page could do better

**SOURCE NOT STATED. Relayed by Sleven, 2026-09-12, from a competitive search he is running
himself. NOT the Design desk and NOT Echo — C1 assumed Echo on first filing and was wrong;
that filing is withdrawn at `claude/ECHO_the-competitive-landscape-and-where-we-win-2026-09-12.md`.
Verified by C1 before filing — the verification
pass is section 0 and is C1's. Everything from section 1 down is the document as received,
unaltered.**

---

## 0. C1'S VERIFICATION PASS — read this before acting on anything below

### ONE FIGURE IS WRONG, AND IT IS THE PROJECT'S OWN RECURRING DEFECT

**The report says "3D GLB models (~295)". There are not 295 models.**

Measured in `claude/AUDIT_images-models-dimensions-phase-one-2026-09-12.md`, section 4:

    256    GLB files that exist in testing/_deploy/models/
    214    distinct files actually mapped by LOADOUT_MODEL
    295    ClassNames that map onto those 214 files
    318    ClassNames in LOADOUT_SHIPS total
     42    files referenced by no ClassName at all

**295 is a ClassName count, not a model count.** It takes a number off one surface and
labels it with another surface's noun. **This is the same defect class the desk spent
2026-09-12 on** — 253 cards against 254 data rows against 318 ClassNames against 253 RSI role
rows — and it has now appeared in an outside competitive review.

**Not held against the author.** Whoever ran this had no access to the audit; it is on disk and
is not published. **That is a supply failure on this desk's side, not an accuracy failure on
theirs**, and the fix is that the audit's figures travel with the next brief rather than that
anyone is told to be more careful.

### "253 ships" IS RIGHT FOR THE SURFACE SHE MEANS

The catalog renders 253 cards. The report is describing the catalog. **Correct as written**, and it is
worth noting only because the number is not transferable: the same "253" is a different
population in the RSI roles file (`claude/Q63-8A_career-against-the-official-role-2026-09-12.md`
— only 225 of the two 253s join).

### NOT VERIFIED BY THIS DESK

- **"~452 craft recipes."** Not checked. Plausible; no figure re-derived.
- **Every claim about a competitor** — Erkul v5's shopping cart, UEX freshness stamps,
  FleetYards' API, CSG's power modelling, and the "stale or dead" verdicts on Hardpoint,
  SPViewer and StarJump. **None of it has been checked by this desk and none of it should be
  published.** It is positioning input. It is not a fact we assert.
- **"Idris-P $1900 vs older $1500."** It cites our own displayed conflict. Not re-derived here.

### THE FINDING THAT MATTERS MORE THAN THE CORRECTION

**The report's number-one recommendation is a decision this project already made and never built.**

It says: *per-ship "checked against patch X on date Y" badge (green / stale / unverified)*,
and lists it first under "Nail the core promise: verification."

**That is `last_verified_patch`.** It is a standing architecture decision in the project's own
instructions — *"Every data row carries last_verified_patch; front end flags unverified data"* —
and the front end does not flag it.

**So an outside reviewer, with no access to our architecture decisions, independently named our
unbuilt decision as our largest competitive gap.** That is the strongest possible evidence the
decision was right and the strongest possible evidence it has been left too long. **It goes to
the top of the design queue on that basis alone.**

### WHAT IS SLEVEN'S AND NOT MINE

Two items in the list are not architecture and not design. They are product positioning and
they are his:

1. **"Open in Erkul / CSG handoff"** — deliberately routing our own users to a competitor for
   deep min-max, in exchange for owning acquisition and visual truth. It is a coherent strategy
   and it is a strategy, not a UI decision.
2. **Dropping the preview gate and the "testing" stamp** — that is a decision to start taking
   real traffic, with everything that follows from it.

**Everything else in the document is design or architecture and does not need him.**

---

## 1. WHAT CITIZEN COMPASS IS — the document as received

*"Know where to buy, before you fly."* Unofficial SC fan tool that joins two jobs most sites
split apart:

- **Catalog (`/next`)** — Should I pledge this, or can I earn it in-game, and where?
- **Loadout Bench (`/loadout`)** — What's actually on the hull, in CIG's own hardpoint layout,
  with file-faithful stats?

There's also a lighter Find shop browser and a private preview gate.

### Catalog does

- 253 ships, search (ship / maker / job / shop / place), career chips, "buyable in game" filter
- Status pills: in-game vs pledge-only
- aUEC + pledge $ (multi-currency FX), dealers to places (New Deal / Astro / Orison / Teach's /
  Buy & Fly)
- Dev progress list + sale calendar (Invictus, IAE, etc.)
- Legend, sources, and known conflicts shown not "fixed" (e.g. Idris-P $1900 vs older $1500)
- Empty "no image" instead of wrong art
- Click-through into loadout when a hull ID exists

### Loadout Bench does

- 3D GLB models (~295) with CIG-position hardpoint dots (tagged cig / estimated)
  — **C1: see section 0. The model count is 256 files / 214 in use; 295 is ClassNames.**
- Stock vs edited loadout; fixed vs editable ports from game files
- Live stats ("Everything that moves") — CIG numbers when stock, "summed" when you change parts
- A/B compare ("Try another alongside"), undo, share link, day/night/blackout
- Tabs: Loadout, Engineering (fuse counts only), Liveries (names only — not painted on the
  model), Where to buy, Specs
- Craft recipes on parts (~452); armor / gun-vs-armor matchup with honest ranges
- Explicit refusals: no fake component shop prices, no guessed livery colors, no invented fuse
  failure

**Personality: forensic, anti-handwave. That's the brand.**

## 2. SAME-CATEGORY TOOLS

**Not verified by this desk. Positioning input only.**

**Erkul v5** — overlaps on loadout + shopping + ship finder. Does well: community default for
fitting; DPS/power/cooling; LIVE/PTU; aUEC cart and buy route; share builds. Gap: not a "status
before you fly" catalog; Discord login; no CC-style provenance or hardpoint 3D bench.

**FleetYards** — overlaps on catalog + dealer aUEC + hangars. Does well: strong ship DB and API;
personal/org fleets; dealer and rental locations. Gap: not a DPS/loadout sim; SPA-heavy;
hangar-first rather than buy-decision narrative.

**UEX** — overlaps on prices and vehicle sell lists. Does well: live 4.10 prices, pledge matrix,
trade/marketplace, freshness stamps. Gap: marketplace UX rather than "decide this hull"; no
loadout or 3D; crowdsourced lag.

**CStone Finder** — overlaps on where to buy X. Does well: best "find this item in shops". Gap:
not a ship status matrix or a loadout product.

**starcitizen.tools** — overlaps on purchasing tables. Does well: dense dealer matrices, lore and
locations. Gap: static wiki tables; no interactive bench.

**RSI Store / Matrix** — official pledge $ and holoviewer. Does well: canonical $ and official
models. Gap: no aUEC dealers; no community loadout truth.

**Citizen Starter Guide builder** — overlaps on loadout + shopping. Does well: explicit 4.10
LIVE/PTU; deep power and sustained modelling; no account needed. Gap: newer, less brand default;
weak on the pledge-vs-aUEC status story.

**SCUplift** — overlaps on filterable catalog + $ / aUEC + loadout path. Does well: one-stop
verse DB pitch. Gap: smaller mindshare; dealer depth less clear.

**myfleet / Holoviewer** — overlaps on 3D. Does well: fleet scale, VR, share scenes. Gap: not
buy, status or loadout stats.

**Hardpoint / SPViewer / StarJump** — historical peers. Stale, empty or dead; not current rivals.

**Closest full-stack rival: Erkul**, especially now v5 does shopping.
**Closest catalog/dealer rivals: FleetYards + UEX + wiki.**
**Least contested wedge: file-faithful hardpoint 3D + acquisition honesty + buy-status in one
product.**

## 3. WHAT WE ALREADY DO BETTER

- One decision path: status to price to dealer to opening the actual ship
- Epistemic honesty — conflicts, absences, "NO PRICE JOIN" — rare and sticky for a
  design-literate audience
- Hardpoints in CIG positions on a real model. Erkul and CSG win on math; they do not own this
  visual trust
- Refusing to fake joins (parts to shops, liveries to textures) — builds long-term credibility

## 4. WHERE WE FALL BEHIND

- Erkul and CSG go deeper on optimisation math — power triage, sustained DPS, component carts
- UEX and FleetYards feel more live and patch-fresh on prices
- FleetYards and myfleet own "my hangar / my fleet" identity
- **The catalog still admits aUEC verification is incomplete, which undercuts the core promise**
- Preview gate and "testing" stamp — fine for now, friction for real users
- Loadout "Where to buy" sends you out instead of closing the loop
- No multi-ship compare on the catalog; no mobile-first density pass
- Horizontal scrollbar and density on the bench — seen on the Vulture

## 5. WHAT THIS PAGE COULD DO BETTER

Prioritised for a design and product lens: keep the honesty brand, take the useful bits from
rivals, do not become a worse Erkul.

### 5.1 Nail the core promise: verification

- Per-ship "checked against patch X on date Y" badge — green / stale / unverified
- Dealer price freshness like UEX, even if community-sourced
- Surface multi-shop deltas visually — cheapest shop highlighted, not only in text

### 5.2 Make "where to buy" a closed loop

- On the ship page: a map-ish or step list — system to station to dealer to terminal
- Deep-link into `/find` with the hull pre-filled
- Optional: "cheapest aUEC path today", without inventing component prices

### 5.3 Catalog UX upgrades — the biggest design wins

- Compare 2 or 3 ships side by side: price, cargo, crew, buyable, dealers
- Stronger empty and loading states; fix career chip oddities (Destroyer, empty careers)
- Manufacturer pages and role landing pages, for SEO and for browsing
- Mobile: cards are dense — test a single-column decision card (status to price to shop to CTA)

### 5.4 Loadout Bench — differentiate, do not clone Erkul

- Keep CIG-vs-summed and hardpoint truth as the hero
- Add a clear "Open in Erkul / CSG" handoff for deep DPS — own acquisition and visual truth,
  point out for min-max
- Paint swatch chips next to livery names, still without faking 3D paint
- Fix scrollbar and column overflow; tighten the stats panel hierarchy, pilot care-abouts first
- "Where to buy" tab: hull dealers plus "components: use Find/UEX", as a designed panel rather
  than an essay

### 5.5 Trust and positioning

- Homepage one-liner under the title: *"Pledge vs aUEC, dealers, and the real hardpoints — with
  sources."*
- A public data-ethics strip: what we will and will not invent. This is the differentiator
  against Erkul's confidence
- Drop or soften the preview friction when ready for traffic
- Patch ribbon: catalog compile date against loadout game build — make the mismatch obvious if
  they drift

### 5.6 Later

- Personal shortlist (localStorage) of hulls being decided between
- HangarXPLOR / FleetYards import only if it serves "should I buy this" — do not become a fleet
  CRM
- PTU vs LIVE toggle if we ever dual-build data

## 6. ITS BOTTOM LINE

*Citizen Compass isn't trying to be the best DPS calculator or the biggest marketplace. Its lane
is purchase truth + file-faithful ship bench. Erkul is coming for the shopping half; UEX and
FleetYards already own live prices and hangars. You win by making verification undeniable,
closing the buy loop, sharpening catalog compare and decision UX, and treating the 3D hardpoint
bench as the visual proof competitors don't have — while handing deep min-max to Erkul on
purpose.*

It offers a ranked redesign brief (P0/P1/P2 with UI notes) or mocks of specific catalog and
loadout improvements as the next step.

---

## 7. C1'S DISPOSITION

**The ranked brief is ordered to the Design desk (Echo)**, and it goes out as BRIEF-002 with the audit figures attached so
the model-count error cannot repeat. **The mocks are not ordered yet** — a ranked brief that
Sleven has not seen is the cheaper thing to be wrong about.

**Section 5.1 is promoted above everything else in the list**, on the reasoning in section 0.

**Two items wait on Sleven** and are in his tray: the Erkul handoff, and dropping the preview
gate.

*C1, 2026-09-12.*
