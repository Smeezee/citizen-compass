# SC Brain — Acquisition maps for plan steps 2–8

**Status:** Architecture map pack (2026-09-14). Spec only — not built yet.
**Step 1** (local RSI watcher) = separate Build GO. **Folder tree** = already HAVE.

Done bar for every path: tracked down + automated + easy to get from `sc-brain/`.

---

## 2. Index / ask surface over SC Brain

| | |
|---|---|
| **Shelf** | `sc-brain/INDEX.md` + `sc-brain/plumbing/indexes/` |
| **What it is** | One place to find anything without archaeology |
| **HAVE** | Root `INDEX.md` stub; shelf READMEs |
| **NEED** | Per-series index files; simple “what’s new” log; later a tiny ask script (local, no cloud AI required for v1) |
| **Automation** | Each watcher/importer appends one line to `plumbing/indexes/latest.md` on change |
| **Done when** | You can open INDEX and reach every standing series in ≤2 clicks/links |
| **Builder** | Architecture writes map; Build wires append-on-change once watchers exist |

---

## 3. LIVE / PTU auto-extract on build change

| | |
|---|---|
| **Shelf** | `sc-brain/build-truth/{live,ptu,hardpoints,default-profiles}/` |
| **Call (don’t clone)** | `extract_p4k_entry.py`, `decode_cga_nodes.py`, `extract_default_profile.py`, hardpoint transform/placement under `data-layer/derived/` |
| **HAVE** | Extractors; manual per-patch habit; dual-track designed |
| **NEED** | Trigger = new LIVE/PTU build string (from RSI watcher state) → run extractors → file compiled summaries into SC Brain (pointers OK; don’t duplicate huge binaries into git) |
| **Automation** | Scheduled or event: “build string changed” → extract job → write `build-truth/live/CURRENT.md` + JSON sidecars |
| **Out** | StarBreaker; Erkul/SPViewer scrapes |
| **Done when** | New patch lands → SC Brain build-truth updates without someone remembering |
| **Builder** | Build (wire existing tools); Architecture owns shelf contract |

---

## 4. Creator watchlist claim pipeline

| | |
|---|---|
| **Shelf** | `sc-brain/creators/watchlist/` + `sc-brain/creators/claims/` |
| **HAVE** | Watchlist names seeded in README |
| **NEED** | Per-creator feed config; claim card schema; fetch new videos/streams metadata; **claims only** |
| **Claim card fields** | entities, actions, numbers, patch stamp, stance (`fact`\|`opinion`\|`speculation`), evidence link + timestamp — **never verbatim script** |
| **Creators** | Space Tomato, BoredGamer, SaltyMike, The AstroPub, Active in the Verse, Subliminal, Morphologis, SuperMacBrothers, Farrister |
| **Automation** | Local poll of channel/RSS/API → new item → empty claim stub or metadata card → optional later AI classify (not required for v1 ingest) |
| **Done when** | New watchlist upload creates a claim card under `claims/` without hand filing |
| **Builder** | Build for fetcher; Architecture locks schema first (below) |

### Claim card schema (v1)
```json
{
  "id": "creator-slug_YYYYMMDD_short",
  "creator": "Space Tomato",
  "source_url": "https://...",
  "published_at": "ISO-8601",
  "patch_stamp": "4.10.0-LIVE or null",
  "stance": "fact|opinion|speculation",
  "entities": ["ship or topic names"],
  "actions": ["what they claimed happened"],
  "numbers": [{"label": "...", "value": "..."}],
  "notes": "short non-verbatim paraphrase only"
}
```

---

## 5. Historian + pipeline board

### Pipeline board
| | |
|---|---|
| **Shelf** | `sc-brain/pipeline/{announced,teased,speculated}/` — **never mix columns** |
| **NEED** | One card per ship/feature; move between columns only with evidence link |
| **Card fields** | name, kind (ship\|feature), column, evidence[], first_seen, last_confirmed, status_note |
| **Automation** | Mostly human/Architecture filing at first; RSI + creator claims can *propose* moves (not auto-promote speculated → announced) |
| **Done when** | Board is the single place for “is this announced or rumor?” |

### Historian / continuity
| | |
|---|---|
| **Shelf** | `sc-brain/historian/` |
| **Topics** | Retired locations (e.g. Port Olisar → successor); discontinued pledges (store vs in-game are separate); “what used to be true” timeline |
| **NEED** | Timeline note format; verify-from-sources rule |
| **Automation** | Low at first — filing discipline + later AI historian track |
| **Done when** | Continuity questions answer from `historian/` without Discord archaeology |

---

## 6. Bugs, orgs, lore / languages, SQ42

### Bugs & workarounds
| | |
|---|---|
| **Shelf** | `sc-brain/bugs/{known-issues,workarounds}/` |
| **HAVE path** | CIG known-issues via patch/DevTracker once RSI watcher lands |
| **NEED** | Workaround cards: symptom, where/when, patch, steps, still_true? |
| **Done when** | Patch day refreshes known-issues; workarounds are searchable |

### Active orgs
| | |
|---|---|
| **Shelf** | `sc-brain/orgs/` |
| **Rule** | Verify real day-to-day ops; skip vanity/empty shells |
| **NEED** | Org card: name, focus, evidence of activity, last_verified |
| **Automation** | Later; start manual keepers |

### Lore / languages
| | |
|---|---|
| **Shelf** | `sc-brain/lore/languages/` |
| **NEED** | Glossaries + “where to learn” with community credit |
| **Automation** | Mostly curated; Discord harvest careful + credited |

### SQ42 (spoiler-gated)
| | |
|---|---|
| **Shelf** | `sc-brain/lore/sq42/` **only** |
| **NEED** | Cast/credits track; trailer/dev signal track |
| **Rule** | Never surface on unscoped site pages |
| **Done when** | Owner can open sq42 shelf and find cast/credits without spoiling main site |

---

## 7. Fresh pillars + Reddit / wiki soft layers

### Fresh pillars → `sc-brain/pillars/`
- Corporate / IP filings (trademarks, patents)
- Canon outside client (novels, art books, soundtracks, credits)
- Engine / industry tech talks
- Diegetic in-world media (without citizen-collector — use text-asset / other capture paths)
- Player-science methods (copy **methods** we re-run, not third-party sites)

Each pillar = subfolder + README when first series starts.

### Soft community → `sc-brain/community/`
| Path | Rule |
|---|---|
| Reddit lead scavenger | **Rumor-tagged until verified** |
| Full Wiki API sync | Archive/cross-check — **not** breaking news (wiki lags) |
| **Call** | `scripts/external_sources/api_star_citizen_wiki.py`, `tools/import_wiki_ship_fields.py` |

---

## 8. Full CIG social / video firehose + historical backfill

| Shelf under `cig-firehose/` | Status | Notes |
|---|---|---|
| youtube / twitch | NEED | Live firehose first; backfill separate job |
| social (X, Instagram) | NEED | Polite local poll; respect ToS/rate limits |
| jobs (LinkedIn) | NEED | Hiring = build signal |
| Historical backfill | NEED | Separate from live — don’t block live watcher |

**Depends on:** step 1 RSI watcher pattern proven, then clone cadence for each channel.

---

## What Architecture needs from Owner (only if stuck)

Almost nothing to start maps. Only later:
- Confirm creator watchlist adds/drops
- Confirm SQ42 spoiler policy stays “shelf only”
- Word to register any new Scheduled Task (hard rule 6)

**Do not wait** on another agent to write these maps.

---

## Suggested build queue after RSI watcher (step 1)

1. Index append-on-change (step 2) — small  
2. Build-string → extract hook (step 3) — uses existing tools  
3. Claim schema + one creator fetcher (step 4) — prove pattern  
4. Pipeline board templates (step 5) — mostly docs/cards  
5. Then 6 → 7 → 8 as capacity allows  

---

## Related
- Master plan: `docs/SC-BRAIN_master-acquisition-plan-2026-09-14.md`
- Tree: `sc-brain/README.md`
- RSI watcher GO: `correspondence/open/build/2026-09-14_memo_build_go-rsi-firehose-watcher-sc-brain.md`
