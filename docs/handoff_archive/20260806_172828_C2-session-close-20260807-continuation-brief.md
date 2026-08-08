# HANDOFF — C2 session, 2026-08-05 → 2026-08-07

    from     C2 (Cowork), closing
    for      the next session, whoever it is
    scope    what you need to CONTINUE. Not what I did.
    read     this first, then docs/HANDOVER-collector-rev5-COMPLETE.md

**Two rules before anything else, both learned the hard way this session:**

> **1. Before declaring anything absent from this repo, search at least THREE
> phrasings.** I grepped `docs/` for "approval", found nothing, and told Sleven
> the CIG record did not exist. It was in two files I had already read. The word
> "approval" appears zero times in the file that holds it.

> **2. File to `inbox/` BEFORE handing anything to Sleven.** The moment he has a
> document he forwards it. If it is not filed at that instant, the machine-side
> session is working from a copy the repo has no record of.

**And a mechanical fact that wasted an hour: `inbox/` reads EMPTY almost always.
That is healthy.** The Go watcher lifts files out within seconds and moves them
into `docs/`. **To verify a drop landed, look in `docs/` — never in `inbox/`.**
Also: **you cannot build a file inside `inbox/` in stages** — the watcher takes
it mid-write. Build outside the repo, place it complete, in one operation.

---

# PART 1 — SETTLED. Do not re-derive.

| Settled | Where |
|---|---|
| **CIG confirmed the site 2026-07-28** under clause 2(k), submitted 07-25. Sleven has a live RSI legal contact and has been through the Fan Kit. **A fresh 2(k) notification IS due** — the confirmation describes a ship price table as it stood then. | `docs/RECORD_cig-fansite-approval.md` |
| **Compass is free forever. No ads, no sponsors, no paywalls.** Advertising exists only inside an arrangement made *with* CIG. Binding, not open to proposal. | `docs/RULING_advertising-amended-sleven-own-terms.md` |
| **One item record, many placements.** Ship-attached items appear in the ship section AND stay in the catalogue. Liveries are a category off by default. | `docs/RULING_one-item-record-many-placements.md` |
| **Commodity prices exist.** UEX served 2,597 rows, 123 commodities × 135 terminals, median age 1 day. The gap was a request never made. | `docs/handoff_archive/20260805_203717_...uex-commodities-landed...` |
| **Mission payouts are in the files for ~50%** — `FixedReward` is a dict with a real amount. `CalculatedReward` is a boolean and marks the runtime-computed half. | `docs/REPORT_full-data-layer-dig-and-two-corrections.md` §1 |
| **Quantum range is precomputed** per ship, 257 of 316, in `ships.json QuantumTravel`. Do not derive it. | `docs/URGENT_ships-json-quantum-range-job2.md` |
| **206 commodities, 96,717 commodity↔location pairs**, in `resources/`. Closes the "remaining gap" declared 2026-07-31. | `docs/URGENT_commodity-gap-closed-resources-folder.md` |
| **Extracted creative assets are OUT.** Textures, icons, models, CIG's description text. Factual data from game files is fine. | `docs/CORRECTION_extracted-textures-are-not-granted.md` |
| **No licensed item icons exist, from anyone.** Fan Kit has no item category. Cornerstone, the wiki, UEX, Erkul, sc-craft, star-crafting, sccraftlab — all checked, none grants reuse. | `docs/ANSWERED_image-licensing-cic-research-and-analysis.md` |
| **Player screenshots ARE covered** by CIG's stated exemption, on a compliant fan site. | same |
| **Cloudflare Workers:** 20,000 static files free / 100,000 paid, 25 MiB per file both tiers, static asset requests "free and unlimited", storage free. **Only file count binds.** ~11,225 used. | `docs/WORKORDER_image-01-...md` §5 |
| **Fan-site compliance checklist**, verbatim, complete. Domain `citizencompass.netlify.app` passes the brand-string test. | `docs/AMENDS_wo-image-01-mandatory-image-marking-and-atlas-conflict.md` §3 |
| **Every published image must carry a Made-by-the-Community logo + trademark notice**, corner, ≥50% opacity, legible. | same, §1 |
| **UEX's item taxonomy is good** — 17 sections, 55 categories. Keep it as the spine. Do not build a second one. | `docs/FINDING_7728-items-taxonomy-three-real-problems.md` |
| **The grabber is BUILT and working.** Process-locked to `StarCitizen.exe`. 7 captures. | `citizen-collector/`, `docs/handoff_archive/20260805_201715_...` |
| **MyBook backup verified.** 17.8 GB, 85,768 files, exit 0. The old exit-1 was PowerShell wrapping `git bundle verify`'s success message on stderr. | `docs/handoff_archive/20260805_211606_...` |

---

# PART 2 — OPEN, RANKED, WITH WHAT BLOCKS EACH

**1. The ten-minute in-game test.** BLOCKS: the glyph atlas, the reader, the
vocabulary, the event recorder — the entire reading half of the collector.
Blocked on: **Sleven, and nothing else.** Two questions at once: is the UI font
legible in a captured frame at 1920×1080, and **is the aUEC balance visible
while a shop panel is open** (that one gates the whole event recorder and is
easy to forget). Open since 2026-08-02.

**2. Does the collector's price role survive?** BLOCKS: rev 6 of the collector
spec. Blocked on: **Sleven's ruling.** C2's read is that the defensible role is
**patch-attributed observation**, not price coverage — UEX has coverage and
freshness, and cannot stamp a patch. **Do not write rev 6 before this lands or
you write it twice.**

**3. Liveries: listed or paged?** BLOCKS: nothing — the join work is identical.
C2 recommends listed-only with a deep link to the ship page. `WO-PLACE-01 §2a`.

**4. Is "Ship Armor" structural or cosmetic?** BLOCKS: only the category label.
43 items, 0 priced, 0 shops. `WO-PLACE-01 §3`.

**5. The image-marking vs atlas conflict.** BLOCKS: the atlas pipeline, which is
**not cleared to build**. A legible mark in the corner of a 64 px icon is not
achievable. Blocked on: reading what the Fan Kit's own docs say about applying
the mark — **and Sleven already has the kit.**

**6. Three secrets unrotated** — UEX token, PostgreSQL password, Cloudflare
token. All exposed. **Oldest open item in the project.** Blocked on Sleven.

**7. The fresh clause 2(k) notification.** A draft is already specified in
`docs/workorder-image-provenance-and-renders.md` Part 3. **Code does not send
it. Sleven does.**

**8. The path-join bug.** Live — fired 2026-08-06 03:32 and left a zero-byte
artifact inside `snapshots/`. Four occurrences. `docs/URGENT_path-join-bug-is-live-fired-tonight.md`

**9. `NotForRelease` / `WorkInProgress` filter.** Nothing filters on them.
**Contract-derived pages may be advertising unreleased missions right now.**

**10. `FixedReward` census.** C2's 50/46 is a 25% sample; a full scan timed out
through the Cowork bridge. **Run it locally.**

**11. `blueprint_index.json` is still 11.4 MB** at the top level. Live
dependency or leftover? Under the static ruling, a page that fetches it is the
failure mode.

---

# PART 3 — WHAT I WAS MID-WAY THROUGH

**The 7,728-item filing system.** Sleven ruled on placement (Part 1). `WO-PLACE-01`
covers liveries and ship armour. **Four of the six rulings are still open:**

    "Full Set" (112)    is a set an item or a container? It behaves like a bundle.
    junk drawer (366)   six buckets identified, not yet confirmed or named
    commodities         175 in UEX items / 206 in game files / 204 from UEX's
                        commodities endpoint. THREE COUNTS. Which is
                        authoritative, one page type or two?
    no manufacturer     3,218 items, 42%. Leave blank, infer, or hide the filter?
    (3,218)

**Sleven said he can tell you where every item goes. Do not ask him to sort
7,728 things — get the rules, not the rows.**

**CIC (the research assistant) is mid-thread and productive.** He found the
image-marking rule and the fan-site checklist. He offered to draft the exact
footer notice markup and the atlas/`<picture>` delivery structure. **He correctly
refuses to download the Fan Kit on Sleven's behalf.**

---

# PART 4 — FINDINGS ONLY IN MY CONTEXT, NOT YET IN A FILE

**These die with this session unless carried forward.**

**`screenshot` is an empty string on all 7,728 UEX items.** The image gap,
confirmed at the source rather than inferred.

**The UEX item schema, 28 fields:** `id, id_parent, id_category, id_company,
id_vehicle, name, section, category, company_name, vehicle_name, slug, size,
uuid, color, color2, url_store, wiki, quality, is_exclusive_pledge,
is_exclusive_subscriber, is_exclusive_concierge, is_commodity, is_harvestable,
screenshot, game_version, notification, date_added, date_modified`.
**`id_parent`, `id_vehicle`, `color`/`color2` and `quality` have never been
examined by anyone.**

**130 distinct manufacturers.** Clark Defense Systems 455, RSI 402, Kastak Arms
218, Greycat 199, Fiore 146, Behring 137, Stegman's 116, Roussimoff 111, Virgil
111, Aegis 109, Quirinus 108, Drake 106. **3,218 items have none.**

**Priced coverage by section**, which nobody has looked at: Clothing 1055/1809,
Armor 710/2366, Personal Weapons 157/558, Vehicle Weapons 185/324, Systems
176/272, **Liveries 19/1099**, **Commodities 0/175**, Utility 84/91, Technology
20/20.

**A browsable HTML of all 7,728 exists** at
`C:\Users\david\Downloads\citizen-compass-all-7728-items.html` — search, sort,
filter, prices and price age joined. **Built this session, referenced in no
document.** Also `C:\Users\david\Downloads\_cc_items_merged.json`, a scratch
merge — safe to delete.

**Name-pattern rule test:** 21 rules matched 3,733 items (48%) — **but most were
re-deriving what UEX already supplies correctly.** The measurement is the
finding: **do not build a second taxonomy.** Rules apply only where UEX is
silent or the shape is wrong.

**Two orphan files from the path bug** sit beside the snapshot directories:
`20260806T033217Z.pullstderr.log` (98 bytes) and `.pullsummary.json` (0 bytes).
**The 98-byte one contains the misleading dotenv error** — it is the physical
evidence of that defect and worth keeping until the bug is fixed.

**`data-layerrawhardpoints/ship_specs.json` is real ship data**, not junk — uuid,
game_name, slug, class_name, port_tags, sizes. **Do not bin it with the two
empty malformed directories.**

---

# PART 5 — WHAT I GOT WRONG, AND HOW

**Thirteen errors in about eight hours. Sleven or another AI caught most of
them; I caught a few myself. The individual mistakes matter less than the four
patterns underneath, which are in §5.15.**

## 5.1 — I called a working tool broken

Reported `device_commit_files` as silently failing: five files "written", inbox
empty. **It had worked every time.** The watcher moves files to `docs/` within
seconds. **I checked where I put files, never where they went.** Told Sleven a
tool was defective on that basis.

## 5.2 — "Mission payouts are in no file. Only observable."

Stated three times as fact. **`FixedReward` is present on ~50% of contracts with
real aUEC amounts.** I found `CalculatedReward` was a boolean and stopped
looking. **This was the #1 justification for the entire collector.**

## 5.3 — "Screenshots are the only route to commodity prices."

Every plan for weeks rested on it. **UEX serves them; the endpoint was never
called.** I inherited the premise and never tested it. The root cause was a bare
`except ImportError: pass` swallowing a dotenv failure and reporting a missing
token that was never missing — **but I could have found that by reading the pull
summary, which I eventually did, hours later.**

## 5.4 — "Zero item images. 0% coverage."

**39.1% — 4,805 of 12,283 rows — carry image URLs**, in a source already gated
on disk and never parsed.

## 5.5 — "`items/` is `items.json` split per file."

Counts matched exactly (21,849 both) so I stopped. **Every file is
`{Item, Raw}`; `items.json` holds only the `Item` half. ~850 MB of `Raw` never
opened**, carrying a per-item 3D model path.

## 5.6 — "1,774 positioned entities."

**1,196 distinct.** Nine template entities account for 578 duplicate rows.
**Claude Code caught it**, and a naive dict join would have silently discarded
up to 119 real positions.

## 5.7 — "~200 commodities."

Carried through five revisions of the collector spec as if counted. **It is
206.** An estimate laundered into a fact by repetition.

## 5.8 — "Data.p4k icons are precisely the granted class."

**No.** §XIII.D grants *"**certain** RSI Services-related images… that RSI may
expressly designate 'for fansite use'."* A texture in the shipped archive was
never designated. **CIC caught it.** I had recommended a build on it.

## 5.9 — I paraphrased the ToS from memory and filed it as a finding

Wrote in `historian-vision-architecture.md` that the grant "does not apply if
you charge a subscription or access fee", then **repeated it to Sleven as
fact.** The clause restricts *using their art and marks* while charging — a
materially different and more workable constraint. **I never opened the source
before filing.**

## 5.10 — "A separate CIG licence is the short path."

Said twice. **CIG's own FAQ: "We are not currently offering any Non-Commercial
licenses. No means no, please do not submit multiple requests."**

## 5.11 — I declared the CIG approval record absent

Grepped `docs/` for "approval", got schema and WebFetch hits, told Sleven **"it
was never written down."** It was in `workorder-image-provenance-and-renders.md`
and `URGENT_wo_craft_01_b_description_rights_correction.md` — **both of which I
had already listed and read this session.** The word "approval" appears zero
times in the file that holds it.

**This is my own starmap finding turned around.** I had written: *"Searching the
schema and calling the data absent is a mistake that will repeat. Search values,
not just keys."*

## 5.12 — I framed a question as either/or that was not

Asked whether liveries should have own pages **or** live on the ship page.
**Sleven rejected the premise: both, with visibility control.** His answer was
better, and mine would have made the ship page a second authority for what an
item is — the exact defect this project already enforces against.

## 5.13 — I filed after delivering, not before

Sleven's standing rule, stated plainly: **the inbox note goes in first, then the
file goes to him.** I did it backwards on rev 5. He forwards documents the
moment he has them; filing afterwards is filing after it mattered.

## 5.14 — I recommended sprite atlases without checking the image rules

Recommended the delivery architecture, then discovered afterwards that CIG
requires a legible logo on every image — **which a 64 px icon cannot carry.** I
found the conflict myself, but only after recommending the thing.

## 5.15 — THE FOUR PATTERNS. This is the useful part.

**A. I stopped at the first negative result.**
5.1, 5.2, 5.3, 5.5, 5.11. Grep returned nothing → absent. Field was a boolean →
no payout exists. Counts matched → same data. **One negative check is not
evidence of absence, and I treated it as proof five separate times.**

**B. I read permissively when I wanted a permissive answer.**
5.8, 5.9. Both on rights questions, both where a permissive reading unblocked
work I wanted to do. **"Certain" was doing load-bearing work in a sentence I
skimmed.** The correction came from opening the source both times.

**C. I inherited premises without testing them.**
5.3, 5.4. Two of the project's largest stated gaps were assertions nobody had
checked, and I built plans on top of them rather than checking. **A premise
repeated in three documents is still not a verified premise.**

**D. I stated estimates as counts.**
5.7, and 5.14 is the same reflex applied to design. **If a number was not
computed this session, say so.**

**Underneath all four: I was fast and confident on exactly the questions where
being wrong was most expensive** — rights, the collector's justification, and
what data we already hold. **Slow down on those three. Everything else can be
fast.**

## 5.16 — WHAT WORKED, so it is not lost with the rest

**Pushback caught more than self-review did.** Sleven caught 5.7, 5.11, 5.12,
5.13. CIC caught 5.8. Claude Code caught 5.6. **Adversarial reading by another
party found six of thirteen. Build for it rather than around it.**

**Opening the file always beat reasoning about the file.** Every correction came
from reading the actual bytes — the ToS, the pull summary, `resources/`,
`ships.json`, the contract files. **The `resources/` folder had been on disk
since 1 August and closed the project's largest stated gap in one `ls`.**

**Recording the source of a fact, not just the fact.** Claude Code's grabber
sidecar stamps `patch_source`, `location_source` and a
`location_pattern_verified` flag. **That is better provenance than I asked for
and it is the pattern that would have prevented half of §5.**
