# Testing area — feature inventory

Everything added to `testing/_layer.html` on top of the live page, so anything can be found and pulled out later without hunting through the file. Current as of 2026-08-02.

**Nothing here is on the live site.** The layer is injected into a copy of `releases/latest.html` by `testing/build.py`. The live page is read, never written.

**How to remove any one item:** each entry names the CSS/JS identifiers it owns. Deleting the block that defines them removes the feature cleanly — they do not reach into each other except where the "depends on" line says so.

---

## 1. Password gate

**What it does.** Blocks the page behind a password (`apples`) until entered. Remembers the visitor so friends do not retype it.

**Identifiers:** `#cc-gate`, `html.cc-locked`, `localStorage.ccGate`

**Honest limitation, already on record:** the check runs in the browser and can be bypassed with developer tools. It stops casual discovery of the URL, nothing more. Server-side protection needs a Netlify paid plan.

**Pull it if:** the preview goes public, or real access control is needed.

---

## 2. Display engine

**What it does.** Whole-page control over text size, typeface, weight, spacing, line height, background, accent colours, contrast, borders, row height, corner rounding, motion and glow. Seven one-click profiles including low-vision and dyslexia-friendly. Exports the chosen settings as CSS.

**Identifiers:** `#cc-tab`, `#cc-panel`, `body.cc-on`, `--cc-*` custom properties, `localStorage.ccDisplay`

**Standing instruction:** ships in every build from now on.

**Default text size is 130%** on desktop and tablet, 100% below 700px wide — a phone loses a whole screen to the header at 130%. A saved preference always wins over both.

**Pull it if:** never, per standing instruction. But the *defaults* it sets are worth exporting to the live site.

---

## 3. Ship detail pages

**What it does.** Ship names in the matrix open a full page: 3D model viewer with orbit and zoom, acquisition panel (aUEC price, dealers, pledge price, RSI link), loadout slot grid, provenance line, related-ships strip.

**Identifiers:** `#cc-ship`, `#cc-bar`, `#cc-back`, `#cc-stage`, `#cc-canvas`, `#cc-still`, `CC_MODELS`, `CC_EMBED`

**Depends on:** three.js r128, GLTFLoader, OrbitControls, DRACOLoader — all inlined, no CDN.

**The loadout panel is deliberately empty.** It says "awaiting data" because hardpoint data lives in PostgreSQL and has not been wired in. Nothing is invented there.

**Pull it if:** the 3D models become a hosting problem. The rest of the panel would still be worth keeping.

---

## 4. Ship thumbnails

**What it does.** Shows a photo instantly and cross-fades it out when the 3D model finishes loading, so the stage is never blank.

**Identifiers:** `#cc-still`, `CC_SAFE()`, `testing/_deploy/images/`

**Built by:** `testing/_tools/mk_thumbs.py` — resumable, takes a start index and count. 241 images, 118 MB → 4.5 MB at 560px wide.

**Pull it if:** never worth pulling; it costs 4.5 MB and removes the "is this broken?" moment.

---

## 5. RSI links moved off the matrix

**What it does.** Ship names in the table were themselves links to RSI, so clicking a name left the site. Names are now plain text, the whole cell opens the detail page, and the RSI link lives inside that page.

**Identifiers:** `CC_RSI` (holds all 229 URLs), `.cc-open`

**All 229 URLs were preserved**, also exported to `rsi-ship-urls.json` / `.csv`. Nothing was discarded.

**Pull it if:** you decide the matrix should link straight out again. The URLs are already in `CC_RSI`.

---

## 6. Section rail (left edge)

**What it does.** The four page sections — Ship Purchase Matrix, Development Progress, Sale Calendar, Legend & Sources — as vertical tabs pinned to the left. Smooth-scrolls, highlights the section you are in, stays visible on ship detail pages.

**Identifiers:** `#cc-rail`, `body.cc-railed`, `body.cc-ship-open`

**Builds itself from whatever `nav a[href^="#"]` links exist**, so a fifth section on the live site appears automatically with no code change.

**Hidden below 900px** — a 46px vertical rail is unusable on a phone; the original horizontal links come back there.

**Pull it if:** the sections ever move to separate pages.

---

## 7. Category picker

**What it does.** "Browse by category" opens a popup of all 19 roles as chips, each showing its ship count. Clicking one filters the table; clicking again clears.

**Identifiers:** `#cc-browse`, `#cc-bcat`, `#cc-pcat`

**Replaces** the long "Categories you can search: …" text line, which is hidden.

**Drives the site's own `filterShips()`** by setting the search box — it does not duplicate the filtering logic.

**Pull it if:** the role sort (item 10) proves to be what people actually use. Worth watching which one reviewers reach for.

---

## 8. Manufacturer drawer (left edge)

**What it does.** A MANUFACTURERS tab pinned beside the section rail, always reachable however far you have scrolled. Slides out all 18 manufacturers with ship counts; clicking one jumps to that block.

**Identifiers:** `#cc-mtab`, `#cc-mdraw`, `body.cc-mdraw-open`

**Clears any active filter first** — a hidden row cannot be scrolled to.
**Closes an open ship page first** — otherwise you land behind an overlay.

**Hidden below 900px**, where the popup version (`#cc-bman`) takes over instead. Exactly one way in at any screen size.

**Pull it if:** the manufacturer count grows past what a single list can hold.

---

## 9. Column sorting

**What it does.** Click a header to sort. Ship name and Role sort A–Z, aUEC price and Pledge USD sort low-to-high. Click again to reverse, a third time to return to normal.

**Identifiers:** `th.cc-sortable`, `.cc-ind`, `data-cc-ord`, `window.ccResetTable()`

**Sorting turns manufacturer grouping off** — "cheapest ship" is a question about all 254, not about each brand separately. The status bar says so rather than leaving you to notice.

**Ships with no price always sort last**, both directions, so pledge-only entries do not pile up at the top of "cheapest".

**Pull it if:** never expected; this is table-stakes behaviour.

---

## 10. Dealer column filtering

**What it does.** Click a dealer column header — Area18, Orison, Lorville, Levski, Ruin Station — to show only ships sold there.

**Identifiers:** `th.cc-dealer`, `state.dealer`

**Pull it if:** the dealer columns change shape. It assumes columns 3–7 are the five dealers.

---

## 11. Budget filter

**What it does.** Type what you have in aUEC; ships above that price disappear.

**Identifiers:** `#cc-budget`, `state.budget`

**Ships with no aUEC price are excluded when a budget is set** — a budget is a question about aUEC, and a pledge-only ship cannot answer it. Showing them would read as "free".

**Why it exists:** prices run 28,350 to 65,356,200 — a 2,000× spread, median 2.6 million. 95 ships sit under 3 million, 156 under 10 million. There was previously no way to ask that question.

**Pull it if:** reviewers do not touch it. It is the newest and least proven item here.

---

## 12. Buyable-in-game toggle

**What it does.** Hides the 75 ships that cannot be bought with aUEC at all.

**Identifiers:** `#cc-buyonly`, `state.buyOnly`, `isBuyable()`

**Detects buyability structurally** — a purchasable row's price cell carries `.num`, a pledge-only row gets `.price-blank`. Not a guess about colour or text.

**Why it exists:** 75 of 254 ships, 30% of the table, are noise to anyone shopping with aUEC.

**Pull it if:** the colour coding turns out to be enough on its own.

---

## 13. Filter status bar

**What it does.** Shows every active sort and filter in plain words, with a Reset that clears all of them at once. Reset sits far left, description across the middle.

**Identifiers:** `#cc-state`, `#cc-state-txt`, `#cc-state-clr`

**Everything stacks.** Sort, dealer, budget and buyable-only compose in one visibility pass; the status bar lists whichever are on.

**Pull it if:** never while items 9–12 exist. Without it, people cannot tell why they are seeing fewer ships.

---

## 14. Feedback panel

**What it does.** An orange FEEDBACK tab opens the Jotform in an overlay. Loads the form only when opened, not on every page load. Closes with the X, Escape, or clicking outside. A "Send another response" button reloads just the form, since the embedded form otherwise sits on its thank-you page.

**Identifiers:** `#cc-fb-tab`, `#cc-fb`, `#cc-fb-frame`, `#cc-fb-again`

**Form:** `https://form.jotform.com/262126879809067`

**Needs internet** — it will not work in the standalone offline file.

**Pull it if:** the review round ends.

---

## 15. Section heading treatment

**What it does.** Section titles centred and enlarged from 1.15rem to 2rem (2.4rem on wide screens), with an accent rule underneath that follows the display engine's accent colour.

**Identifiers:** `main section > h2` overrides

**Why:** at 1.15rem against a 2.2rem page title, a section title read as a caption rather than a place.

---

## 16. Version banner — game label and split patch-note links

**What it does.** Names the game beside the LIVE and PTU version tags, and gives each tag its own destination: LIVE goes to that release's own RSI patch-note page, PTU goes to the Spectrum Patch Notes channel.

**Identifiers:** `.cc-scgame`, `.cc-patchlink`, `CC_PATCH`, `.sc-banner[data-cc-split]`

**Why the label:** the header reads "Citizen Compass v0.3.9" and the banner beneath showed 4.9.0 and 4.10.0 with nothing saying what they belonged to. Three version numbers, no labels.

**Why the split:** both tags shared one link to RSI's patch-notes index, and **that index lists LIVE releases only.** Clicking the PTU tag landed on a page with no PTU on it.

**PTU goes to the actual thread, guarded.** RSI publishes no PTU page and the wiki does not cover PTU either — both point at Spectrum. Every PTU build gets a *new* thread at the same base slug plus an incrementing suffix (6 threads for 4.10 alone, builds 12311913 → 12368639). So the direct link is stamped with the version it was recorded for, and **the code refuses to use it once the banner's PTU version moves past that** — it falls back to the channel and the tooltip says why. Forgetting to update it costs one extra click, never a wrong destination.

**The muted "build … · all builds ↗" is the escape hatch** for build-level drift, which the version gate cannot see: a newer build of the *same* version gets a new thread while the recorded link stays plausible and one behind.

**LIVE falls back the same way.** RSI assigns the comm-link ID and it cannot be derived from the version, so `CC_PATCH.live` is a lookup and an unrecognised version drops to the index — less specific, never wrong. Currently mapped: 4.9.0.

**Maintenance:** `CC_PATCH.ptuThread` per PTU build, `CC_PATCH.live` per LIVE release. Both are one line. `docs/workorder-patch-link-resolver.md` specifies the Go job that removes both — thread slugs are a walkable series and each thread's `<title>` states its build, so it automates cleanly.

**Pull it if:** never for the label. The direct PTU link could revert to channel-only if the per-build update is unwanted; the gate and the fallback stay useful either way.

---

## 17. Mobile layout corrections

**What it does.** Below 900px: DISPLAY and FEEDBACK become bottom pills, the section rail and manufacturer drawer hide, the popup manufacturer button returns, and the bottom edge is divided into lanes so nothing overlaps.

**Identifiers:** the `@media (max-width:900px)` blocks

**Four real defects fixed:** 130% default ate the first screen; the DISPLAY tab covered the Patch Notes link; `#backToTop` and the FEEDBACK pill overlapped; the sticky `.trademark-bar` sat under both pills. Verified with an all-pairs collision check at 390px.

---

## Two recurring lessons, recorded because they bit twice each

**Do not hold references to DOM the page owns.** The page rebuilds `#matrix-body`, and a captured row reports a zero rect once detached — which silently scrolls to the top instead of failing. Broke the manufacturer jump. Everything now resolves rows at click time.

**Do not match rendered text exactly.** Ship names gained a trailing link glyph and every lookup silently missed, leaving the whole table unclickable with no error. Matching is now normalised, and a miss should log rather than `return` quietly.

---

## Not built, deliberately

- **Shareable URL state** — a filtered view cannot currently be sent to anyone.
- **Ship comparison** — side-by-side for two or three ships.
- **Keyboard shortcuts** — `/` to focus search and similar.

Held until reviewers have used what exists, so the next additions answer observed behaviour rather than guesses.
