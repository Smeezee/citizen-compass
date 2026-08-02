# LATEST_HANDOFF.md — Update #130 — 2026-08-02 10:05 AM

---

# CITIZEN COMPASS — LATEST HANDOFF

Copy/paste this whole file into a new AI conversation for instant context. It's regenerated automatically — always the most current snapshot available.

---

## CURRENT STATE (auto)

**Generated:** 2026-08-02 10:05:01 (auto-regenerated every time a file lands in inbox/ or this script runs — don't hand-edit this section)

**Project health score:** 35/100
- Data completeness: 0%
- Viewer progress: 50%
- Documentation: 100%

**Ships:** 2 complete viewers / 4 total (50%)
- Complete: arrow, cutlass-black
- In progress / not started: constellation-aquila, gladius

**Data layers:**
- data-layer: 60646 files (10338.53 MB)

**Scripts:** 16  |  **3D models:** 723  |  **Docs:** 590

---

## RECENT UPDATES (append-only, newest first)

### 2026-08-02 10:04:31 — update_closing_final_push_before_move.md

# CLOSING UPDATE — final push before the machine is disassembled

**Nothing is in flight. Nothing is half-finished. Stopping here.**

## THE CHECK THAT MATTERS

```
git rev-parse HEAD origin/main
a32b8a3bc8ed45221fa13d3b79ed08badcdecbb3
a32b8a3bc8ed45221fa13d3b79ed08badcdecbb3
```

**Same hash twice. The push landed.**

## The brief's file count was stale — 16, not 63

It said 51 modified / 12 untracked. The working tree held **3 modified and 13
untracked**, and `HEAD` already matched `origin/main` at `7a72733` with nothing
landed after it. The larger figure was taken before the last three commits.
Saying so rather than quietly working to the smaller number.

## Committed — `a32b8a3`

`RECOVERY.md`, `data-layer/ship_resolution.json`, the editions/paints
acquisition finding, four work orders (front-end build plan, loadout real-data,
**loadout reader** — that one was not on the list but is a work order in `docs/`
and belongs), the three `20260802_09*` handoff entries, and the running handoff
record.

Nothing was outstanding under `checks/`, `scripts/` or
`data-layer/external-source-*` — all already committed earlier today.

## EXCLUDED — verified, not assumed

| file | why |
|---|---|
| `_c1_verify_wo.py` | one-off probe, 3.8 KB |
| `rescale_run_output.log` | 183 KB console output; its only unique content (four chassis cross-references) is already on disk in each ship's `MODEL_SOURCE.txt` and in the archived handoff entry |
| `testing/_src/_modelfolders.txt` | **checked against every build script — referenced by none** |
| `testing/_src/_scunpacked_names.json` | same; both are scratch, not build inputs |

The two `_src` files sit in a source directory, so I grepped the build code
before excluding them rather than trusting the label. Neither is read by
anything.

## MOVED ASIDE — not deleted, per rule 1

`testing/_deploy_lite/` → `_to_delete/deploy_lite_unclaimed_20260802/`
**245 files, 6.1 MB, referenced by no script, no config and no page.** Still
nobody's and still ungenerated, so it does not enter history.

Also cleared a **second stale `.git/index.lock`** — 0 bytes, six minutes old, no
`git` process of any kind running. Moved aside, not deleted. **That is the
second one today**, and something in this repo is not cleaning up after itself.
Worth knowing before the next session starts.

## Built from current source — verified by rebuild, not by mtime

| file | status |
|---|---|
| `testing/_deploy/index.html` | **rebuild is a byte-for-byte no-op** — `82271923…` before and after |
| `testing/_layer.html` | same mtime, same build pass |
| `testing/index.html` | same build pass — but see below |

**`testing/index.html` cannot be byte-verified.** `testing/build.py:26` injects
a UTC timestamp on every run, so it differs on each build by construction. Its
currency is established by mtime and by the layer it was built from, not by
hash. Stating that rather than implying a check I did not perform.

## The offsite copy was stale — found and fixed

The Cloudflare site served fine (200, `Hammerhead.glb` intact with a valid glTF
header), **but the bytes it served did not match the local build**:
served `be79501e…` against local `82271923…`.

That matters precisely because this is the offsite copy of the 349 MB deploy
build and the machine is about to be taken apart for three days. A site that
serves is not the same as a site that serves the current build — the same
distinction as a command exiting 0 versus the work being done.

Redeployed. This was completing the stated purpose of the check, not starting
something new: one proven command, run four times already today, content-
addressed so unchanged assets are not re-uploaded.

## State at stop

- `HEAD == origin/main == a32b8a3`, 0 ahead, 0 behind
- working tree: only the four deliberately-excluded scratch files
- Cloudflare serving the current build as the offsite copy
- `.env` untracked, three secrets, **one machine, no backup** — unchanged and
  still the largest single risk across this gap
- the UEX token remains unrotated after its screenshot exposure
- the Cloudflare token arrived over chat twice and is in a transcript; rotate at
  leisure, nothing depends on the value

## Not started, deliberately

The rule 14 enforcement proposal (`docs/proposal-rule14-single-writer-enforcement.md`)
is written and committed but **not implemented**, as instructed. It is the right
first thing to pick up, and it is a clean starting point rather than a
half-finished one.

### 2026-08-02 09:36:28 — update_plan_in_game_capture_overlay.md

# PLAN — in-game capture: what it would actually take

**From C2. 2026-08-02. Planning only. Nothing built, nothing written to the repository.**

Two answers here. The store-link question is §1 and it is short. The overlay
question is §2 onward, and it turned out better than expected — **the hard part
is already solved by a file the game writes.**

---

## 1. THE RSI STORE LINK ROUTE — dead end for the group that needed it

Measured across all 7,728 items.

    items carrying an RSI store link                    1,387
    price-without-description group                       461
      ...of those with a store link                        34   (7%)

    all items with no description                       2,384
      ...with a store link                                716   (30%)

    store links by section:  Liveries 601 · Armor 348 · Miscellaneous 127
                             Personal Weapons 106 · Clothing 101 · Undersuits 37

**34 of 461. The cheap fix is not there.** Worse, the links are unreliable as
image sources even where they exist — `ORC-mkX Arms Iceborn` points at
*Medical-Career-Kit-Medium*, and several Morozov-SH pieces share one
*Sangar-Helmet-And-Mo…* bundle page. **They are pledge-bundle pages, not item
pages.** An image scraped from one would frequently be the wrong object.

And 601 of the 1,387 are Liveries, which get no doorway and no screenshots.

**Conclusion: screenshots are the route for the 461. There is no shortcut.**

---

## 2. WHAT ALREADY EXISTS — do not rebuild it

`overlay_app.py`, `ask_engine.py` and `ASK_OVERLAY_SETUP.md` are already in the
repo. A `Ctrl+Shift+Space` global-hotkey popup, `tkinter`, runs headless under
`pythonw.exe`, searches local project files, falls back to a DuckDuckGo scrape,
answers through local `qwen3:14b` via Ollama.

**That is the shell.** What Sleven is asking for is a second mode inside it —
capture rather than ask. Its known limitations already recorded: hotkey
conflicts, and needing to run as Administrator to receive a hotkey while an
elevated game window has focus.

---

## 3. THE SAFETY BOUNDARY — non-negotiable, and there is a precedent

Star Citizen runs **Easy Anti-Cheat**. RSI's own knowledge-base article is
vague about third-party software — it addresses modded game files and says
nothing specific about overlays or capture tools — so the boundary has to be
drawn from what is demonstrably accepted rather than from a written permission.

**The precedent is `SCOverlay`, posted on RSI's own Community Hub.** It displays
in-game action names as keys are pressed, and it is built to be anti-cheat safe
by construction:

- **no DLL injection**
- **no function hooking**
- native Windows Raw Input API only
- reads the player's own `actionmaps.xml` off disk
- draws a transparent top-most window

**That is exactly the architecture to copy, and the line not to cross:**

    ALLOWED    read files the game writes
               read raw OS input
               capture the screen at OS level
               draw an overlay window

    NEVER      read or write game memory
               inject a DLL, hook any function
               send synthetic input into the game
               modify any game file

Anything in the second list risks a ban on Sleven's own account and would put a
Fan-Kit-compliant site next to a tool that violates the ToS. **The first list is
enough — see §4.**

---

## 4. THE FINDING — the game already logs the loadout, by name we can join

Read from `StarCitizen/LIVE/Game.log` and `LIVE/logbackups/`.

**Every session log carries the exact build:**

    FileVersion: 4.9.188.23497
    ProductVersion: 4.9.188.23497
    BackupNameAttachment=" Build(12344265) 01 Aug 26 (19 43 20)"

**Screenshots are already timestamped to the second** —
`ScreenShot-2026-07-22_11-29-29-35A.jpg` — and log lines are UTC to the
millisecond. **Correlating a screenshot to what was happening is arithmetic, not
guesswork.**

A real 39,159-line play session carries `[Cargo]` 13,057, `[Inventory]` 2,800,
`[Missions]` 1,536, plus location-bearing asset paths like
`data/objectcontainers/pu/loc/mod/stanton/station/ser/reststop_cargo/…`.

**And the `[Inventory]` lines are the prize:**

    <2026-01-28T22:38:17.463Z> [Notice] <AttachmentReceived> Player[Sleven-K]
      Attachment[rsi_odyssey_undersuit_01_01_01_200000000232,
                 rsi_odyssey_undersuit_01_01_01, 200000000232]
      Status[persistent] Port[Armor_Undersuit]

That middle field is a **ClassName**, and ClassName is a join key we already
hold — `stdItem.ClassName` in `fps-items.json` / `ship-items.json`, and the
suffix of `labels.json`'s `item_Desc_<ClassName>` keys.

### Tested, one session, against 10,804 catalogue ClassNames

    distinct attachment ClassNames in the session      49
      joined to the catalogue                          28
      not joined                                       21

**Every one of the 21 misses is a character-rig part** — `body_01_noMagicPocket`,
`FP_Visor`, `PU_Protos_Head`, `Head_Teeth`, `Shared_Scalp_Unified`, `brows_001`,
`Head_Eyelashes`, `universal_necksock_01`. Not gear, and correctly absent from an
item catalogue.

**On actual equipment the join rate is effectively 100%:**

    Armor_Undersuit   rsi_odyssey_undersuit_01_01_01        Odyssey II Undersuit Alpha
    Armor_Helmet      rrs_specialist_light_helmet_01_04_01  Arden-SL Helmet Archangel
    Armor_Torso       rrs_specialist_light_core_01_04_01    Arden-SL Core Archangel
    Armor_Arms        rrs_specialist_light_arms_01_04_01    Arden-SL Arms Archangel
    Armor_Legs        rrs_specialist_light_legs_01_04_01    Arden-SL Legs Archangel
    backpack          rrs_combat_light_backpack_01_04_01    Arden-CL Backpack Archangel
    wep_sidearm       klwe_pistol_energy_01                 Arclight Pistol
    magazine_attach_1 klwe_pistol_energy_01_mag             Arclight Pistol Battery (30 cap)
    medPen_attach_1   crlf_consumable_healing_01            MedPen (Hemozal)
    mobiglas_attach   MobiGlas                              mobiGlas Original Casing

### What this changes

**The player's real loadout is readable from a log file, with zero process
interaction.** No injection, no memory, no ToS question — the same safety class
as a tool RSI hosts a post about.

That does three things at once:

1. **It solves screenshot labelling.** A screenshot taken at 22:38:17 can be
   auto-tagged with everything equipped at 22:38:17 — with UUIDs, because
   ClassName resolves to UUID. The naming-by-UUID discipline from the capture
   protocol stops being manual.
2. **It delivers `claude/historian-loadout-context.md` without the manual step.**
   That doc assumed a player builds a loadout in the bench and hands it over.
   They would not have to. *"My power plant is dying, can I fix it at Everus"*
   becomes answerable because the log already said what is fitted.
3. **It is a differentiator no competitor has.** All four crafting tools and both
   keybinding tools are catalogues. **None of them knows what you are actually
   wearing.**

---

## 5. ARCHITECTURE — three layers, each independently useful

**L1 — the log reader (build first, no UI at all).**
Tail `Game.log`. Parse `<AttachmentReceived>` into
`{timestamp, port, class_name, entity_id}`, resolve ClassName → UUID → catalogue
row. Capture `FileVersion` at session start as the patch stamp. Emit a rolling
`session_state.json`.
**Testable entirely offline against the existing `logbackups/` — 39,159 lines of
real session already on disk.** No game needed, no overlay needed, no risk.

**L2 — capture and correlate.**
Use the game's own screenshot key so the game writes the file. A watcher on
`LIVE/screenshots/` matches each new file to the nearest L1 state by timestamp
and writes a sidecar: patch, UTC time, equipped items with UUIDs, and the last
location-bearing asset path seen.
**Deliberately no screen-capture API at first.** The game already writes a clean
JPG; adding an OS capture path buys nothing and adds a moving part.

**L3 — the overlay, extending `overlay_app.py`.**
A second hotkey that says *"tag the last screenshot"* and offers the equipped
items as the pick list, plus a free-text field for what a shop kiosk is showing.
**This is where a human closes the gap the log cannot** — the log knows what is
worn, not what is on a shelf.

**Order matters.** L1 is useful on its own (the Historian gets a loadout), L2 is
useful without L3 (screenshots arrive labelled), and L3 is pure convenience. If
the project stops after L1 it has still gained something real.

---

## 6. WHAT THIS CANNOT DO — state it before anyone assumes otherwise

- **It cannot read shop shelves.** Nothing in the log names an item on a kiosk.
  Prices and stock still come from UEX, or from OCR, or from Sleven typing them.
- **It cannot give a precise position.** Location comes from asset-path loading
  events — "a reststop in Stanton" — not coordinates. Good enough to say which
  station; not good enough to say which floor.
- **OCR is a separate project, and I would not start it.** Reading item names off
  a shop UI means handling the game's font, scaling, HDR, and every UI change per
  patch. Two of the four crafting sites already have community submission forms
  because this is harder than it looks.
- **It only ever knows Sleven's own session.** This is a personal capture tool,
  not telemetry, and it should stay that way — the moment it collects anyone
  else's data it becomes a privacy question and a very different conversation.

---

## 7. RISKS

- **EAC risk is low but not zero.** File reads and an overlay window are the
  SCOverlay pattern, but EAC behaviour changes without notice and RSI's article
  is not a permission slip. **Never run capture during anything competitive, and
  stop at the first sign of an EAC warning.**
- **Log format is undocumented and will change.** `<AttachmentReceived>` is an
  internal debug line, not an API. Parse defensively, assert the join rate stays
  near 100% on gear, and treat a sudden drop as "the format moved," not "the
  player changed clothes."
- **Administrator rights.** Already recorded in `ASK_OVERLAY_SETUP.md` — a
  global hotkey will not fire over an elevated game window unless the overlay is
  elevated too. That is a real friction point for L3, and it is why L1 and L2
  are designed to need no hotkey at all.
- **Log rotation.** `logbackups/` is how sessions persist; `Game.log` is
  overwritten on launch. **Anything not read before the next launch is gone.**

---

## 8. NOT VERIFIED

- **Whether `[Cargo]` lines name cargo contents.** 13,057 of them in one session
  and I only sampled four — they looked like elevator/platform loading, not
  manifests. **Worth a proper look; if they carry commodity names and amounts,
  the mining and trading side gets the same treatment as gear.**
- **Whether ship components appear as attachments** the way personal gear does.
  The sampled session was on foot. **If they do, the loadout bench gets its real
  data from the log too.**
- **Whether the location asset paths resolve to our 479 shops or 1,774 positioned
  entities.** They are file paths, not UUIDs, and the mapping is unproven.
- **Whether the join rate holds across sessions.** One session, 28 of 28 on gear.
- **Current EAC behaviour toward overlay windows.** Read RSI's article and the
  SCOverlay post; ran nothing.

### 2026-08-02 09:28:51 — update_decision_ship_honest_now_images_later.md

# DECISION — foundation first, images later, honesty as the standing constraint

**Ruled by Sleven, 2026-08-02. Recorded by C2. Planning only, nothing built.**

---

## THE RULING

1. **Foundation first.** The data is gathered. The job now is putting it where
   people can use it — not waiting for a better version.
2. **Images are a later, separate workstream.** Sleven will capture in-game
   screenshots of items, weapons, gear, locations and routes himself. It is
   legwork, it is attainable, and it does not gate anything.
3. **Ship what we have, presented as well as it can be presented.**
4. **The constraint: never misrepresent what the information is.** Partial is
   fine. Dressed-up is not.

Point 4 is the extension of rule 4 (*every price shows its age and its source*)
from prices to the whole site. **Rule 4 says how sure we are about a number.
This says how sure we are about a page.**

---

## WHY THIS IS THE RIGHT CALL, AND NOT JUST AN ACCEPTABLE ONE

**Only 136 items of 7,728 — 1.8% — have nothing beyond a name and a category.**
69% can say what a thing is; 36% can say where to buy it; 98.2% can say
something more than a name.

Waiting for images would hold back a site that can already answer more than any
competitor for the categories people actually search.

**And the images, when they come, will have better provenance than anything else
on the site.** The ship models came from a Hugging Face pack whose author's
redistribution rights are unestablished. UEX's 394 shop screenshots are
community-uploaded with unknown licensing. **Screenshots Sleven takes himself
have none of those questions** — known capturer, known patch, no third-party
redistribution. That makes the later workstream cleaner than the shortcut would
have been.

---

## PER-DOORWAY COVERAGE — measured, all 7,728

This was flagged as unknown in the Build A plan. 69% was the average; the split
matters more.

| doorway | items | with description | with price |
|---|---:|---:|---:|
| Clothing | 1,809 | **87%** | 58% |
| Food, drink & meds | 170 | **85%** | 69% |
| Ship parts | 758 | 74% | 63% |
| Suits & armour | 2,565 | 71% | 32% |
| Weapons & ammo | 558 | **50%** | **28%** |
| Tools & equipment | 111 | **50%** | **94%** |
| *(no doorway)* Liveries | 1,099 | 72% | 2% |
| *(no doorway)* Decorations | 77 | 52% | 19% |
| *(no doorway)* Miscellaneous | 334 | 19% | 12% |
| *(no doorway)* Commodities | 175 | **0%** | **0%** |

**No doorway is catastrophically thin — the worst is 50%.** The eight-doorway
structure survives the data.

Three things worth acting on:

- **Weapons & ammo is the weakest doorway** — 50% description, 28% priced — and
  it is a high-demand category. It will look thinnest exactly where people look
  hardest. **It is also the strongest candidate for the first screenshot batch.**
- **Tools & equipment is inverted** — 94% priced but only 50% described. It
  answers *"where do I buy it"* almost perfectly and *"what is it"* poorly. That
  is a different page emphasis, not a worse page.
- **Commodities is 0% and 0%.** Nothing at all. Confirms it gets no doorway, and
  is a second argument for pulling UEX commodity prices.

---

## THE ENGINEERING CONSEQUENCE — build the slot now, fill it later

Images being a later workstream is only cheap **if the data model expects them
today.** Retrofitting a media layer into 7,728 rendered pages is expensive;
declaring the field now costs nothing.

**Add to the item record in the Build A data contract, nullable from day one:**

    img       relative path, or null
    img_src   'sleven' | 'rsi_store' | 'uex' | null
    img_patch patch the screenshot was taken in
    img_date  capture date

`img_src` matters because the three sources have **different permission
stories** and a future question about one must not force a review of all of
them. `img_patch` matters because a screenshot of a 4.9 item is wrong by 4.12
and nothing else on the page would say so.

**The rendering rule from the coverage work still holds:** a null image produces
**no visible gap** — no placeholder box, no grey silhouette, no "image coming
soon." The layout is designed imageless and images are added *into* it, not
reserved *within* it.

---

## CAPTURE PROTOCOL — worth agreeing before the first batch, not after

The legwork is the expensive part. These are the things that are free at capture
time and unrecoverable afterwards.

1. **Record the patch version with every batch.** A folder per patch —
   `shots/4.9/` — is enough. Without it every image silently rots and nothing on
   the page can flag it.
2. **Name by UUID, not by display name.** `28c76343-8da9-495a-9339-3d5de02e6c3c.jpg`,
   not `venture-helmet-white.jpg`. Display names change between patches and
   collide — "Full Set" exists twice, "Container" exists twice. **UUIDs are the
   join key everywhere else on the site and they do not move.**
3. **One item, one frame, consistent framing.** A gear page with fifteen
   differently-lit, differently-cropped shots looks worse than no images at all.
   Same angle, same background, same distance — a shop inspection view is
   probably the most repeatable.
4. **Capture the shop, not just the item, when you are already there.** 394 of
   479 shops have a UEX screenshot of unknown licence. Our own would replace
   those cleanly, and a shop photo answers *"what does this place look like so I
   can find it"* — which nothing currently does.
5. **Start with Weapons & ammo.** Weakest doorway, high demand, and the 461
   price-without-description items are the group where a picture carries the most
   information.
6. **Do not capture liveries.** 1,099 items, 2% priced, no doorway. It is the
   largest category and the least worth the walking.

---

## WHAT THIS DOES NOT CHANGE

Nothing in `claude/plan-build-a-static.md` or `WO-CRAFT-01`. The four-question
standard, the no-visible-gap rule, and the doorway structure were all designed
imageless. **This ruling confirms the plan rather than altering it** — which is
the useful thing about having designed for the constraint before deciding to
accept it.

---

## NOT VERIFIED

- **Whether the 461 price-without-description items overlap the 1,387 carrying an
  RSI store link.** Still not computed. If they do, that group has a cheap
  legitimate image source before any screenshot is taken.
- **Whether RSI store images may be hotlinked or copied at all** under the Fan
  Kit position. Not researched.
- **What the 136 truly-bare items are.** Some are likely placeholder or debug
  records that should not get a page rather than a photograph.

### 2026-08-02 09:27:09 — update_coverage_and_newbie_standard.md

# The completeness picture, measured — and what "usable for the newest player" has to mean

**From C2. 2026-08-02. Planning input, not a build. Nothing written to the repository.**

Sleven's position: the missing images do not matter much if the information is
structured so the newest player can use it, because the asset is having
everything in one place that other sites scatter.

**That position is correct, and it is now measured rather than asserted.** But
it carries an obligation, in §3.

---

## 1. WHAT AN ITEM PAGE CAN ACTUALLY ANSWER — all 7,728 measured

|  | has a price | no price | total |
|---|---:|---:|---:|
| **has a description** | **2,337 (30%)** | 3,007 (39%) | 5,344 (69%) |
| **no description** | 461 (6%) | 1,923 (25%) | 2,384 (31%) |
| **total** | 2,798 (36%) | 4,930 (64%) | 7,728 |

Read as four different pages:

- **2,337 — the full answer.** What it is, what it costs, which shops, where
  those shops are, how old the price is. **No competitor has this combination
  for a single item.**
- **3,007 — "what it is" without "where to buy".** Still a real page: CIG's own
  description, category, manufacturer, and an honest line about stock.
- **461 — "where to buy" without "what it is".** Weakest class, and the one
  where a picture would help most.
- **1,923 — neither.**

## 2. THE FLOOR IS MUCH HIGHER THAN 25%

The 1,923 with neither description nor price are not blank. Checking what else
they carry — manufacturer, size, RSI store link, pledge-only flag, patch stamp:

    5 extra fields      3
    4 extra fields    202
    3 extra fields    385
    2 extra fields    515
    1 extra field     682
    0 extra fields    136

**Only 136 items — 1.8% of the catalogue — have nothing beyond a name and a
category.** The other 1,787 carry something worth putting on a page.

**So the real shape is:** 69% can say what a thing is, 36% can say where to buy
it, and **98.2% can say something more than its name.** That is a much better
starting position than "no images, 64% unpriced" suggests, and it is the number
that should be quoted internally instead of the scary one.

---

## 3. THE OBLIGATION THIS CREATES

"Usable for the newest player" is not a design intention. Left as one it becomes
a slogan that everybody agrees with and nobody can fail.

**Proposed testable standard — the four questions.** Every item page answers
these in plain words, above the fold, in this order, and **each has a defined
answer when the data is missing:**

| # | question | when known | when not known |
|---|---|---|---|
| 1 | **What is this?** | CIG's description | category + manufacturer + size, as a sentence |
| 2 | **Can I get it, and how?** | "Sold at 4 shops" | "You can't buy this in the game — it came with a pledge" *or* "No shop we know of stocks this" |
| 3 | **What does it cost?** | cheapest price + where | omitted entirely, never "N/A" or "—" |
| 4 | **How sure are you?** | price age + source | "This is a player report, and gear prices swing a lot" |

**Question 4 is the one nobody else answers at all**, and it is the whole reason
to trust the site over a confident wrong number elsewhere.

**This is assertable, which is the point.** Four coverage classes exist in §1;
the test is that a page from each renders all four questions with no blank
field, no dangling label, and no dash standing in for an answer. That is a rule
12 check, not a design review.

### The rule that follows

**A missing field must never produce a visible gap.** Not an empty heading, not
"Unknown", not a grey placeholder box where an image would go. **Sections
disappear; sentences change.** A page with three of four answers should look
like a page that was only ever meant to have three.

This is stricter than the earlier plan's "assert a page renders correctly with
optional fields empty" — that permits an empty-but-present section. At 64%
unpriced and 100% imageless, empty-but-present is most of the site.

---

## 4. WHERE THE "EVERYTHING IN ONE PLACE" CLAIM IS TRUE, AND WHERE IT IS NOT

Worth being precise, because the claim is the strategy.

**True:** UEX has prices and terminals but no item descriptions or stats. Erkul
has ship-component stats but no FPS gear, no prices, no locations. The wiki has
lore and some stats but not current prices. **The join across all of it exists
only here** — item, description, stats, price, shop, location, patch stamp,
confidence.

**Not yet true:** for the 461 price-without-description items we hold *less*
than the wiki does. For liveries and cosmetics we hold almost nothing anyone
wants. And for anything needing an image, we hold nothing at all.

**So the honest version of the claim is narrower and stronger:** *for the things
people actually search for — gear, weapons, components, consumables — this is
the only place the whole answer sits on one page.* It is not "we have everything
about everything," and it should not be sold as that internally, because the
first person to check a livery page will find out.

---

## 5. WHAT THIS CHANGES ABOUT BUILD ORDER

Nothing about the plan. One thing about priority:

**The description wiring (WO-CRAFT-01 §WO-1) is the highest-value item in the
project and this measurement raises it further.** It is the difference between
2,798 pages that can answer anything (36%) and 5,344 that can (69%). It needs no
new data, no decisions, and it is not blocked by the tab layout question that
holds up everything else in Build A.

**Images stay worth chasing for one narrow group** — the 461
price-without-description items, where a picture is the only thing that would
tell someone what they are looking at. 1,387 items carry an RSI store link,
which is the cheapest route to a legitimate image and has not been examined.

---

## 6. NOT VERIFIED

- **Whether the 461 overlap with the 1,387 carrying an RSI store link.** Not
  computed. If they do, that group has a cheap fix.
- **Whether the 136 truly-bare items are real game content** or debug/placeholder
  records. `fps-items.json` is known to carry ~230 placeholder entries, so some
  of the 136 may not deserve a page at all.
- **Whether descriptions are evenly spread across the doorways.** 69% is the
  total; a doorway sitting at 20% would look broken while the average looked fine.
  **Worth computing before the doorway pages are designed.**

### 2026-08-02 09:24:59 — update_craft_split_and_rule14_proposal.md

# UPDATE — craft indexes split page-per-file; rule 14 enforcement proposal delivered

## The amendment's question, answered with the distribution

**Per-file splitting alone does NOT bring p99 into range. The source list needs
its own file.** Measured over all 1,597 rows:

| | p50 | p90 | p95 | **p99** | max | >20 KB |
|---|---:|---:|---:|---:|---:|---:|
| whole row, `sources` inline | 2,191 | 12,690 | 18,334 | **63,706** | 91,648 | 74 files |
| `sources` moved out | 1,868 | 2,311 | 2,962 | **3,040** | 3,284 | **0** |
| `sources` alone | 2 | 10,832 | 16,150 | 62,559 | 90,637 | 74 files |

C1 was right that a 7 KB mean with a 90 KB tail is two problems. It is worse
than that: **p99 is 63.7 KB, 29x the median.** Splitting per blueprint moves the
tail from one file to 74 of them; it does not remove it.

Moving `sources` out collapses the page distribution entirely — **nothing over
3.3 KB, zero files above 20 KB.**

**The 127-source blueprint specifically:** `BP_CRAFT_klwe_pistol_energy_01_mag`
is 91,648 bytes, of which **90,637 (99%) is the source list**. Split, its page
is **971 bytes** and the 86 KB source list is fetched only if someone opens it.
The four next-largest are Mining Lasers at ~80 KB, also 98% sources. The tail is
entirely sources, in every case.

**A finding the split surfaced: 873 of 1,597 blueprints (54.7%) have an EMPTY
source list.** So a sources file is written only where there is something to
write — **724 files instead of 1,597**. Writing empty ones would have added 873
requests that can only ever return `[]`.

## What now exists

```
blueprints/<key>.json          1,597 files   3.06 MB   page data, no sources
blueprints/sources/<key>.json    724 files   5.68 MB   lazy-loaded
items/<id>.json                5,344 files   1.87 MB
blueprints/_list.json                        254.7 KB  minimal listing
                               ----------
TOTAL                          7,666 files
```

**File budget: 7,666 craft + 480 existing = 8,146 against a 20,000 cap — 11,854
headroom (59% free).** Comfortably inside the arithmetic C2 already did.

**What a visitor downloads now:**

| | before | after |
|---|---:|---:|
| landing on the craft index | **10.91 MB** | 254.7 KB |
| opening a blueprint | (already loaded) | **1.7 KB** (p50), 3.0 KB worst |
| its source list | (already loaded) | 86 KB, **only if opened** |

The combined indexes stay exactly as they are — build artifacts for derivation,
never fetched by a browser.

**Verified by round-trip, not by file count:** the worst row was reassembled
from its page plus its sources file and compared to the original — `True`.
`blueprint_key` is unique across all 1,597 and needs no filename sanitisation;
same for all 5,344 item keys. Both checked before writing, not after.

`scripts/split_craft_pages.py` rebuilds its output directories from scratch each
run, so a removed blueprint cannot leave a stale page behind.

## A 7,666-file accident, closed before it happened

`data-layer/processed/.gitignore` covered the combined `*.json` files but **not
subdirectories**. The split created 7,666 untracked files that a single
`git add -A` would have swept into one commit — the same way another session's
work has been swept twice already tonight. Added `blueprints/` and `items/`;
untracked count under `processed/` is back to **0**.

## Rule 14 enforcement proposal — delivered

`docs/proposal-rule14-single-writer-enforcement.md`. **Proposal only, nothing
implemented**, per instruction.

The short version: the two previous fixes worked because each had a
**registration choke point** a guard could refuse at. File writes have none —
three sessions, one OS user, one machine. **I cannot make the write impossible,
and claiming otherwise would be the enforcement-that-isn't this project keeps
finding.** So the target is rule 14's own second clause: make an unacknowledged
write loud, and refuse to ship un-provenanced content.

Mechanism: a tracked `LAYER.lock` holding the last owner-acknowledged sha256;
the build refuses when disk disagrees and names both hashes; writes go through
one helper that updates file and lock atomically; the deploy re-checks **at
upload time, not at start** — the lesson from staging files I had verified
minutes earlier that changed in between; and a daily checker reports drift even
if nobody builds.

**All four of tonight's incidents would have stopped at the build.** None was
malice and none was a stale-mtime mistake — every one was a session editing a
copy it believed was current. Incident 3 is the clearest: a genuine improvement
that happened to carry an old version of one line, silently reverting a
committed fix.

Limits stated in the doc rather than glossed: it does not prevent the write, it
does not recover clobbered content (git does, which is why committing after
every edit is part of the workflow), and it adds a step to every legitimate
edit.

## Layer state — checked, and the tab has NOT come back

`_layer.src.html` changed again since my commit (`889e4ff1` → `95177c82`,
+82 lines) and `cc-lo-tab` appears once, which looked like a third regression.
**It is not.** The single occurrence is a comment recording why the id was
dropped from the dock's IDS array. Live element `<a id="cc-lo-tab">`: **0**.
Style rule `#cc-lo-tab`: **0**. `id="cc-kb"` 1, `cc-ship::after` 2, `cc-strip` 7
all intact.

That is C2's A3 fix, which C1 has already accepted and checksum-verified.
Committing it so it is not lost — but noting that it reached me as a disk write
rather than as an edit from C1, which is precisely the traffic the new workflow
is meant to end.

**No deploy performed** — the amendment did not ask for one, and the split
output is not wired into any page yet.

### 2026-08-02 01:45:59 — update_plan_build_a_static.md

# PLAN — Build A (find / item / shop) under the static ruling

**From C2 to C1. 2026-08-02. Planning only. Nothing built, nothing written to the repository.**

Written after reading `docs/order-front-end-build.md` and the 2026-08-02 handoff
archive, so it starts from the rulings rather than from my earlier plan. Where
this and `docs/workorder-front-end-build-plan.md` disagree, **this is the
correction** — the differences are listed in §7.

---

## 1. THE MEASUREMENT THAT SETTLES THE ARCHITECTURE

The static ruling left an open question nobody had measured: whether a static
site can actually carry 7,728 items, 23,734 prices and 479 shops.

**It can, easily. Measured, trimmed to the fields the front end needs, gzipped:**

| payload | rows | raw | gzipped |
|---|---:|---:|---:|
| item index — id, name, category, section, manufacturer, uuid, slug | 7,728 | 1.16 MB | **0.28 MB** |
| price table — item, terminal, buy, sell, date | 23,734 | 1.15 MB | **0.15 MB** |
| shop table — 479 item terminals with location fields + game_version | 479 | 0.07 MB | **0.01 MB** |
| **total** | | **2.38 MB** | **0.44 MB** |

**The entire searchable catalogue is under half a megabyte over the wire.**

For scale: `testing/_deploy/index.html` is already 1.5 MB, and `_deploy/` is
**349 MB** — 235 ship models. The data is noise next to what already ships.

### What follows from it

- **No page-per-item build.** Three JSON files, client-side routing. That is
  **3 files against the 20,000 cap, not 8,867.** The cap stops being a
  consideration at all.
- **No sharding, no lazy-loading of the core three.** They load once and the
  whole site is interactive.
- **No FastAPI, and now for a second independent reason.** The ruling rested on
  the zero-runtime-dependency property. This adds: there is nothing a backend
  would do here that 440 KB of JSON does not already do faster.

### The one payload that does NOT go in the bundle

**Descriptions.** 5,344 items carry CIG prose (WO-CRAFT-01 §WO-1), averaging
several hundred characters — roughly 2.7 MB raw before compression. That is six
times the rest of the bundle combined for something only ever read one item at a
time.

**Shard them.** `desc/<bucket>.json` keyed by item id, bucket = `id % 64`, fetched
on demand when an item page opens. 64 files, ~40 KB each. Still trivially inside
the cap.

---

## 2. DATA CONTRACT

Emitted by a build step from the sealed snapshots, into `testing/_deploy/data/`.

    items.json      [{i:id, n:name, c:category, s:section, m:manufacturer,
                      u:uuid, g:slug, x:exclusivity, p:parent_id, col:color}]
    prices.json     [{i:id_item, t:id_terminal, b:price_buy,
                      s:price_sell, d:date_modified}]
    shops.json      [{i:id, n:name, ty:type, sy:star_system, p:planet,
                      ss:space_station, ci:city, o:outpost, gv:game_version,
                      f:{food,medical,shop_fps,shop_vehicle,freight_elevator}}]
    desc/NN.json    {item_id: "description text"}     64 shards
    meta.json       {snapshot, patch, built_at, counts}

Single-letter keys are not premature optimisation — they are most of the gap
between 2.38 MB and something worth thinking about. **Document the mapping in
`meta.json` so it is not folklore.**

**Joins, all by id, none by name:**

    items.i  ->  prices.i
    prices.t ->  shops.i
    items.u  ->  desc shard        (uuid only used to build the shard, not at runtime)

---

## 3. THE DOORWAYS

Eight, ordered by how many *priced* items sit behind them. Full reasoning in
`claude/plan-doorways-and-browse-layer.md`; corrections to it are in §7.

| # | doorway | UEX sections | items | priced |
|---|---|---|---:|---:|
| 1 | Suits & armour | Armor, Undersuits | 2,565 | 815 |
| 2 | Clothing | Clothing | 1,809 | 1,055 |
| 3 | Weapons & ammo | Personal Weapons | 558 | 157 |
| 4 | Ship parts | Systems, Vehicle Weapons, Avionics, Propulsion, Module | 758 | 474 |
| 5 | Tools & equipment | Utility, Technology | 111 | 104 |
| 6 | Food, drink & meds | Misc → Foods #63, Drinks #62, Consumables #16 | 170 | ~110 |
| 7 | Ships | source 1 + `ship_resolution.json` | 254 live | — |
| 8 | Places | shops, stations, cities, planets, systems | 479 shops | — |

Liveries (1,099), Decorations (77), Flair (31), Commodities (175), Other (41) and
the `Miscellaneous → Miscellaneous #61` bucket (325) are **findable by search and
tag, with no doorway.** That is the point of tags.

**Doorway 7 must use `data-layer/ship_resolution.json`** — 254 live, 215 matched,
2 ambiguous, 37 without a game file, 6 tier variants, **95 game files parked by
Sleven, do not surface them.** Do not re-derive this.

**Each doorway page is:** an honesty sentence with real counts → sub-category
tiles with count and priced-count → the views strip → nothing else.

---

## 4. THE THREE PAGES

### 4.1 Search

One text field, ordinary English. Stop-word strip before matching (list in
`docs/workorder-front-end-build-plan.md` §A1). Match against name, category,
manufacturer, shop name, place name. Location-aware: *"flight suits new babbage"*
ranks New Babbage stock first and says why.

Nine real test phrases are in that plan and are the requirement, not a
convenience. **A real phrase returning nothing is a search bug.**

Runs entirely client-side over `items.json` — 7,728 rows is nothing to filter in
a browser.

### 4.2 Item page

Order: breadcrumb → header → **description** → answer line → where to buy → sell
line (conditional) → confidence panel → others in this category.

**Description sits above the answer line and is the biggest change from the
earlier plan.** 69% coverage, against 36% for price and 0% for images. Two
rendering modes — prose, and CIG's newline-delimited stat blocks
(*"Item Type: Heavy Armor / Damage Reduction: 40%"*). **My detection heuristic
for telling them apart is untested — validate against a sample.**

**Answer line:** *"Sold at 4 shops. Cheapest is Casaba Outlet in Area18 at
12,400 aUEC."*

**For the 4,930 items with no price**, the answer line changes rather than
disappearing:

    exclusive (1,313)   "You can't buy this in the game. It came with a pledge."
    unexplained (2,524) "No shop we know of stocks this."
    liveries (1,080)    cosmetic; treated as above

**Sell price is one conditional line, not a section** — 171 items of 7,728 have
one.

**Price age colouring must come off the real distribution:** median 66 days, 75%
over 30 days. The earlier plan's "amber at one day old" would render the whole
site amber. Suggested fresh <30 / amber 30–75 / red >75 — **Sleven's call, not
mine.**

### 4.3 Shop page

479 shops, not 823 — 823 counts fuel, refinery, commodity and rental terminals
too. 469 have at least one price row.

Breadcrumb built from **whichever location fields are non-null**, not a fixed
shape: of 479 item terminals, space station is set on 379, planet 340, city 65,
outpost 39, moon 9, system 479. **The earlier plan's "system › planet › city ›
shop" is the minority path.**

Answer line, what they sell, what they buy, also-at-this-location.

**Shops have pictures — 394 of 479 carry a `screenshot`.** Whether we may display
UEX-hosted community screenshots is unresolved and touches the 7 unread
`fan_kit_compliance` warnings. **Design the page to work without them and treat
images as an enhancement pending that answer.**

Each shop carries `game_version` — a real last-verified-patch, set on 429 of 479,
and mostly stale (3.24.2 on 154, 4.0 on 108). Show it. Nobody else does.

---

## 5. ENTRY POINTS — planned both ways so this does not block

The tab layout is the only decision still blocking Builds A, B and C. **Both
branches are planned so work can start before it lands.**

Measured: the base page's nav is at `releases/latest.html:452-454` and uses
**in-page anchors** (`#matrix`, `#calendar`), not page links. That matters —
"put FIND in the nav" is not a one-line change to an existing pattern.

**Branch 1 — C1's recommendation (my preference).** DISPLAY and FEEDBACK stay on
the right edge. FIND and KEYBINDS become nav entries. LOADOUT already goes on the
ship page. Since the nav is anchor-based, either the nav gains its first true
page link, or Find becomes a section on the same page. **The second is more
consistent and cheaper, and suits a client-rendered app.**

**Branch 2 — right edge keeps everything.** Requires solving the geometry:
five tabs at `44% + 0/150/290/430/570px` puts FIND at 1045px on a 1080px
viewport. Only works at 1440p. Not recommended.

**Either way the build owns an explicit list with an explicit position per
entry, controlled by Sleven** — not re-emitted from whatever was last in the
file. That is the correction to my §8a, which would have restored the LOADOUT
tab after every rebuild and overridden a decision already made twice.

---

## 6. VERIFICATION — HARD RULE 12

- **Assert the bundle stays under 1 MB gzipped.** Measured 0.44 MB today. This
  is the assertion that keeps the static ruling true as data grows.
- **Assert every one of the nine real search phrases returns a correct result.**
- **Assert an item page renders complete with description, price and image all
  empty.** 2,384 items have no description; 4,930 have no price; 7,728 have no
  image. **All three absent at once is the common case, not the edge case.**
- **Assert a price never renders without its age and source.**
- **Assert the shop breadcrumb renders for a terminal with no city** — 414 of
  479 have no `city_name`.
- **Assert no name-based join anywhere.**
- **Assert the 95 parked game-file ships never appear.**
- **Assert the compliance footer is present on every page and every overlay.**

---

## 7. CORRECTIONS TO MY EARLIER PLANS

Both live in the project and the repo; treat these as amendments.

| # | earlier claim | correction |
|---|---|---|
| 1 | "823 shops" | **479** item terminals, 469 with a price row |
| 2 | "What it sells for" as a page section | **171 items of 7,728 (2.2%)** — one conditional line |
| 3 | "amber at a day old" | median age **66 days**; 75% over 30. Thresholds from the distribution |
| 4 | "design pages that work without a picture" | true for items (0 of 7,728); **false for shops** (394 of 479) |
| 5 | "no 'what it's good for' — that's writing, not data" | **5,344 items (69%)** have CIG prose |
| 6 | "Build B forces the FastAPI backend" | **ruled against.** §1 shows nothing needs it |
| 7 | §8a — build re-emits the tabs | **would override Sleven's LOADOUT removal.** Do not implement |
| 8 | "verify the `Loadout` array across ships" | **confirmed by C1**, 10 of 10. Closed |
| 9 | ship identity not addressed | **`ship_resolution.json` exists.** Use it |
| 10 | `commodity_trade_locations.json` gives where-to-buy | **tag-matched, not stock.** 15 materials share one identical 468-location set |

---

## 8. WHAT I DID NOT VERIFY

- **The stat-block vs prose detection heuristic.** Mine, untested.
- **Whether the nav can take a page link at all** without disturbing the
  anchor-scroll behaviour. Read the markup; did not test.
- **Description coverage per doorway.** Total is 69%; the split is unknown, so I
  cannot say whether Ship parts reads better or worse than Clothing.
- **Whether `is_available` / `is_available_live` / `is_visible` should filter
  shops.** 768 / 755 / 773 of 823 are true. Meaning unknown — **check UEX's docs
  before using them**, or ~20 shops get wrongly shown or hidden.
- **Licence and hotlink status of the 394 shop screenshots.**
- **Real gzip transfer size**, as opposed to my `gzip.compress` estimate.
  Cloudflare may use brotli, which would be smaller.

---

## 9. OPEN FOR SLEVEN

1. **Tab layout** — branch 1 or 2 in §5. Blocks A, B and C.
2. **Price-age thresholds** — fresh/amber/red boundaries.
3. **Shop screenshots** — display or not, given the Fan Kit position.
4. **Does Clothing get its own doorway**, or fold into Suits & armour? It is the
   best-covered data on the site — 1,055 of 1,809 priced — and burying it costs
   the most of any single call here.

### 2026-08-02 01:41:24 — update_craft01_wo1_wo2_done.md

# UPDATE — WO-1 and WO-2 complete. All assertions hold, including C1's three unverified numbers.

## Preconditions

`categories.json` `3de4f9fa2bf7674d`, `items_prices_all.json` `308542bf043df9c2`
— both match. Sealed snapshots intact. blueprints 1597, contracts 5108.

## WO-1 — PASS

| assertion | got | want |
|---|---:|---:|
| matched | **5344** | 5344 |
| fps records with text | **5182** | 5182 |
| ship records with text | **2598** | 2598 |
| UEX items | **7728** | 7728 |

Join is UUID-only by construction; no name match is possible in that code path.
Output 2.05 MB.

## WO-2 — PASS. The three unverified numbers CONFIRM.

**This was C2's verification and it holds:**

| assertion | got | want |
|---|---:|---:|
| contracts carrying `Blueprints[]` | **768** | 768 |
| blueprints with >=1 contract | **676** | 676 |
| **max sources on one blueprint** | **127** | 127 |

C1's reconciliation arithmetic was right: the numbers only closed if these were
correct, and they are.

Every remaining assertion also holds — rows 1597, the full `source_kind`
distribution, 4274 leaves, 298 lacking QuantityScu and all `item`, every leaf
with MinQuality, 721 priced, 1537 with modifiers, `ingredient_cost` null
throughout.

**Performance:** the contract scan took **1.5 seconds**, not the 45+ a naive
scan costs. The substring pre-filter cut 5,108 files to 768 — and 768 qualifying
on `"PoolUUID"` is exactly the count that carry `Blueprints[]`, so the filter is
lossless here rather than merely fast.

## FILE SIZE — this bears on the static-JSON ruling

**`blueprint_index.json` is 11,439,463 bytes — 10.91 MB.**

The ruling assumed page-sized payloads. This is one file, and the `sources[]`
arrays are why: 676 blueprints carry contract sources, up to 127 each.

It does not reverse the ruling — the ruling rests on zero runtime dependency,
not on payload size — but **10.91 MB is not a page payload.** WO-3 reads WO-2,
and if a blueprint page fetches this file to render one row, that is 10.91 MB to
show one blueprint. The shape that works is per-blueprint shards or an index
plus lazy source fetch. Flagging now because it is cheaper to decide before 1,597
pages are built on it than after.

Not tracked in git: `data-layer/processed/.gitignore` added, on the same
reasoning as `journal.jsonl` and `*_perfile.json` — large, fully reproducible
from tracked sealed snapshots, with exact assertions recorded in the work order.

## OPEN ITEM 1 — SETTLED. `resources.json` does NOT hold mining locations.

Opened all 557 records. **The union of every key across every record is:**

```
AdditionalWaitForNearbyPlayersSeconds, Composition, DespawnTimeSeconds,
GlobalParams, HarvestableKey, HarvestableUUID, Key, Kind, Name, Parts,
RespawnInSlotTime, Signature, Tier, UUID
```

**No planet, moon, system, body, region, deposit or site field exists.** The
hypothesis is disproven. "Where to mine it" stays empty in WO-5 — but now for a
*verified* reason rather than "no source found", which is a materially better
thing to be able to say on 37 pages.

### But it is not a dead end — it answers a different question

`Kind` distribution: **cave_harvestable 244, mineable 274, salvageable 25,
harvestable 14.**

That is *how* a material is obtained, which is precisely the distinction WO-5
needs for the 11 hand-mined gems ("hand-mined, not traded as cargo"). Currently
that split is asserted from their absence in `commodities.json` — an argument
from silence. `Kind` would make it positive evidence.

14 of the 37 ingredients appear here by name. **I did not join on name** —
FORBIDDEN 1. Records carry `UUID` and `HarvestableUUID`, so a UUID join is
available and is the only one I would use.

**Data-quality note:** many `cave_harvestable` records carry
`Name: "<= PLACEHOLDER =>"`. Any page reading `Name` from this file must handle
that, or placeholder text ships to users.

## VOCABULARY RECONCILIATION — reporting, not picking

C2's `source_kind` (blueprints) and the acquisition routes (ships, paints,
editions) are the same question — *how do you get this* — arriving from two
directions.

**Proposed: two levels. Level 1 is the honest one-line answer; level 2 keeps the
precision neither side should lose.**

| L1 | L2 | covers |
|---|---|---|
| **bought** | `shop` | aUEC at a named terminal — UEX prices, dealer columns |
| | `pledge` | real money on the RSI store |
| | `trade` | exchanged for goods, not currency — Wikelo Emporium |
| **awarded** | `mission` | completing contracted work — C2 `contract`, 676 |
| | `event` | time-limited event — C2 `event`, 31 (XenoThreat, RedWind) |
| | `reward` | status or standing, no specific action — C2 `direct_reward` 16, `other_pool` 1, plus Subscriber/Concierge |
| **included** | `factory` | arrives fitted, never separately obtained — War/Sneak Specials |
| | `default` | available without acquisition — C2 `default`, 8 |
| **unknown** | `unknown` | the files do not say — C2 `none`, **865** |

**Why two levels rather than one flat list.** Your point was that a
contract blueprint and a Subscriber livery are both "awarded, not bought". At L1
that is one word and the site can say it once. At L2 they stay distinguishable,
because *how* you earn them differs completely. A single flat vocabulary forces
a choice between losing the shared idea and losing the distinction.

**Mapping is total and lossless in one direction:** every C2 value and every
acquisition route maps to exactly one L2 term, and no L2 term is unreachable.
`other_pool` folds into `reward` — it is one row, the Microsatellite probe, and
"awarded by some pool we cannot classify" is a `reward` with low confidence, not
a category.

**`unknown` deliberately keeps its own L1.** Folding it under any of the other
three would assert something the files do not support — 865 blueprints, 54%, is
far too much to guess about.

**Not implemented.** WO-2's output currently carries C2's `source_kind` verbatim
so the assertions could be verified exactly as written. Remapping is a
mechanical pass once the vocabulary is ruled — and it must happen before WO-3
renders any of it, or the two taxonomies ship.

## Stopping here

WO-3 (1,597 pages), WO-4 and WO-5 are not started. WO-3 renders `source_kind`
prose, so it is downstream of the vocabulary ruling, and the 10.91 MB payload
shape should be settled before pages are built against it.

### 2026-08-02 01:38:03 — update_craft01_intake.md

# UPDATE — WO-CRAFT-01 received, starting

Filed on intake per rule 13.

**Filename note:** the order was given as
`docs/workorder-crafting-and-descriptions.md`, which does not exist. It is
`docs/workorder-craft-01.md` (plus `workorder-craft-01-addendum.md`). WO-CRAFT-01
matches unambiguously so I am proceeding, flagging rather than guessing silently.

## Taken as verified, not re-derived

C1 independently measured and matched: preconditions hashes, file counts
(blueprints 1597, contracts 5108, fps-items 5420, ship-items 5384), WO-1
(7728/5344), and the WO-2 numbers derivable from `blueprints.json` alone.

## The three numbers C1 could NOT verify

768 contracts with `Blueprints[]`, 676 blueprints with a contract, max 127
sources — the scan exceeded C1's 45-second window. They reconcile arithmetically
(693 either way, and the no-pool bucket of 865 matches exactly), but the scan has
not been run.

**My first run is their verification. If any differ, that is the finding — I
stop and report rather than adjusting the assertion.**

## Before WO-2

Reconciling C2's `source_kind` with the acquisition routes in
`docs/finding-editions-paints-acquisition.md` into one vocabulary, and reporting
it rather than picking silently.

## Holding

- Assertions stay exact. Not softened to ranges. A break is the signal.
- No name-based joins; UUID only.
- No estimates, no placeholders, no ingredient cost.
- Reporting WO-2's output file size — it bears on the static-JSON ruling.

### 2026-08-02 01:34:56 — update_schema_authority_closed.md

# UPDATE — alembic drop hazard CLOSED, and the class closed with it

All four items done. Uncommitted pending a go-ahead (rule 2).

## A correction to the ruling's premise, found before acting on it

The ruling said to retire **schema-init's** creation of `ship_registry`.
**schema-init never created it.** It creates only the three `pipeline_*` tables.

`ship_registry` is created by **`registry-builder/main.go`** (`ensureSchema()`,
line 331). So there were **three** schema authorities, not two — which is itself
the argument for building the control rather than fixing the instance.

## 1. `ship_registry` declared — and it matches exactly

Added to `app/models.py`, mirroring `registry-builder`'s DDL column for column:
`ship_code` varchar(20) unique, `manufacturer_code` varchar(10),
`manufacturer_name` varchar(150), `ship_name` varchar(150), `source_slug`
varchar(150) unique, `folder_slug` varchar(150) nullable, `created_at` timestamp
default now().

**The match was verified, not assumed.** After declaring it, `alembic check`
dropped `remove_table:ship_registry` and proposed **no ALTERs in its place** —
which was the sharper half of the concern. A near-miss model would have been
quieter and equally wrong.

Deliberately not a `VerifiableMixin` table: it is a generated cross-index
rebuilt from source, not community-sourced data with its own provenance story.

## 2. The three `pipeline_*` tables excluded, by name

`alembic/env.py` gains `EXCLUDED_TABLES` and an `include_object` hook, wired
into **both** `configure()` calls (offline and online — one would have been a
silent half-fix).

Held to the conditions:

- **Named explicitly.** No pattern match. A `pipeline_*` prefix rule would
  silently adopt the next table someone adds, which is precisely the failure
  being closed.
- **Commented** with who owns the DDL (`schema-init/main.go`) and why:
  subsystem telemetry, written only by `findings_store.py` and `framework.py`,
  read by nothing in `app/`, schema moving with the checker layer.
- Records that this is the **one-writer-per-artifact** rule applied to schema —
  two authorities over one table being the same defect as two watchers on one
  handoff file.
- Notes explicitly that `ship_registry` is *not* in the list, and why.

**Result: `alembic check` now reports "No new upgrade operations detected."**
The hazard is closed — autogenerate would emit nothing.

## 3. The control — `checks/schema_checks.py`

`schema_ownership`: every live table must be claimed by **exactly one**
authority.

- claimed by **neither** -> DEFECT (an unregistered table; autogenerate will
  propose dropping it and the proposal will look ordinary)
- claimed by **both** -> DEFECT (ambiguous ownership)
- named but absent -> WARNING (a boundary pointing at nothing)
- `alembic_version` handled as legitimately neither

It parses `EXCLUDED_TABLES` from source rather than importing `env.py`, because
importing it runs alembic's configuration machinery and needs a live
connection — a checker that requires the thing it checks to be healthy is not
much of a checker.

### Rule 12 — the guard was made to fire

| case | result |
|---|---|
| table claimed by **neither** | **DEFECT, names the table** |
| table claimed by **both** | **DEFECT, "BOTH"** |
| declared table | not flagged |
| excluded table | not flagged as unclaimed |
| offenders removed | **PASS** |
| no session | **LIMITATION**, never a false PASS |

`env.py` was tampered with to force the double-claim case and **restored
byte-identical**, asserted.

**The proof caught a design flaw in my own checker.** PASS was keyed on *no
findings at all*, so a stale-exclusion WARNING suppressed it — meaning a run
that verified the invariant would look identical to one that never checked.
That is the exact failure this layer exists to catch, in the layer itself. PASS
is now keyed on the absence of DEFECTs.

Registered in `db_checks.py`. Live run against the real database:

```
14 findings: DEFECT=0  WARNING=3  LIMITATION=0  PASS=11
[schema_ownership] all 19 tables claimed by exactly one authority
                   (15 declared in models.py, 3 externally owned, 1 alembic-internal)
```

**DEFECT count is now 0** — the schema_drift DEFECT is gone.

## 4. The 22,988 flip recorded

Written into `docs/order-front-end-build.md` beside the ruling, with both
numbers, why 21,849 is real, why the non-recursive glob produced "items/ is
empty", and the note that the ruling rests on the zero-runtime-dependency
reason precisely because a decision resting on the file count would have
flipped on a definition.

## One thing NOT done, and it is a judgement call

**`registry-builder/main.go` still contains `CREATE TABLE IF NOT EXISTS
ship_registry`.** So `ship_registry` currently has two creators: alembic (via
the model) and registry-builder.

I did not retire it, for a reason worth stating: **no alembic migration creates
`ship_registry`.** The model matches the existing table, so autogenerate
proposes nothing — correct for this database, but it means a **fresh** database
would never get the table if registry-builder stopped creating it. Retiring the
Go DDL therefore needs a migration that creates it, written as a no-op where it
already exists, applied under a fresh verified backup.

That is a real change to a tool's bootstrap behaviour, on a premise that turned
out to be different from the ruling's. Flagging rather than doing it.

**The new checker does not currently catch this**, because it compares against
`models.py` and `EXCLUDED_TABLES`, not against Go source. Detecting "two things
create this table" is a different check — worth having, not built.

## Uncommitted

`app/models.py`, `alembic/env.py`, `checks/schema_checks.py`,
`checks/_verify_schema_checks.py`, `checks/db_checks.py`,
`docs/order-front-end-build.md`. No commit go-ahead was given for this change.

### 2026-08-02 01:29:31 — update_schema_authority_intake.md

# UPDATE — closing the alembic drop hazard, and building the control

Filed on intake per rule 13.

## Ruling received

- `ship_registry` -> declare in `app/models.py`, and **retire schema-init's
  creation of it in the same change** so one table has one authority.
- The three `pipeline_*` tables -> `include_object` exclusion that **names them
  explicitly**, with a comment recording that `schema-init/main.go` owns their
  DDL and why.
- **Build the control**: a checker asserting every table is claimed by exactly
  one authority. Claimed by neither = an unregistered table. Claimed by both =
  drift. Either is a finding.
- Record the 22,988 flip in the front-end order.

## One consequence I need to handle carefully

Retiring schema-init's creation of `ship_registry` leaves **nothing** creating
it on a fresh database unless alembic does. So the change is not just "delete
the Go DDL" - it needs a migration that creates the table, written so it is a
no-op where the table already exists.

That means `alembic upgrade head` against the real database, which means
**rule 4: verified backup first.** The last one predates tonight's 3,751 rows.

## Order

1. Read schema-init's DDL and the live table definition, and match the model to
   both exactly - a mismatch produces ALTERs instead of drops, which is quieter
   and still wrong.
2. `include_object` exclusion, naming the three tables.
3. Conditional migration for `ship_registry`.
4. Verified backup.
5. Apply, then confirm `alembic check` is clean.
6. Build the ownership checker, with rule 12 proof: create a table in neither
   place and confirm it is reported. A guard that has never fired is not a
   guard.
7. Record the 22,988 flip.

Not committing without a go-ahead per rule 2.

### 2026-08-02 01:25:09 — update_models_gap_options_and_21849.md

# UPDATE — the alembic drop hazard: options and consequences. Plus 21,849 solved.

Reporting, not choosing, as instructed.

## THE HAZARD, measured

`alembic check` proposes **10 operations — 4 table drops and 6 index drops**:

```
remove_table:pipeline_check_results     remove_index:ix_pipeline_check_results_check_name
remove_table:pipeline_check_runs        remove_index:ix_pipeline_check_results_checked_at
remove_table:pipeline_findings          remove_index:ix_pipeline_check_runs_started_at
remove_table:ship_registry              remove_index:ix_pipeline_findings_check_name
                                        remove_index:ix_pipeline_findings_last_seen
                                        remove_index:ix_pipeline_findings_status
```

**3,751 rows at risk:** `pipeline_check_results` 3,057, `pipeline_findings` 383,
`ship_registry` 295, `pipeline_check_runs` 16.

Confirmed: **zero** occurrences of any of the four in `app/models.py`.

**Root cause is two schema authorities.** `schema-init/main.go` creates
`pipeline_check_results`, `pipeline_findings` and `pipeline_check_runs` with
`CREATE TABLE IF NOT EXISTS`. Alembic has never heard of any of them, so
autogenerate reads them as tables that should not exist. `ship_registry` is in
the same position.

The danger is specifically `alembic revision --autogenerate`. Its output looks
like ordinary work — a migration file full of plausible operations — and nothing
in it announces that it is about to drop a night's findings.

## OPTION A — declare the models in `app/models.py`

**Consequence:** autogenerate stops proposing the drops. Alembic becomes the
single authority.

**Cost, and it is not zero:** the models must match `schema-init`'s DDL
*exactly* — column types, nullability, server defaults, index names. Any
mismatch and autogenerate proposes ALTERs instead of drops, which is quieter but
still wrong. And `schema-init/main.go` would then be creating tables alembic
also manages: harmless while it stays `IF NOT EXISTS`, but two things creating
one table is the condition that produced this hazard in the first place. Closing
it properly means retiring schema-init's table creation, which is a second
change.

## OPTION B — exclude them via `include_object` in `alembic/env.py`

**Consequence:** autogenerate ignores those tables. No drops proposed.

**Cost:** they stay outside alembic permanently, so every future change to them
is manual. It silences the symptom while keeping two authorities.

**But it is not purely a workaround, and this is the part worth weighing:**
`include_object` exists precisely to say "these objects are owned elsewhere."
For the three `pipeline_*` tables that is arguably *true* — they are the checker
subsystem's operational telemetry, not application domain models, and keeping
subsystem tables out of the app's ORM is defensible separation rather than
evasion.

## What I find, since you asked

**The two groups are not the same case, and I would not treat them the same.**

- **`ship_registry` is domain data** — 295 ships, the same registry
  `registry_sync` compares the database against. That belongs in `models.py`.
  Option A.
- **The three `pipeline_*` tables are subsystem telemetry.** They are written
  only by `checks/findings_store.py` and `framework.py`, read by nothing in
  `app/`, and their schema moves with the checker layer rather than the
  application. Option B is honest for these *if* the exclusion is explicit and
  commented — naming them, saying schema-init owns them, and saying why.

Your read was that declaring is correct and excluding is a workaround. I agree
for `ship_registry`. For the `pipeline_*` tables I think it is closer to a
genuine ownership boundary than a dodge — but that is a judgement about where
the boundary *should* sit, which is yours.

**Either way the hazard must close before anything else touches alembic.** A
mixed answer still closes it: all four stop appearing in autogenerate output.

**One thing neither option gives you:** a control. Both rely on the drift being
absent. Neither stops someone applying a hand-written migration that drops a
table. If that matters, it is a separate ask.

## 21,849 — SOLVED, and it corrects both the order and the hypothesis

It is the **file count of `items/` in the scunpacked-data (source 1) snapshot.**

| snapshot | `items/` files |
|---|---:|
| `20260731T041451Z` (superseded) | **21,849** |
| `20260801T204744Z` (current) | **21,849** |

**Both are populated.** The order's "the snapshot's `items/` directory is empty"
is wrong, and the hypothesis that the number came from the superseded snapshot
*because* the current one is empty is wrong too — they are identical, which is
expected, since both snapshots are the same upstream commit `4764726`. The files
are per-item JSON (`3_seat_bench_constellation.json`,
`987_hat_01_01_01.json`, …).

So C2 conflated **source 1's game-file item count (21,849)** with **UEX's priced
item records (7,728)**. Two different things: everything in the game files
versus only what UEX has a price for.

**This is worth carrying into the backend decision even though it is already
ruled.** If "a page per item" ever means source 1's game items rather than UEX's
priced ones, the arithmetic is **21,849 + 823 + 316 = 22,988 — over the 20,000
cap.** The static ruling holds regardless, and for the stronger reason, but the
file-count argument flips depending on which "items" is meant. Recorded so the
next person to reach for it has both numbers.

## Corrections to my own stale context

`schema_drift` **was already fixed** at 20:23 and I should have read
`20260801_202307_update_schema_drift_stable_key.md` before listing it as open.
The archive entry is also sharper than my diagnosis: the real culprit was
**memory addresses** in `server_default` renders
(`<TextClause object at 0x0000017059E56C10>`, 4 distinct across 2 runs), not
merely unstable ordering — and that is why my hex normaliser missed them.

I have not touched `findings_store.py`, `source_checks.py` or
`pipeline_findings`. I read enough to answer this question and nothing more.

## Committed

`8f46e69` — `find.src.html` added to `build_deploy.py` PAGES, per the go-ahead.

### 2026-08-02 01:23:41 — update_build_spec_crafting_surfaces.md

# BUILD SPEC — the crafting surfaces (D2, D3, D4)

**From C2 to C1. 2026-08-02. Spec only — C2 wrote nothing to the repository.**

Companion to `claude/build-spec-descriptions-and-blueprint-index.md`, which
specifies Build 1 (item descriptions) and Build 2 (the blueprint index). **This
document assumes the blueprint index exists.** Everything here reads it and
nothing here parses `blueprints.json` or `contracts/` again.

Three surfaces:

    D2   Blueprint page     1,597 pages
    D3   Reverse lookup     "I have this. What can I make?"
    D4   Material pages     37 pages — SCOPE CUT, see §4

Every number below is measured output from a read-only run against the sealed
snapshots, not a prediction. **Four things I had previously planned turned out
to be wrong, and one of them removes half of D4.** They are in section 1.

---

## 1. WHAT VALIDATION CHANGED

### 1a. `commodity_trade_locations.json` does NOT tell you where to buy a material

`claude/plan-crafting-build-from-data-on-hand.md` §6 says this file gives
*"where it is sold"*. It does not.

Measured: Agricium, Titanium, Gold, Tungsten, Copper, Quantainium, Borase,
Aluminum, Laranite, Beryl, Taranite, Bexalite, Corundum, Hephaestanite and
Quartz **all have exactly 468 SoldAt locations, and the location sets are
byte-identical to each other.**

The reason is in the record itself — every entry carries
`MatchedTagName: "Commodity"` or `"Metal"`. **The file matches locations by
tag, not by stock.** It says "this place trades in commodity-tagged goods," not
"this place sells Agricium."

**Consequence: the "where to get it" half of D4 has no data behind it at all.**
Not stale data, not partial data — none. Combined with the absent commodity
prices, D4 shrinks to "what this material makes," which is still worth building
but is a smaller thing than planned. Section 4 reflects that.

### 1b. No ingredient has a refined version

Same plan section promised *"what it refines into"* from
`RefinedVersionUUID` / `RefinedVersionName`. Measured across the 26 ingredients
present in `resources/commodities.json`: **0 carry a RefinedVersionUUID.** The
field exists on the schema and is null for every material we care about.

### 1c. Six blueprints have no output at all

    BP_CRAFT_COOL_S04_CNOU_Pioneer                       source_kind = none
    BP_CRAFT_cds_combat_heavy_helmet_01_02_02            source_kind = direct_reward
    BP_CRAFT_cds_combat_superheavy_backpack_01_03_01     source_kind = contract
    BP_CRAFT_cds_combat_superheavy_helmet_01_03_01       source_kind = contract
    BP_CRAFT_cds_combat_superheavy_suit_01_03_01         source_kind = contract
    BP_CRAFT_cds_undersuit_01_02_02                      source_kind = direct_reward

`Output.UUID`, `Output.Name` and `Output.Type` are all null. **These pages
cannot show what they make, cannot link to an item, and cannot show a price.**
Three of them are reachable from real contracts, so they are not dead content —
the output just does not resolve in this extraction.

**Do not let these six 404 and do not let them render blank.** They should say
what they need and where they come from, and say plainly that the item they
produce is not identified in the game data.

### 1d. Output UUID is not unique — three pairs collide

    dabd2d8d  "FullForce"  PowerPlant    BP_CRAFT_POWR_LPLT_S02_FullForce  +  BP_CRAFT_POWR_SASU_S02_DayBreak
    dadc9318  "FoxFire"    QuantumDrive  BP_CRAFT_QDRV_ACAS_S01_FoxFire    +  BP_CRAFT_QDRV_JUST_S01_Goliath
    6fc982c0  "Glacis"     Shield        BP_CRAFT_SHLD_ORIG_S04_890J       +  BP_CRAFT_SHLD_RSI_S04_Polaris

1,597 blueprints resolve to **1,588 distinct outputs**. In each pair the two
blueprint keys name different products — DayBreak is not FullForce, Goliath is
not FoxFire, the 890J shield is not the Polaris shield — yet both point at the
same output UUID.

**Most likely a copy-paste error in CIG's data**, alongside the missing-`c`
reward key already recorded. **Not certain.** Treat item → blueprint as
many-to-many, show "2 blueprints make this" on the item page rather than picking
one, and do not silently deduplicate.

---

## 2. D2 — THE BLUEPRINT PAGE

1,597 pages. Reads the index only.

### 2.1 The problem that shapes the page

**Sources per blueprint, measured across the 676 contract-sourced ones:**

    min 1   median 6   p90 33   max 127

    1 source        135 blueprints
    2-5 sources     166
    6-20 sources    273
    21-50 sources    62
    51+ sources      40

**A page that renders one row per source produces a 127-row table to answer one
question.** Grouping is not a nicety here, it is the design.

Also measured: **22 distinct mission givers** overall, and **68 blueprints are
awarded by more than one giver** (max 9 different givers for a single
blueprint).

    Shubin Interstellar  2,760      Eckhart Security       291
    Headhunters          1,361      Bit Zeros              280
    Citizens for Prosperity 792     Recco Battaglia        269
    Foxwell Enforcement    761      InterSec Defense Sol.  207
    United Wayfarers Club  656      FTL Courier            156

    Mission types: Mercenary 3,179 · Ship Mining 2,658 · Refueling 656 ·
    Bounty Hunter 456 · Delivery 335 · Hauling 172 · Salvage 150 · Hand Mining 102

**Worth noticing:** Ship Mining is the second-largest source of blueprints.
Crafting is not a combat-only loop, and the page should not read as though it is.

### 2.2 Page structure

1. **Answer line.** *"Crafts an Omnisky III Cannon in 9 minutes. Most easily
   from Shubin Interstellar mining contracts."*

2. **What it makes.** Name, type, grade, link to the item page. If a shop price
   exists: *"Or buy it outright for 14,845 aUEC at Ship Weapons CRU-L5."*
   Measured: **721 of 1,597 blueprint rows carry a price.**
   **If `output_uuid` is null (6 pages) this whole block is replaced by a plain
   statement that the output is not identified in the data.**

3. **What it needs.** Ingredients grouped by component group. Group names are
   real and readable — Frame, Emitter, Aperture Iris, Insulative Liner, Armored
   Carapace, Shell, Barrel.
   - `resource` leaves show a quantity in SCU.
   - **`item` leaves show no quantity — `QuantityScu` is null on all 298 of
     them.** Render the name alone. Never print "null SCU".
   - Every leaf has `MinQuality`; show it where it is above the floor.
   - **No cost column. No total.** See §5.

4. **What quality does.** The `modifiers` table — stat, value at minimum
   quality, value at maximum. Measured: **1,537 of 1,597 carry at least one
   modifier; 60 carry none** (36 WeaponAttachment, 17 Char_Armor_Backpack,
   3 Misc, 3 Char_Armor_Legs, 1 Cargo). The section must disappear cleanly on
   those 60 rather than render an empty table.

5. **Where the blueprint comes from** — by `source_kind`:

   - **`contract` (676).** Lead with the *best* source: highest `Chance`, then
     lowest `MinReputation`. Then a grouped summary — *"Also awarded by 126
     other Mercenary and Ship Mining contracts from Shubin Interstellar and 3
     others."* Full list behind a disclosure, never inline.

     Each source shows: contract title, giver, mission type, lawful or unlawful
     (`Illegal` — measured 7,571 false, 776 true), drop chance
     (**measured 8,283 at 1, 53 at 0.25, 11 at 0.75**), and the reputation gate
     rendered from `ReputationPrerequisite`:

         "Needs Sr. Contractor standing with InterSec Defense Solutions."

     built from `MinStanding.Name` and `Faction`. The raw numbers
     (`MinReputation: 5800`) are available if wanted but the name is the answer.

     **There is no payout to show.** `CalculatedReward` is a boolean — measured
     8,260 true, 87 null, no numbers anywhere in the field.

   - **`event` (31).** *"Reward from the XenoThreat event"* — and for the 25
     XenoThreat entries the pool key carries the contribution tier
     (`_15_`, `_25_`, `_50_`, `_60_`, `_85_`, `_100_`), so say which.
     The 6 RedWind entries: *"Reward from RedWind Linehaul."*
     **Caveat on record: whether RedWind's contracts carry a `Blueprints` array
     was never checked.** If they do, those 6 are misclassified.

   - **`direct_reward` (16) and `default` (8).** Stated plainly.

   - **`other_pool` (1).** The Microsatellite probe. It exists so nothing falls
     through silently.

   - **`none` (865).** ***"We don't know how you get this blueprint."***
     Verified against all 5,108 contracts, so this is a finding, not a hedge.
     **54% of all blueprint pages say this.** It has to read as confident.
     Suggested wording, and the reason for it: *"Nothing in the game files says
     how this blueprint is obtained. It may come from an event, or it may not be
     available yet."* — states what we checked, offers the two live
     possibilities, claims nothing.

6. **Provenance line.** Patch stamp and source, same as every page.

---

## 3. D3 — REVERSE LOOKUP

The cheapest genuinely-new thing in the crafting area. **Needs no data beyond
the index.** None of the four competing tools inverts the question.

### 3.1 The inverted index — all 37 ingredients, measured

    856  resource  Aslarite            83  resource  Borase
    495  resource  Ouratite            82  resource  Torite
    341  resource  Laranite            75  resource  Silicon
    261  resource  Tungsten            73  resource  Corundum
    228  resource  Iron                71  item      Dolivine
    194  resource  Agricium            63  resource  Gold
    145  resource  Taranite            58  item      Hadanite
    137  resource  Stileron            51  resource  Tin
    122  resource  Hephaestanite       38  resource  Aluminum
    113  resource  Lindinium           37  item      Sadaryx
    101  resource  Titanium            34  item      Beradom
     96  resource  Copper              33  resource  Beryl
     92  resource  Pressurized Ice     32  item      Aphorite
     88  resource  Savrilium           28  resource  Quartz
     84  resource  Riccite             25  resource  Bexalite
                                       25  item      Glacosite
                                       16  item      Janalite
                                        9  item      Feynmaline
                                        8  item      Carinite
                                        7  item      Saldynium (Ore)
                                        3  resource  Quantainium
                                        1  item      Yormandi Eye

**37 total. A plain multi-select covers the entire space** — no search box, no
autocomplete, no infrastructure.

### 3.2 Behaviour

- Tick what you are carrying. 26 resources and 11 hand-mined gems, visually
  separated because they are acquired completely differently.
- Two result lists, and **the second is the more useful one**:
  - **"You have everything for these."**
  - **"You're one short."** — with the missing ingredient named. This is what
    turns the page from a lookup into a plan.
- Sort by the output's shop price, descending, so the most valuable thing the
  pile makes is at the top. **Only 721 of 1,597 have a price** — unpriced rows
  sort last, never interleaved with a blank.
- Quantities are deliberately ignored. The data gives `QuantityScu` per recipe
  but the player's hold size is unknown and 298 leaves have no quantity at all.
  **Match on presence, not amount, and say so on the page.**
- Every row links to its blueprint page.

### 3.3 Why it works

Aslarite is in **856 of 1,597 blueprints** — 54%. Ouratite 495, Laranite 341.
A player who just finished a mining run is holding common ore and has hundreds
of answers. The value is not the list, it is the ranking and the "one short"
column.

**State the scope limit plainly on the page:** this matches ingredients, not
whether you have the blueprint. A player can be shown something they cannot yet
craft. That is still useful — it tells them which blueprint to go get — but it
must not pretend otherwise.

---

## 4. D4 — MATERIAL PAGES (scope cut)

37 pages. **Reduced by §1a and §1b to essentially one good section.** Build it
anyway — it is the only surface in the project that speaks to miners, and it is
the bridge between the mining audience and the gear audience.

**What is real:**

- **What it makes.** The inverted index from §3.1, ranked by output shop price.
  For Aslarite that is 856 blueprints, so it needs the same grouping discipline
  as D2 — summarise by output type, disclose the full list.
- **Name and description.** Measured: **all 26 resource ingredients present in
  `resources/commodities.json` carry a real Name and Description** — no
  placeholders. `labels.json` holds 552 `items_commodities_*` keys as a
  secondary source. **My name-match against those labels was fuzzy and I do not
  trust the 37-of-37 hit rate it reported — verify per material before relying
  on it.**
- **Container sizes.** All 26 carry `CargoContainers[]` — 1 / 2 / 4 / 8 / 16 SCU.
- **The 11 hand-mined gems are not in `commodities.json` at all.** Those pages
  get the "what it makes" section and nothing else. Say why: they are hand-mined,
  not traded as cargo.

**What is NOT available and must not be faked:**

- Where to buy it — §1a. The tag-matched location list is not stock data.
- What it costs — no commodity price rows exist on disk.
- What it refines into — §1b, zero coverage.
- Where to mine it — not in any file examined.

**Leave those four slots in the template, empty and labelled.** Three of them
open up the moment commodity prices land; the mining-location one needs a source
that does not currently exist and should be recorded as an open data gap.

---

## 5. STILL FENCED OFF

**Anything requiring an ingredient cost.** Zero commodity price rows on disk,
verified twice. That fences off the craft-vs-buy verdict, any total-cost figure,
the materials shopping trip, and cost-per-improvement ranking.

Keep `ingredient_cost` in the schema, keep it null, and assert it stays null
(§6). **Do not ship an estimate.**

**Grind-route planning stays out of scope by decision.** CmdrQuattro's tool owns
it. Link out.

---

## 6. VERIFICATION — HARD RULE 12

Exact, not greater-than-zero. A check that cannot fail is not a check.

- **D2: assert the six null-output blueprints render a complete page.** Named in
  §1c. This is the empty-state test that matters most, because three of them are
  reachable from real contracts and will get traffic.
- **D2: assert a 127-source blueprint renders without a 127-row table.** Take
  the max-source blueprint from the index and assert the rendered source count
  is bounded.
- **D2: assert an `865`-group page renders complete with no source block.**
  54% of pages.
- **D2: assert the modifier section is absent, not empty, on all 60 rows that
  carry no modifiers.**
- **D2: assert no payout figure appears anywhere.** `CalculatedReward` is
  boolean; a number on screen means something invented it.
- **D3: assert the ingredient list is exactly 37**, and that ticking Aslarite
  alone returns 856 blueprints.
- **D3: assert the "one short" list is non-empty for a single-ingredient
  selection** — otherwise the logic has collapsed into the "have everything"
  case.
- **D4: assert no material page renders a buy location or a price.** This is the
  §1a guard. The tag-matched data is present and will look plausible if someone
  wires it up by mistake.
- **All: assert `ingredient_cost` is null on all 1,597 rows.**
- **All: assert no name-based join exists.** 35 of 37 ingredient names match UEX
  commodity names exactly. It will work. It is still forbidden — use the
  `resources/commodities.json` UUIDs, which cover 26 of 37 properly, and leave
  the other 11 unjoined rather than matching on a string.

---

## 7. WHAT I DID NOT VERIFY

- **Whether RedWind's contracts carry a `Blueprints` array.** Six blueprints are
  classed `event` on the pool key alone.
- **Whether the three colliding output UUIDs are a CIG error or intentional.**
- **Whether the six null outputs resolve in a newer extraction.** The snapshot is
  from 2026-08-01; the game is on 4.9.
- **`CategoryUUID` on blueprints** — never resolved to a name. It may give a
  better grouping for D2 than `output_type`.
- **The `items_commodities_*` label match** — fuzzy, see §4.
- **Whether mining locations exist in any file** — the `Kind: cave_harvestable`
  entries in `resources/resources.json` (557 records) were seen but not opened.
  **That is the most likely home for the missing mining-location data and is
  worth ten minutes before D4 is called complete.**

---

## 8. REFERENCE IMPLEMENTATION — the derived views

Read-only. Reads `blueprint_index.json` from Build 2 and writes two small
lookup files. Neither touches a snapshot.

```python
import json, os, collections

ROOT  = r"C:\Users\david\citizen-compass"
INDEX = os.path.join(ROOT, r"data-layer\processed\blueprint_index.json")
OUT   = os.path.join(ROOT, r"data-layer\processed")

with open(INDEX, encoding="utf-8") as fh:
    rows = json.load(fh)

# ---- D3: ingredient -> blueprints -----------------------------------------
inverted = collections.defaultdict(list)
kinds    = {}
for r in rows:
    for name in {i["name"] for i in r["ingredients"]}:
        inverted[name].append(r["blueprint_uuid"])
    for i in r["ingredients"]:
        kinds[i["name"]] = i["kind"]

ingredients = [
    {
        "name": name,
        "kind": kinds[name],                    # resource | item (hand-mined)
        "blueprint_count": len(uuids),
        "blueprints": sorted(uuids),
    }
    for name, uuids in sorted(inverted.items(), key=lambda kv: -len(kv[1]))
]

with open(os.path.join(OUT, "ingredient_index.json"), "w", encoding="utf-8") as fh:
    json.dump(ingredients, fh, ensure_ascii=False, indent=1)

# ---- D2: source summary per blueprint -------------------------------------
def summarise(r):
    """Collapse up to 127 contract sources into one displayable block."""
    srcs = r["sources"]
    if r["source_kind"] != "contract" or not srcs:
        return None

    def rep_floor(s):
        rep = s.get("reputation") or {}
        return ((rep.get("MinStanding") or {}).get("MinReputation") or 0)

    best = sorted(srcs, key=lambda s: (-(s.get("chance") or 0), rep_floor(s)))[0]
    givers = collections.Counter(s.get("giver") for s in srcs)
    types  = collections.Counter(s.get("mission_type") for s in srcs)
    rep    = (best.get("reputation") or {})
    standing = (rep.get("MinStanding") or {}).get("Name")

    return {
        "total": len(srcs),
        "best": {
            "title":        best.get("title"),
            "giver":        best.get("giver"),
            "mission_type": best.get("mission_type"),
            "chance":       best.get("chance"),
            "illegal":      best.get("illegal"),
            "standing":     standing,
            "faction":      rep.get("Faction"),
        },
        "givers":        givers.most_common(),
        "mission_types": types.most_common(),
        "others":        len(srcs) - 1,
    }

summary = {r["blueprint_uuid"]: summarise(r) for r in rows}
with open(os.path.join(OUT, "blueprint_sources.json"), "w", encoding="utf-8") as fh:
    json.dump(summary, fh, ensure_ascii=False, indent=1)

# ---- hard rule 12 ----------------------------------------------------------
NULL_OUTPUT = 6
assert len(ingredients) == 37, f"ingredients {len(ingredients)}"
assert ingredients[0]["name"] == "Aslarite" and ingredients[0]["blueprint_count"] == 856
assert sum(1 for i in ingredients if i["kind"] == "item") == 11, "hand-mined count moved"
assert sum(1 for r in rows if not r["output_uuid"]) == NULL_OUTPUT, "null-output count moved"

outputs = collections.Counter(r["output_uuid"] for r in rows if r["output_uuid"])
assert len(outputs) == 1588, f"distinct outputs {len(outputs)}"
assert sum(1 for v in outputs.values() if v > 1) == 3, "output collisions moved"

contract_rows = [r for r in rows if r["source_kind"] == "contract"]
assert max(len(r["sources"]) for r in contract_rows) == 127, "max sources moved"
assert all(r["ingredient_cost"] is None for r in rows), "something invented a cost"

print("ingredients:", len(ingredients))
print("null-output blueprints:", NULL_OUTPUT, "| output collisions: 3")
print("max sources on one blueprint:", max(len(r["sources"]) for r in contract_rows))
print("OK ->", OUT)
```

**On the assertions.** They are exact on purpose and they will break when the
game patches. **That is the signal, not the bug.** Update the numbers
deliberately, with a note recording which patch moved them.

### 2026-08-02 01:11:49 — update_build_spec_descriptions_and_blueprint_index.md

# BUILD SPEC — two builds, both validated against the real data

**From C2 to C1. 2026-08-02. Spec only — C2 wrote nothing to the repository.**

Two builds. Both run entirely on data already collected, gated and sealed.
Neither is blocked on the commodity price pull.

**Everything in this document was executed read-only against the real snapshots
before being written down.** Every count is measured output, not a prediction.
Where a number is asserted in section 5, a run produced it.

    BUILD 1   Item descriptions        5,344 item pages gain CIG's own prose
    BUILD 2   The blueprint index      1,597 rows, the table every crafting
                                       surface reads

**Why these two.** Build 1 is the largest visible improvement available anywhere
in the project right now and it depends on nothing. Build 2 is the foundation —
no crafting page can be built before it, and it carries zero design risk because
it is pure derivation. One visible, one structural, neither blocked.

---

## 0. READ STATE

    scunpacked-data/snapshots/20260801T204744Z/
        blueprints.json      1,597 records
        contracts/           5,108 files
        fps-items.json       5,420 records
        ship-items.json      5,384 records
        labels.json          90,121 labels

    uexcorp/snapshots/20260801T235530Z/
        items_category_*.json  7,728 records, 100 files   sha of categories.json 3de4f9fa2bf7674d
        items_prices_all.json  23,734 rows                sha 308542bf043df9c2

Both snapshots are sealed. If these hashes have moved, stop — something has
modified a sealed snapshot.

---

# BUILD 1 — ITEM DESCRIPTIONS

## 1.1 What this corrects

`claude/front-end-build-plan-2026-08-02.md` §3 states:

> **No "what it's good for" or "how to use it".** That is writing, not data.

That is wrong, and it was wrong when I wrote it. The descriptions were already on
disk in a file the project had gated a day earlier.

## 1.2 The measured coverage

    fps-items.json   records with a description      5,182 of 5,420
    ship-items.json  records with a description      2,598 of 5,384
    combined uuid -> description map                 7,780 entries

    UEX catalogue                                    7,728 items
    UEX items carrying a uuid                        5,566
    UEX items that gain a description                5,344

    = 69% of the whole catalogue
    = 96% of every item that carries a uuid

**Put that next to the other two coverage figures for the same pages:**

    description   69%
    price         36%
    image          0%

Description is the best-covered field on the item page. The doorway plan was
built around templates that must survive having almost nothing in them; this is
the single largest thing available to stop 7,728 pages reading like a database
dump.

## 1.3 The join

**UUID only. No name matching.** The UEX manifest forbids a name-matching path
and it is not needed here.

    UEX  items_category_*.json  ->  .uuid
    scunpacked  fps-items.json  ->  .stdItem.UUID   (fall back to .reference)
    scunpacked  ship-items.json ->  .stdItem.UUID   (fall back to .reference)

Both scunpacked files share the same record shape: a top-level object with
`className`, `reference`, `name`, `type`, `subType`, `size`, `grade`, `tags`,
`classification`, and a nested `stdItem` carrying `UUID`, `ClassName`, `Size`,
`Grade`, `Mass`, dimensions, `Type`, `Name`, `Description`, `DescriptionText`,
`Manufacturer`.

**Field priority, in order:**

1. `stdItem.DescriptionText`
2. `stdItem.Description`
3. `labels.json` key `item_Desc_<ClassName>`

The third path exists but keys on **class name, not UUID** — 5,805 `item_Desc_*`
keys, 5,558 with more than 20 characters of content. Use it only where the UUID
path returns nothing. `labels.json` also holds 4,749 `item_Name_*` keys if a
display name is ever needed.

**Do not merge the two ship-items and fps-items maps blindly** — build fps first,
then let ship-items overwrite, or vice versa, but pick one and record which. The
combined map is 7,780 entries against 5,420 + 5,384 inputs, so there is overlap.

## 1.4 What the descriptions actually contain

Two distinct kinds, and the page should handle both:

**Prose.** *"CDS's quest to create the ideal light armor continues with the
FBL-8a. This light armor will keep you fast on your feet with its strategic mix
of protective plating and reinforced nano-weave fabrics…"*

**Stat blocks**, newline-delimited key/value:

    Item Type: Heavy Armor
    Damage Reduction: 40%
    Temp. Rating: -80 / 105 °C
    Radiation ...

**Detect and render these differently.** A stat block rendered as a paragraph
reads as broken. Suggested test: if more than half the non-empty lines match
`^[A-Za-z][A-Za-z .'-]{2,30}:\s`, render as a definition list; otherwise render
as prose. **This heuristic is mine and is untested — validate it against a
sample before trusting it.**

Descriptions contain literal `\n`. Preserve line breaks.

## 1.5 Where it goes on the page

Slot 3 of the item page defined in `front-end-build-plan-2026-08-02.md` §A2 —
under the header, above the answer line. The answer line ("Sold at 4 shops,
cheapest is…") stays the most important element; the description is context, not
the answer.

**Where a stat block exists, it also belongs beside the price**, because it is
the thing that tells someone whether the cheaper item is the worse item.

## 1.6 Verification — hard rule 12

- **Assert the join returns exactly 5,344.** Fewer means the fallback chain is
  broken; more means something matched by name.
- **Assert the 2,384 items with no description still render a complete page.**
  That is 31% of the catalogue. This is the empty-state test the doorway plan
  already requires, now with a real number attached.
- **Assert no name-based match occurs.** Log any item that gained a description
  without a UUID match — the count must be zero unless the `labels.json`
  fallback is deliberately enabled, in which case count it separately.
- **Assert a stat-block description renders as a list and a prose description
  renders as a paragraph**, using one known example of each.

---

# BUILD 2 — THE BLUEPRINT INDEX

One derived table. 1,597 rows. Everything crafting reads it and nothing else
parses `blueprints.json` or `contracts/` again.

## 2.1 Row shape

| field | source |
|---|---|
| `blueprint_uuid` | `blueprints.json[].UUID` |
| `blueprint_key` | `.Key` |
| `output_uuid` `output_name` `output_type` `output_subtype` `output_grade` | `.Output.*` |
| `craft_time_seconds` | `.Tiers[0].CraftTimeSeconds` |
| `ingredients[]` | flattened `.Tiers[0].Requirements` |
| `component_groups[]` | `.Tiers[0].Requirements.Children[]` — `Key`, `Name`, `RequiredCount` |
| `modifiers[]` | each group's `Modifiers[]` |
| `source_kind` | derived, see 2.3 |
| `sources[]` | contract records, or pool keys |
| `shop_price_min` `shop_price_terminal` | UEX join on `output_uuid` |
| `last_verified_patch` | snapshot patch stamp |

Every blueprint has exactly **one** tier. Do not build for many.

## 2.2 Ingredient flattening — and the trap in it

Walk `Requirements` depth-first. `Kind == "group"` sets the current group name.
`Kind == "resource"` and `Kind == "item"` are leaves. Keep `UUID`, `Name`,
`QuantityScu`, `MinQuality`, and the enclosing group name.

**Measured across all 1,597 blueprints — 4,274 leaves:**

    Kind == "resource"    3,976    all 3,976 carry QuantityScu
    Kind == "item"          298    NONE carry QuantityScu
    all 4,274 carry MinQuality

**`QuantityScu` is null on every `item` leaf.** Those 298 are the hand-mined
gems — Dolivine, Hadanite, Sadaryx, Beradom, Aphorite, Glacosite, Janalite,
Feynmaline, Carinite, Saldynium (Ore), Yormandi Eye. A template that assumes a
quantity will print "null SCU of Hadanite" on roughly one recipe in five.
**Render those as a name with no quantity.**

37 distinct ingredients total. 1–4 leaves per blueprint, average 2.7.

## 2.3 `source_kind` — derivation and measured distribution

Evaluate in this order, first match wins:

    Availability.Default == true                              -> default
    blueprint_uuid appears in any contract's Blueprints[]     -> contract
    any pool Key contains "Xenothreat" or "RedWind"           -> event
    any pool Key is BP_REWARD_<x> where BP_CRAFT_<x> exists   -> direct_reward
    RewardPools present but none of the above                 -> other_pool
    no Default, no RewardPools                                -> none

**Measured result — this is the assertion:**

    none            865
    contract        676
    event            31
    direct_reward    16
    default           8
    other_pool        1
    -------------------
    total         1,597

The single `other_pool` row is `BP_CRAFT_Carryable_2H_FL_MissionItem_Microsatellite_a`
("Probe"), pointing at `BP_MISSIONREWARD_Carryable_2H_FL_MissionItem_Microsatellite_a`.
**It exists so nothing falls through silently.** If that bucket ever grows past 1,
a new reward mechanism has appeared and someone should look.

## 2.4 Contract extraction — what each contract gives, and one correction

For each of the 5,108 files, read `Blueprints[]`. Each entry:
`Chance`, `PoolUUID`, `PoolContents[]` of `{ItemName, ItemUUID, BlueprintUUID}`.

Alongside, capture from the contract: `UUID`, `DisplayTitle` (fall back to
`Title`), `MissionGiver`, `MissionType.Name`, `Faction`, `TimeToComplete`,
`Difficulty`, `Illegal`, `ReputationPrerequisite`,
`LocationPools[].ResolvedLocations[].Name`.

**Correction to `claude/plan-crafting-build-from-data-on-hand.md` §3.** That plan
lists `CalculatedReward` as the payout. **It is a boolean, not an amount** —
measured 8,260 `true`, 87 `null`, no numbers. It means the reward is computed at
runtime. **There is no payout figure in this data.** Do not display one.

**What is genuinely there and is better than expected — `ReputationPrerequisite`
is a full object:**

    { "Faction": "InterSec Defense Solutions",
      "Scope": "FactionReputation",
      "MinStanding": { "Name": "Sr. Contractor",   "MinReputation": 5800 },
      "MaxStanding": { "Name": "Elite Contractor", "MinReputation": 95250 } }

That gives the reputation gate in human words — *"needs Sr. Contractor standing
with InterSec Defense Solutions"* — which is exactly the question a player has.

**`Illegal`** — measured 7,571 false, 776 true. Lawful/unlawful badge, free.

**`Chance`** — measured 8,283 at 1, 53 at 0.25, 11 at 0.75. Real and varied.
Show it. Nobody else does.

## 2.5 The thing that will break the page if it is not handled

**Sources per blueprint: minimum 1, maximum 127.**

One blueprint is awarded by 127 different contracts. A blueprint page that
renders a row per source will produce a 127-row table for a single answer.

**Group by `MissionGiver` and `MissionType` and summarise**: *"Awarded by 127
Mercenary contracts from Headhunters and 4 others."* Offer the full list behind
a disclosure. Show the **best** source first — highest `Chance`, then lowest
reputation requirement.

## 2.6 Price join

`output_uuid` = `items_prices_all.json[].item_uuid`, taking rows where
`price_buy > 0`, keeping the minimum and its `terminal_name`.

**Measured: 721 of 1,597 blueprint rows gain a price.** (The earlier figure of
719 counted distinct *items*; 1,597 blueprints resolve to 1,588 distinct outputs,
so the row count differs slightly. Both are correct for what they count.)

**No ingredient cost. No total. No craft-vs-buy verdict.** There are zero
commodity price rows on disk. Leave the slot in the schema, leave it null, and
do not let anything populate it before the commodity pull lands.

## 2.7 Modifiers

Each component group carries `Modifiers[]` with `Key`, `Name`, `QualityRange`
(min/max, observed 0–1000), `ModifierRange` (`AtMinQuality`/`AtMaxQuality`),
`ValueRangeType` (observed `linear`), `UnitFormat`.

**Measured: 1,537 of 1,597 blueprints carry at least one modifier.**
The 60 without are mostly `WeaponAttachment` (36) and `Char_Armor_Backpack` (17).
The template must not assume a quality curve exists.

## 2.8 Performance — two runs timed out getting this wrong

Scanning 5,108 contract files naively exceeds 45 seconds.

- One pass over the directory.
- **Substring-test the raw text for `"PoolUUID"` before calling `json.loads`.**
  Only ~15% of contracts award blueprints; parsing the other 85% is wasted.
- **Do not loop 146 pool keys against every file.** That is 745,000 substring
  searches and it is what timed out. Invert it: extract from the file, then look
  up.

On a machine without a 45-second cap this is a non-issue, but the wasted work is
real either way.

## 2.9 Verification — hard rule 12

- **Assert 1,597 rows out.** Same as in.
- **Assert `source_kind` partitions to 865 / 676 / 31 / 16 / 8 / 1.** These are
  measured. Any drift means the data or the derivation changed, and both are
  worth knowing about.
- **Assert 676 blueprints have at least one contract source**, and that the
  scan found **768** contracts carrying a `Blueprints` array. A run finding fewer
  has silently skipped files.
- **Assert all 4,274 ingredient leaves carry `MinQuality`, and that exactly the
  298 `item`-kind leaves lack `QuantityScu`.** If a `resource` leaf ever lacks a
  quantity, the flattening is wrong.
- **Assert 721 rows carry a price and 0 rows carry an ingredient cost.** The
  second is the important one — a cost appearing means something invented it.
- **Assert an `865`-group page renders complete with no source.** That is 54% of
  all blueprint pages.
- **Assert no name-based join exists.** 35 of the 37 ingredient names happen to
  match UEX commodity names exactly. It will work. **It is still forbidden** —
  use the UUIDs in `resources/commodities.json`, which cover 26 of 37 properly,
  and leave the other 11 unjoined rather than matching on a string.

---

## 3. WHAT I DID NOT VERIFY

- **The stat-block detection heuristic in 1.4 is mine and untested.**
- **Whether RedWind's contracts carry a `Blueprints` array.** Its 6 blueprints
  are classed `event` on the strength of the pool key alone.
- **`CategoryUUID` on blueprints** — never resolved to a name.
- **Description coverage per doorway.** I have the total (69%) but not the split,
  so I cannot say whether Ship parts is better or worse covered than Clothing.
- **Whether `labels.json item_Desc_*` adds anything beyond the UUID path.** It may
  be entirely redundant. Worth measuring before wiring the third fallback.

---

## 4. REFERENCE IMPLEMENTATION

Read-only. Writes one JSON file each. Neither touches a snapshot.
Both were executed against the real data to produce the counts asserted above.

Paths assume `C:\Users\david\citizen-compass`. Adjust `ROOT` if that changes.

### 4.1 Build 1 — the description map

```python
import json, glob, os

ROOT = r"C:\Users\david\citizen-compass"
SC   = os.path.join(ROOT, r"data-layer\external-sources\scunpacked-data\snapshots\20260801T204744Z")
UEX  = os.path.join(ROOT, r"data-layer\external-sources\uexcorp\snapshots\20260801T235530Z")
OUT  = os.path.join(ROOT, r"data-layer\processed\item_descriptions.json")

def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)

desc, src = {}, {}
for fname in ("fps-items.json", "ship-items.json"):
    for rec in load(os.path.join(SC, fname)):
        std = rec.get("stdItem") or {}
        uuid = std.get("UUID") or rec.get("reference")
        if not uuid:
            continue
        text = (std.get("DescriptionText") or std.get("Description") or "").strip()
        if text:
            desc[uuid] = text
            src[uuid] = fname

uex = []
for path in glob.glob(os.path.join(UEX, "items_category_*.json")):
    uex += (load(path).get("data") or [])

out, hit = {}, 0
for item in uex:
    uuid = item.get("uuid")
    if uuid and uuid in desc:
        hit += 1
        out[str(item["id"])] = {
            "uuid": uuid,
            "name": item.get("name"),
            "description": desc[uuid],
            "source_file": src[uuid],
        }

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print("uex items:", len(uex), "with uuid:", sum(1 for i in uex if i.get("uuid")))
print("descriptions matched:", hit)
assert hit == 5344, f"expected 5344, got {hit}"
print("OK ->", OUT)
```

### 4.2 Build 2 — the blueprint index

```python
import json, glob, os, collections

ROOT = r"C:\Users\david\citizen-compass"
SC   = os.path.join(ROOT, r"data-layer\external-sources\scunpacked-data\snapshots\20260801T204744Z")
UEX  = os.path.join(ROOT, r"data-layer\external-sources\uexcorp\snapshots\20260801T235530Z")
OUT  = os.path.join(ROOT, r"data-layer\processed\blueprint_index.json")
PATCH = "4.9"   # snapshot patch stamp - set from the manifest, do not hard-code blindly

def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)

# ---- contracts: only parse files that can possibly matter -------------------
sources, contracts_with_bp = {}, 0
for path in glob.glob(os.path.join(SC, "contracts", "*.json")):
    with open(path, encoding="utf-8", errors="ignore") as fh:
        raw = fh.read()
    if '"PoolUUID"' not in raw:
        continue
    c = json.loads(raw)
    pools = c.get("Blueprints") or []
    if not pools:
        continue
    contracts_with_bp += 1
    meta = {
        "contract_uuid": c.get("UUID"),
        "title":         c.get("DisplayTitle") or c.get("Title"),
        "giver":         c.get("MissionGiver"),
        "mission_type":  (c.get("MissionType") or {}).get("Name"),
        "faction":       c.get("Faction"),
        "illegal":       c.get("Illegal"),
        "time_to_complete": c.get("TimeToComplete"),
        "difficulty":    c.get("Difficulty"),
        "reputation":    c.get("ReputationPrerequisite"),
    }
    for pool in pools:
        for entry in (pool.get("PoolContents") or []):
            bp_uuid = entry.get("BlueprintUUID")
            if bp_uuid:
                sources.setdefault(bp_uuid, []).append(
                    dict(meta, chance=pool.get("Chance"), pool_uuid=pool.get("PoolUUID")))

# ---- prices ----------------------------------------------------------------
cheapest = {}
for row in load(os.path.join(UEX, "items_prices_all.json"))["data"]:
    uuid, buy = row.get("item_uuid"), (row.get("price_buy") or 0)
    if uuid and buy > 0 and (uuid not in cheapest or buy < cheapest[uuid][0]):
        cheapest[uuid] = (buy, row.get("terminal_name"))

# ---- blueprints ------------------------------------------------------------
blueprints = load(os.path.join(SC, "blueprints.json"))
keys = {b.get("Key") for b in blueprints}

def flatten(node, acc, group=None):
    kind = node.get("Kind")
    if kind == "group":
        group = node.get("Name")
    if kind in ("resource", "item"):
        acc.append({
            "kind": kind,
            "uuid": node.get("UUID"),
            "name": node.get("Name"),
            "quantity_scu": node.get("QuantityScu"),   # null on every 'item'
            "min_quality": node.get("MinQuality"),
            "group": group,
        })
    for child in (node.get("Children") or []):
        flatten(child, acc, group)

rows, kinds = [], collections.Counter()
for b in blueprints:
    tier  = (b.get("Tiers") or [{}])[0]
    req   = tier.get("Requirements") or {}
    avail = b.get("Availability") or {}
    pools = avail.get("RewardPools") or []
    pool_keys = [p.get("Key") or "" for p in pools]

    ingredients = []
    flatten(req, ingredients)

    groups, modifiers = [], []
    for g in (req.get("Children") or []):
        groups.append({"key": g.get("Key"), "name": g.get("Name"),
                       "required_count": g.get("RequiredCount")})
        for m in (g.get("Modifiers") or []):
            modifiers.append({
                "group": g.get("Name"), "key": m.get("Key"), "name": m.get("Name"),
                "quality_range": m.get("QualityRange"),
                "modifier_range": m.get("ModifierRange"),
                "value_range_type": m.get("ValueRangeType"),
                "unit_format": m.get("UnitFormat"),
            })

    uuid = b["UUID"]
    if avail.get("Default"):
        kind = "default"
    elif uuid in sources:
        kind = "contract"
    elif any("Xenothreat" in k or "RedWind" in k for k in pool_keys):
        kind = "event"
    elif any(k.startswith("BP_REWARD_") and "BP_CRAFT_" + k[len("BP_REWARD_"):] in keys
             for k in pool_keys):
        kind = "direct_reward"
    elif pools:
        kind = "other_pool"
    else:
        kind = "none"
    kinds[kind] += 1

    out = b.get("Output") or {}
    price = cheapest.get(out.get("UUID"))
    rows.append({
        "blueprint_uuid": uuid,
        "blueprint_key": b.get("Key"),
        "output_uuid": out.get("UUID"),
        "output_name": out.get("Name"),
        "output_type": out.get("Type"),
        "output_subtype": out.get("Subtype"),
        "output_grade": out.get("Grade"),
        "craft_time_seconds": tier.get("CraftTimeSeconds"),
        "ingredients": ingredients,
        "component_groups": groups,
        "modifiers": modifiers,
        "source_kind": kind,
        "sources": sources.get(uuid, []) if kind == "contract" else pool_keys,
        "shop_price_min": price[0] if price else None,
        "shop_price_terminal": price[1] if price else None,
        "ingredient_cost": None,          # stays null until commodity prices land
        "last_verified_patch": PATCH,
    })

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(rows, fh, ensure_ascii=False, indent=1)

# ---- hard rule 12: assert, do not report ----------------------------------
leaves = [i for r in rows for i in r["ingredients"]]
expected = {"none": 865, "contract": 676, "event": 31,
            "direct_reward": 16, "default": 8, "other_pool": 1}

assert len(rows) == 1597,                     f"rows {len(rows)}"
assert dict(kinds) == expected,               f"source_kind {dict(kinds)}"
assert contracts_with_bp == 768,              f"contracts {contracts_with_bp}"
assert len(sources) == 676,                   f"sourced blueprints {len(sources)}"
assert len(leaves) == 4274,                   f"leaves {len(leaves)}"
assert all(i["min_quality"] is not None for i in leaves), "a leaf lacks MinQuality"
assert sum(1 for i in leaves if i["quantity_scu"] is None) == 298, "quantity nulls moved"
assert all(i["kind"] == "item" for i in leaves if i["quantity_scu"] is None), \
       "a 'resource' leaf lacks a quantity - flattening is wrong"
assert sum(1 for r in rows if r["shop_price_min"]) == 721, "price join moved"
assert all(r["ingredient_cost"] is None for r in rows),  "something invented a cost"
assert sum(1 for r in rows if r["modifiers"]) == 1537,   "modifier count moved"

print("rows:", len(rows))
print("source_kind:", dict(kinds))
print("priced:", sum(1 for r in rows if r["shop_price_min"]))
print("max sources on one blueprint:",
      max((len(r["sources"]) for r in rows if r["source_kind"] == "contract"), default=0))
print("OK ->", OUT)
```

**On the assertions.** They are deliberately exact rather than
greater-than-zero, because a check that cannot fail is not a check. They will
break when the game patches — **that is the point.** A failing assertion after a
patch is the signal that the data moved and someone should look, not a bug in
the script. Update the numbers deliberately, with a note saying which patch
changed them.

### 2026-08-02 00:58:19 — update_crafting_build_plan_and_dangling_pools.md

# Crafting build plan filed + 48 dangling pools resolved + item descriptions found
2026-08-02, C2. Read-only. **C2 wrote nothing to the repository.**

Plan: `claude/plan-crafting-build-from-data-on-hand.md` on claude.ai.
Everything in it runs on data already collected, gated and sealed. No new
acquisition needed.

## BIGGEST ITEM — item descriptions exist, 69% coverage

`claude/front-end-build-plan-2026-08-02.md` §3 says *"No 'what it's good for' or
'how to use it'. That is writing, not data."* **Wrong.**

`fps-items.json` and `ship-items.json` carry `stdItem.Description` and
`stdItem.DescriptionText`:

    fps-items with a description       5,182 of 5,420
    ship-items with a description      2,598 of 5,384
    combined uuid -> description       7,780
    UEX items that gain one            5,344 = 69% of catalogue, 96% of uuid-carrying

`labels.json` separately holds 5,805 `item_Desc_*` keys (5,558 with content) and
4,749 `item_Name_*`, some with stat blocks ("Damage Reduction: 40%, Temp. Rating
-80/105 °C").

**Description coverage (69%) beats price coverage (36%) and images (0%).** This
is the cheapest large improvement available in the project right now and it
benefits 5,344 item pages. Priority order: `stdItem.DescriptionText` →
`Description` → `labels.json item_Desc_*` (label path keys on class name, not
UUID — prefer UUID).

## The 48 dangling pools — resolved, and not broken

    25  XenoThreat event rewards  (BP_REWARDS_Xenothreat2_15_01 ... _100_03)
        XenoThreat is a real faction, 357 labels. Numbers are contribution
        tiers. Event rewards, not contracts — hence no contract awards them.
    16  1:1 mirror keys — BP_REWARD_<x> mirrors BP_CRAFT_<x> exactly.
        All "SecondWind" / "Purgatory Camo" cosmetic variants.
     6  RedWind — RedWind Linehaul delivery contractor, 118 labels.
        NOT CHECKED whether its contracts carry a Blueprints array.
     1  Microsatellite probe mission item.

**"Dangling" was the wrong word — these are obtainable by non-contract routes.**
Site wording should be "event reward" / "special reward", never "unobtainable".

**The 865 no-pool-no-default group remains genuinely sourceless** — zero
reachable across all 5,108 contracts.

## Defect in CIG's own data — worth a bug report

Three reward keys reference blueprints that do not exist under the mirrored name:

    BP_REWARD_ds_combat_medium_helmet_01_02_01   <- missing a 'c'
        actual blueprint: BP_CRAFT_cds_combat_medium_helmet_01_02_01
    BP_REWARD_CollectorMaterial_001
    BP_REWARD_CollectorMaterial_002

Arms, core and legs of that ORC-mkX SecondWind set all use the correct `cds_`
prefix; only the helmet is misspelled. If rewards resolve by this key, that
helmet cannot drop while the rest of its set can. **Not certain enough to
publish. Certain enough to report.**

## Build order in the plan

1. **D1 blueprint index** — one derived table, 1,597 rows, everything reads it.
2. **Wire item descriptions into the item template** — 5,344 pages, independent
   of crafting.
3. **D2 blueprint pages** — 1,597 pages, source/ingredients/quality curve.
4. **D3 reverse lookup** — "I have this, what can I make?" 37 materials, no new
   data, and none of the four competing tools inverts the question.
5. **D4 material pages** — 37 pages, better after prices land.

## Fenced off until commodity prices land

Zero commodity price rows exist on disk (verified twice). No craft-vs-buy
verdict, no total cost, no shopping trip, no cost-per-improvement. **Build the
templates with the slot present and empty** so it stays a data change, not a
redesign. Do not ship an estimate.

Also out of scope by decision: grind-route planning — CmdrQuattro's tool owns it.

## Performance warning for whoever implements D1

Scanning 5,108 contract files naively exceeds 45s. One pass; substring-test for
`"PoolUUID"` before parsing JSON; do not loop the 146 pool keys against every
file. That approach timed out twice here.

## Parked, not actioned

Contacting CmdrQuattro and the other three maintainers about a mutual link or
data exchange. Revisit only after commodity prices land — until then we have
nothing to offer. Terms of use to be read by a person first.

### 2026-08-02 00:45:17 — update_contract_blueprint_join_proven.md

# FINDING — "where do I get this blueprint" is answerable from our own data

**From C2. 2026-08-02. Read-only. Nothing written to the repository.**

Tested in response to the question of whether to pull data from a community
crafting tool. **We do not need to.** The join works.

---

## THE TEST

`contracts/*.json` — 5,108 files in
`scunpacked-data/snapshots/20260801T204744Z/` — carry a `Blueprints` array that
nobody in this project had opened.

Structure, verbatim from `004f6931-271f-4774-8db1-ce7b86de6837.json`:

    "Blueprints": [
      {
        "Chance": 1,
        "PoolUUID": "9cf3799c-2347-46a6-bd65-203f8a426f79",
        "PoolContents": [
          { "ItemName": "Devastator \"Vastator\" Shotgun",
            "ItemUUID": "e5b42569-10da-40a5-a16f-497f5b84cf3c",
            "BlueprintUUID": "f2947ab8-56b3-43e6-9ef6-6301070a1846" },
          ...
        ]
      }
    ]

**This is a direct structured join, contract → blueprint, with a drop chance.**

## RESULTS — full scan of all 5,108 contract files

    contracts that award blueprints                     768
    distinct blueprints reachable via contracts         676
    blueprints carrying a RewardPools field             724
      ...of those, reachable from a real contract       676
      ...dangling (pool exists, no contract found)       48
    the "no default, no pool" group                     865
      ...reachable via contracts anyway                   0

`Chance` is 1 on almost every pool; a small number are 0.25.

**The 865 are confirmed sourceless.** Not an oversight in my earlier read — no
contract in the game files awards them. Saying "we don't know how you get this"
is now a verified statement rather than a hedge.

## WHAT EACH CONTRACT ALSO CARRIES

From the same files, no extra work: `DisplayTitle`, `MissionGiver`,
`MissionType`, `Faction`, `CalculatedReward`, `TimeToComplete`,
`ReputationGained`, `ReputationPrerequisite`, `Illegal`, `Shareable`,
`OnceOnly`, `Cooldown`, `Difficulty`, `AvailabilityLocations`,
`RequiredLocations`, `LocationPools` with resolved location names, and the full
mission text.

Mission givers seen in the scan: Headhunters, Shubin Interstellar, United
Wayfarers Club, Citizens for Prosperity, Foxwell Enforcement, Adagio Holdings,
Eckhart Security, Bit Zeros.

**That is the same dataset the community blueprint finder presents**, derived
independently from the game files we already hold, gated and sealed.

---

## WHY THIS SETTLES THE "PULL FROM A TOOL" QUESTION

**1. The thing we would take, we already have.** Recipes, quantities, quality
curves, and now sources. All four competing tools are built on the same
extracted game files.

**2. The thing we lack, they lack too.** Our blocker is commodity prices. Not one
of the four shows a price. Scraping them moves us zero distance on the only axis
where we are actually stuck.

**3. The only thing genuinely worth taking is the only thing it would be wrong to
take** — CmdrQuattro's grind-route planning. That is his original work: ordering
contracts, respecting reputation gates, inserting rep contracts to unlock tiers.
It is not in any game file. It is the reason his tool exists.

**4. Credit is not a licence.** Attribution answers a courtesy question, not a
permission question. It matters more here than usual for three reasons:

- The Historian is the **monetised** part of the plan. Using another fan's
  research inside a subscription product is a materially different act from
  citing it on a free reference page.
- CIG's 2026-07-28 confirmation reviewed a ship price table. It is a snapshot,
  not a licence, and it does not cover redistributing another fan site's data.
- **This project has already refused two sources on exactly these grounds.**
  Source 4 is self-blocked `blocked_missing_provenance`; source 5 is
  `not_directly_downloadable`. Both were correct calls. Taking a fifth source
  with weaker provenance than either would contradict a decision already on
  record.

**5. Provenance would break the pipeline's own rules.** Scraped tool output has
no manifest, no hash, no patch stamp, and no upstream we can re-verify against.
Every row on this site carries `last_verified_patch`. A scraped row could not.

---

## WHAT TO DO INSTEAD — in order

1. **Build the contract → blueprint index from the files we already have.**
   Proven above. Gives source, faction, payout, reputation gate, drop chance and
   location, with full provenance.
2. **Pull UEX commodity prices.** Still the one real blocker, still the one thing
   no competitor has. Legitimate route, token already active.
3. **Link out to CmdrQuattro for grind routing**, and say why. A reference site
   that points at the better tool for one specific job is more trustworthy, not
   less — and it is what the "one page per thing" rule implies when someone else
   owns that thing.
4. **Consider approaching them.** We will hold something all four lack: prices.
   A data exchange, or a mutual link, is a real proposition and costs nothing to
   ask. **This is a decision for Sleven, not a technical call.**

---

## UNCERTAIN, FLAGGED

- The 48 dangling pools — a pool referenced by a blueprint with no contract
  awarding it. Could be unimplemented content, could be a gap in the extraction.
  Not investigated.
- `Chance: 0.25` appeared on only 2 pools in the first third of the scan. I did
  not tabulate chance across the full set.
- Whether contract availability is patch-current. These are game files from
  2026-08-01; the game is on 4.9. Contract structures change between patches.
- I did not check any of the four tools' terms of use. If Sleven wants to pursue
  option 4, that should be read first — by a person, not by me.

### 2026-08-02 00:41:08 — update_testing_deploy_complete.md

# UPDATE — testing site deployed and verified from served bytes

## Pre-stage re-hash — all three matched

Re-hashed immediately before staging, per instruction:

| file | result |
|---|---|
| `testing/_src/_layer.src.html` | `c26caed…6167634` **match** |
| `testing/_layer.html` | `058d9ce…3582c65` **match** |
| `testing/_deploy/index.html` | `be79501…8de8fb08` **match** |

Landed 00:19:25-27, re-hashed 00:29:56 — stable, no drift.

## Deploy

Cloudflare Workers static assets, worker **`citizencompasstesting`** — the name
matched `wrangler.toml`, so this updated the existing site rather than creating
a second one at a second URL.

```
482 files read from _deploy
1 new or modified asset uploaded: /index.html   (479 already uploaded)
Uploaded citizencompasstesting (8.46 sec)
https://citizencompasstesting.citizencompass-contact.workers.dev
Version ID: 7adec060-3a72-4c1c-857a-adbf967d1d1f
```

Only `index.html` changed, which is consistent with a layout-only edit.

**One blocker cleared on the way:** `wrangler whoami` reported "not
authenticated". `CLOUDFLARE_API_TOKEN` **is** in `.env` (53 chars) — wrangler
simply does not read `.env`. Loaded it into the environment for the invocation.
I did **not** use `wrangler deploy --temporary`, which wrangler suggested: that
publishes to a temporary preview account, which is exactly the
two-URLs-in-circulation failure `wrangler.toml` warns about at length.

My first check of that token was also wrong — a `grep -o` truncated at the `=`
and made a populated value look empty. Corrected before acting on it.

## Verified from the served bytes, not the exit code

| check | result |
|---|---|
| index serves | **HTTP 200**, `text/html`, 1,513,625 bytes |
| served index == local | **sha256 identical** (`be79501e…`) |
| model serves | `100i.glb` **HTTP 200**, 1,487,156 bytes |
| model byte count vs local | **exact match** |
| model is a real glTF | magic bytes `glTF` |

Required markers, all present in the **served** HTML:

| marker | occurrences |
|---|---:|
| `cc-ldock` | 10 |
| `cc-kb-tab` | 8 |
| `cc-fi-tab` | 7 |
| `cc-mtab` | 10 |
| `id="cc-kb"` | 1 |
| `cc-ship::after` | 2 |

The exit code was 0, but it is not what any of the above rests on.

## Observation on the leftover positioning rule

`calc(44% + 430px)` — LOADOUT's old slot — is **gone**. `calc(44% + 570px)`
still appears once, in the *first* `#cc-fi-tab` rule.

It is inert. There are five `#cc-fi-tab` rules, and the fourth overrides it:

```css
#cc-fi-tab{top:auto !important;bottom:10px;right:376px; …}
```

`top:auto !important` beats the earlier `top:calc(44% + 570px)`, so FIND is
never placed at 1045px.

Worth knowing how the dock actually works: the tabs are moved into `#cc-ldock`
by **JavaScript at runtime**, with a retry loop ("keep looking until the
late-built ones arrive"), not by static markup — `cc-fi-tab` is not inside the
dock element in the served HTML. `#cc-ldock` itself is
`transform:translateY(-50%)`, i.e. genuinely vertically centred rather than
stacked from 44%.

**The failure mode if that script does not run is benign:** the CSS fallback
puts FIND at `bottom:10px; right:376px` — on screen, not off it. That is a
better degradation than the old stack had.

No action taken on the stale rule; it changes nothing and is not in scope.

## Not committed

No commit-and-push go-ahead was given for this task, and rule 2 requires it per
change. The `build_deploy.py` edit from the previous order also remains
uncommitted in the working tree.

Live Netlify site untouched.

### 2026-08-02 00:36:10 — update_testing_deploy_intake.md

# UPDATE — deploying the testing site

Filed on intake per rule 13.

## Pre-stage re-hash — all three match

Re-hashed immediately before staging, as instructed, not just before deploying.

| file | expected == actual |
|---|---|
| `testing/_src/_layer.src.html` | `c26caed…6167634` YES |
| `testing/_layer.html` | `058d9ce…3582c65` YES |
| `testing/_deploy/index.html` | `be79501…08de8fb08` YES |

Landed 00:19:25-27, re-hashed 00:29:56 — stable for ten minutes, no drift.

## What is being deployed

Cloudflare Workers static assets, per `testing/wrangler.toml`:

- worker name **`citizencompasstesting`** — the name IS the subdomain, so this
  updates the existing site rather than creating a second one
- `testing/_deploy/` — 480 files, 349 MB, 235 `.glb` models
- **The live Netlify site is not touched by any of this.**

480 files is far inside the 20,000-file static-asset cap.

## What changed in this build

KEYBINDS and FIND moved from the right edge to a new left dock (`#cc-ldock`)
alongside MANUFACTURERS. DISPLAY and FEEDBACK stay on the right. The dock is
vertically centred rather than stacked downward from 44%, which is what put the
fifth tab at 1045px on a 1080px viewport.

Verified by Sleven at 1920x1080, 1600x900, 1366x768, 1280x720, 1024x600 and
390x844 — every tab on screen, zero overlaps, zero page errors.

## Verification plan — served bytes, not exit code

The deploy script has already reported **exit 1 on a fully successful deploy
once**, so the exit code is not trusted as evidence. After deploying I will
fetch from the served URL and confirm:

- index serves
- a model file serves with a plausible byte count
- the page contains `cc-ldock`, `cc-kb-tab`, `cc-fi-tab`, `cc-mtab`,
  `id="cc-kb"` and `cc-ship::after`

### 2026-08-02 00:31:36 — update_crafting_competitive_scan.md

# Crafting category is already crowded — four live tools. 2026-08-02, C2

Full scan + eight design approaches: `claude/crafting-competitive-scan-and-approaches.md`
on claude.ai. Read-only. **C2 wrote nothing to the repository.**

## Four live competitors, all fan-made

1. **citizen-starter-guide.com/star-citizen-blueprint-finder/** — CMDR Quattro.
   Posted to RSI Community Hub (27 upvotes). Search all blueprint types; pooled
   armor sets; **gives the exact MobiGlas tab, faction and contract title per
   blueprint**; 4.8 grind-route planner that sequences contracts, respects
   reputation gates and inserts rep contracts. Stanton/Pyro/Nyx filter,
   lawful/unlawful badges, payouts.
2. **sc-craft.tools** — Norkaan / HTTPS org. 1,000+ blueprints, ownership
   tracking, filter by mission/contractor/resource/system. **Models quality
   modifiers on stats** (damage mitigation, temp resistance, fire rate, recoil).
   "Updated every patch."
3. **star-crafting.com** — 266 blueprints, 247 materials, 156 locations, 2,915
   Finder records, community submissions. States coverage openly: "0/11
   locations mapped".
4. **sccraftlab.com** — blueprints, ships, components, mining calculator,
   missions, Executive Hangar PowerCycle, universe explorer. Crafting queue,
   inventory, rep tracking, org libraries — **behind registration.** Roadmap
   includes an AI assistant, 2026-2027.

## The gap, and it is consistent

**None of the four shows a price.** No ingredient cost, no craft-vs-buy, no
market data at all. star-crafting has 156 locations and 0 of 11 mapped;
sccraftlab has a mining calculator and no prices.

Reason is structural: recipe data is static and shippable, prices need a live
feed and honest tolerance. **We already hold 23,734 item prices and a verified
UUID join to 719 craftable outputs.** This is the only defensible angle.

Two secondary gaps: no-login (sccraftlab gates its best features), and nobody
connects crafting to a specific player's ship.

## Correction to my own claim from earlier today

I said crafting quality/stat modelling was something nobody does. **Wrong.**
sc-craft.tools advertises exactly that. I claimed a differentiator from what the
data allowed without checking what competitors ship — third time this week I have
reasoned from a proxy instead of the artifact.

## Consequence for build order

Do not build a fifth recipe database. The three ideas worth pursuing (craft-vs-buy
verdict, the materials trip, resource-as-destination pages) are **all blocked on
the same single item: pulling UEX commodity prices.** That reinforces the
recommendation already filed in `inbox/update_blueprint_data_found.md`.

One idea needs no new data and is genuinely unserved: **reverse lookup** — "here
is what is in my hold, what can I make?" All four tools filter *by* resource;
none inverts it. Aslarite alone appears in 856 of 1,597 blueprints.

### 2026-08-02 00:23:40 — update_blueprint_data_found.md

# Blueprint/crafting data found — and the one pull that unblocks it. 2026-08-02, C2

Full detail: `claude/finding-blueprints-crafting-data.md` on claude.ai.
Read-only investigation. **C2 wrote nothing to the repository.**

## What is on disk

`scunpacked-data/snapshots/20260801T204744Z/blueprints.json` — **1,597
blueprints**, plus a `blueprints/` folder with one file each. All
`Kind: "creation"`, all single-tier.

Per blueprint: `Output` (UUID/Class/Type/Subtype/Grade/Name), `CraftTimeSeconds`,
`Availability` (`Default` + `RewardPools[]`), and a `Requirements` tree of
`root → group → resource|item` with `QuantityScu` and `MinQuality` per leaf.

Groups are named parts — Insulative Liner (853), Armored Carapace (451),
Frame (272), Shell (233), Barrel (98). Each group carries stat `Modifiers` with a
`QualityRange` 0–1000 mapped to a `ModifierRange`: craft quality shifts real
stats, e.g. `health_maxhealth` 0.9×–1.1×, `weapon_damage` 0.95×–1.05×.

Craftable output: armor 684, personal weapons 174, ship guns 96, power plants 75,
coolers 74, shields 62, radar 60, quantum drives 57, plus attachments and tools.

Ingredients: **37 distinct**. 26 join by UUID to `resources/commodities.json`
(Aslarite alone appears in 856 blueprints). The other 11 are `Kind: "item"`
hand-mined gems — Hadanite, Dolivine, Aphorite, Sadaryx and so on — **not** in
`commodities.json`.

Acquisition: **8** blueprints are `Default: true`. **724** come from named
reward pools. **865 have neither** — the data does not say how you get them.

## The join works — 719 items

`Output.UUID` → `items_prices_all.json.item_uuid` matches on **719 of 1,588
craftable items.** Proper UUID join, no name matching. Spot-checked:
`BP_CRAFT_AMRS_LaserCannon_S1` → `26838ca7-...` "Omnisky III Cannon" →
`id_item 1`, 15,461 aUEC at CenterMass Area 18.

That supports craft-vs-buy on 719 items, which nothing else on the market does.

## THE BLOCKER — no commodity prices exist anywhere on disk

Verified twice:

- `items_prices_all.json` has **zero** rows in the Commodities section. All
  23,734 rows are gear/component sections.
- `resources/commodity_trade_locations.json` (41 MB, 109 commodities) lists
  **where** commodities are sold, with **no price field**.

The 2026-08-01 UEX pull covered `/items/` and vehicle purchase prices and did not
include commodity prices. **Recommend pulling them.** It is the highest-value
single data addition found so far: it completes craft-vs-buy AND fills the
"how much does RMC sell for" intent that the item-page plan currently cannot serve
(only 171 of 7,728 items have a sell price).

Second, smaller gap: the 11 hand-mined gems are not commodities and would still
be unpriced. ~30% of recipes would remain partially costed — state that on the
page rather than estimating.

## Worth testing, cheap

**`RewardPools` → `contracts/` join.** Pool keys look mission-related
(`BP_REWARDS_FullStrikeOnStationB`). If it resolves, "where do I get this
blueprint" becomes answerable. Not attempted.

## Not verified

- Whether 4.9 changed crafting. Confirmed by search that crafting/blueprints are
  live since 4.8; did not read 4.9 notes in detail. Snapshot is from 2026-08-01.
- **A community blueprint-finder tool already exists**, posted on RSI's Community
  Hub. Not evaluated. Look before building — same call as Star Binder.
- What the 865 no-default-no-pool blueprints mean.
- `CategoryUUID` not resolved to names.

## Closing an open item: `tags.json` checked, does not help

Flagged as unopened in `claude/plan-doorways-and-browse-layer.md` §2.
It is a dict of **18,844** UUID → {name, parent_uuid}, 70 roots — the engine's
internal tag tree, not a consumer taxonomy. Largest branches: `ItemPorts` 809,
`SpawnCloset` 247, `DefendArea` 246. Roots include `Subsumption`,
`PopulationManager`, `EntitySpawner_Printing`.

**It does not replace the proposed tag model** — that section of the doorway plan
stands. Four subtrees worth mining later: `LocationType` 147, `MissionType` 101,
`Series` 96, `Manufacturer` 90.

### 2026-08-02 00:16:35 — update_frontend_three_items_complete.md

# UPDATE — front-end order: all three items done. Stopping as instructed.

Builds A, B and C not started — they are downstream of decisions 2 and 3.

## 1. `find.src.html` added to PAGES, guard re-proven

```python
PAGES = [
    ('keybinds.src.html', 'keybinds.html'),
    ('loadout.src.html',  'loadout.html'),
    ('find.src.html',     'find.html'),
]
```

**Rule 12, three entries:**

| test | result |
|---|---|
| all three outputs moved aside, rebuild | **all three restored, byte-identical** (25,106 / 23,104 / 20,517) |
| `find.src.html` removed (the *new* entry) | **exit 1**, "PAGE SOURCE MISSING: find.src.html" |
| source restored, rebuild | exit 0, all three copied |

Outputs were **moved aside to `_to_delete/`, not deleted** (rule 1) and restored.

**A correction to my own method, worth recording.** My first read of the failure
case reported `BUILD EXIT=0` — because I piped Python through `tail`, so `$?`
captured `tail`, not Python. The guard was fine; my measurement was not. Re-run
without the pipe: **exit 1**. This is precisely the trap rule 12's new paragraph
describes — prove by behaviour, and make sure the thing you measured is the
thing you meant to measure.

**Observation, not a defect:** when the guard fires, `index.html` has already
been written, so `_deploy/` is left with a new index and a stale page from the
prior build. On a fresh deploy directory there would be no stale page and links
would 404 — exactly what the error message says. Not changing it; out of scope.

## 2. Tab layout — RECOMMENDATION ONLY, nothing implemented

Confirmed the order's measurements in the source: `calc(44% + 150px)`,
`+290px`, `+430px`, `+570px`.

On 1920×1080, 44% = **475px**:

| tab | top | on a 1080px viewport |
|---|---:|---|
| DISPLAY | 475px | fine |
| FEEDBACK | 625px | fine |
| KEYBINDS | 765px | tight |
| LOADOUT | 905px | mostly off-screen |
| FIND | **1045px** | **35px of viewport left — effectively invisible** |

**Also confirmed: the page already has a `<nav>`**, carrying *Ship Purchase
Matrix* and *Sale Calendar*. There is somewhere for destinations to go.

### Recommendation

**Split by kind, not by fitting more in.**

- **Right edge keeps DISPLAY and FEEDBACK.** Both act on the page you are
  looking at. Two tabs sit at 475px and 625px — comfortably on screen at 1080p,
  with room for a third at 765px if one is ever genuinely page-level.
- **FIND moves into the existing `<nav>`.** It is a destination, the nav already
  exists, and it already holds exactly this kind of link.
- **KEYBINDS moves into the nav too.** Same reasoning.
- **LOADOUT is already ruled** — it goes on the ship page, opening on the ship
  you are viewing. That is the pattern for destinations and it is the right one.

That is 5 → 2 on the right edge, and nothing becomes unreachable.

### On build ownership

The order is right that hand-patching after every build is not workable, and
right that C2's 8a would make Sleven's LOADOUT removal impossible.

**The build should own an explicit list with an explicit position per tab** —
not re-emit whatever was last in the file. Adding a sixth then requires editing
the list and choosing a position, which is a deliberate act with a visible
layout consequence, rather than a silent append that pushes something
off-screen. Removing one requires deleting a line, and it stays removed.

**Not implemented.** Sleven decides the layout first; emitting a broken layout
reliably is not an improvement.

## 3. The backend decision — for Sleven, with corrected numbers

**Two of the order's figures are not supported by the landed data**, and one of
them changes the arithmetic that the whole ceiling argument rests on.

Measured directly from the sealed snapshots:

| quantity | order says | **measured** | source |
|---|---:|---:|---|
| item files | "21,849" | **7,728** | UEX snapshot, 100 category files |
| labels | "90,121" | **63,375** | source 2 snapshot, matches its manifest |
| item price rows | — | 23,734 | UEX `items_prices_all` |
| terminals / shops | 823 | **823** | UEX `terminals` |
| ships | 316 | 316 game files, 254 live | `ship_resolution.json` |

**21,849 is close to nothing in the data. 23,734 is the item *price row* count** —
so the likely explanation is items being conflated with price rows. Worth
confirming before anyone quotes it again.

### What that does to the ceiling argument

A page-per-item build is:

```
7,728 items + 823 shops + 316 ships = 8,867 pages
```

**That is under the 20,000-file Cloudflare cap, not over it.** The order's "would
exceed it" does not hold against the measured counts. The cap is real; it is
just not the binding constraint at this size.

### The trade-off, stated plainly

**Static JSON**
- Keeps the zero-backend property. A deploy stays a folder of files.
- No uptime dependency, no monitoring gap, no fallback to design.
- A bundled index with client-side rendering avoids per-item files entirely, so
  the cap is not even approached.
- Cost: heavier client, and filtering/search happen in the browser.

**FastAPI**
- More flexible; Railway already runs and currently powers nothing public.
- Cost: the site starts depending on a service being up. There is **no
  monitoring, no uptime history, and no fallback** for when it is not — and the
  live site has never had a runtime dependency.

### Recommendation

**Static JSON.** Three reasons, in order of weight:

1. The measured page count fits comfortably, so the argument that forced FastAPI
   does not survive the corrected numbers.
2. Introducing a runtime dependency is a one-way door for a site whose entire
   deploy story is "a folder of files", and it would be taken before any
   monitoring exists to notice it failing.
3. Nothing on the roadmap yet needs server-side work — no auth, no writes, no
   real-time. FastAPI becomes the right answer the moment one of those appears,
   and that decision is cheaper to take later than to unwind.

**This is a recommendation, not a decision. Waiting.** No FastAPI work started.

## Also confirmed while here

- `data-layer/ship_resolution.json` exists and is structured as the order
  describes (`counts`, `matched`, `no_game_file`, `ambiguous`, `tier_variants`).
  Used, not re-derived.
- The build independently reports `unmatched: 6` naming 85X, Arrastra, Fury,
  Mantis, Merchantman, PTV — the same six the auditor found. Third independent
  corroboration.

## Not committed

This order does not grant commit-and-push authority and hard rule 2 requires it
per change. The `build_deploy.py` edit is in the working tree, proven, and
uncommitted. Say the word.

*(+90 older update(s) — full history in docs/handoff_archive/_updates_log.md)*

---

## PROJECT NOTES (from most recent full handoff doc)

# UPDATE — PART C: both Go defects fixed and proven; STOPPED at step 4's stop condition

Defects 1 and 2 are fixed and proven against known-bad input. Step 4's
comparison found a **third difference**, so per the work order I have stopped
and am reporting rather than proceeding to delete `generate_handoff.py`.

## Defect 1 — invented entries — FIXED

`watcher-go/handoff_regen.go`. `strings.Split(string(raw), "\n### ")` replaced
with `updateEntryHeaderRe`, matching only the headers `appendUpdate()` writes.
Both required edge cases preserved: an empty header set returns the whole file
as one entry, and preamble before the first header is kept.

Also extracted `parseUpdateEntriesFrom(path)` so the parser can be exercised
against fixtures rather than only whatever the live log happens to hold.
`parseUpdateEntries()` calls it with `updatesLogPath()` — behaviour unchanged.

## Defect 2 — classification by prose — FIXED

`watcher-go/handoff.go`. `titleLine()` added; both `isHandoffDoc()` and
`isUpdateDoc()` now use it instead of `firstRunesUpper(text, 500)`.
**Evaluation order unchanged** — filename hints first, `isHandoffDoc()` before
`isUpdateDoc()`, a doc matching both is a full handoff. `firstRunesUpper` had no
remaining callers and was removed, with a comment recording what it was and why
it went.

## Rule 12 — proven, not asserted

`watcher-go/handoff_defects_test.go` and `handoff_livelog_test.go`. `go build`,
`go vet` and `go test ./...` all clean.

| test | asserts |
|---|---|
| subheadings stay inside their entry | a body with two `###` subheadings yields **1** entry, not 3, and keeps both |
| no headers returns whole file | content is not dropped |
| preamble preserved | text before the first header survives |
| hyphen separator parses | `-` works as well as `—` |
| update mentioning "handoff" in BODY | classified as **update**, not handoff |
| genuine handoff title | still detected (`CITIZEN COMPASS HANDOFF`, `SESSION ARCHIVE`) |
| filename hint still wins | evaluation order intact |
| `titleLine` | first heading, else first non-blank line |
| **live `_updates_log.md`** | **70 total `###` headers -> 50 parsed entries, 0 phantoms** |

Python (fixed) on the same live log: **50 entries, 0 phantoms.** Identical.

## Step 4 — the comparison, and the STOP

Built the fixed binary and regenerated via `--once`, then regenerated with
`generate_handoff.py`, and diffed.

**The improvement is real and large:** fixed Go emitted **102,901 chars** where
the deployed binary was emitting ~65,000. That recovers almost exactly the
~37,000 characters the addendum measured as discarded.

**Both defects are confirmed fixed by structural comparison:**

| | Go (fixed) | Python (fixed) |
|---|---:|---:|
| `###` headers in output | 40 | 40 |
| timestamped entries shown | 20 | 20 |

Identical. No phantoms, no classification divergence.

### But the outputs still disagree — third difference found

Beyond the Go-only version-marker block (which is the KEEP feature and is
expected), the diff is 21 lines in two groups:

**1. Number formatting — 5 lines.**

| Go | Python |
|---|---|
| `**Project health score:** 35.0/100` | `**Project health score:** 35/100` |
| `- Data completeness: 0.0%` | `- Data completeness: 0%` |
| `- Viewer progress: 50.0%` | `- Viewer progress: 50%` |
| `- Documentation: 100.0%` | `- Documentation: 100%` |
| `**Ships:** ... (50.0%)` | `**Ships:** ... (50%)` |

**2. Python emits a trailing line Go has no equivalent for:**

```
*(raw text of the most recently adopted handoff doc — local AI compression
unavailable right now, showing it unmodified)*
```

That is Python's Ollama-fallback footer. Ollama is disabled and parked, so
Python takes the fallback path and says so; Go never compresses at all, so it
has nothing to report.

### Why I am stopping rather than judging

The work order is explicit: *"If they still disagree there is a third difference
— stop and report, do not assume Go is correct because it was fixed twice."*

They disagree. I can characterise both differences and neither touches entry
content or classification — but "I can explain it" is not "it matches", and this
is precisely the reasoning the stop condition exists to prevent. **Not
executed:** step 5 (delete `generate_handoff.py` and `_verify_generate_handoff.py`)
and step 6 (the CLAUDE.md additions).

### The decision these need

- **Number formatting:** which is correct? Python's `35/100` reads better;
  Go's `35.0/100` is what the live document will show. One of them should
  change so the two agree, or Python's retirement makes it moot.
- **The Ollama footer:** Go is arguably right to omit it, since it never
  attempts compression. If so, this difference is expected rather than a defect
  — but that is a call to make explicitly, not to assume.

## Deployment state — the fix is NOT live

`inbox_watcher_fixed.exe` (5,735,424 bytes, built from fixed source) sits in the
repo root. `inbox_watcher.exe` (3,884,032 bytes, 29 July) is still the binary
the scheduled task runs.

**So the live watcher is still the defective one**, still emitting ~65k with
phantoms. Replacing it means stopping the scheduled task to unlock the file, and
I have not done that — deploying while an unexplained third difference stands
would bake in whichever formatting Go happens to use. Say the word and it is a
two-minute change.

Nothing deleted. `generate_handoff.py`, `_verify_generate_handoff.py` and
`inbox_watcher.py` are all still on disk. Comparison artifacts moved to
`_to_delete/go_migration_comparison_20260801/`.

