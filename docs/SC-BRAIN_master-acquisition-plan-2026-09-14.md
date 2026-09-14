# SC Brain — Master acquisition plan (combined)
**Frozen for handoff:** 2026-09-14  
**Project:** Citizen Compass · subsystem: **SC Brain**  
**Purpose:** One checklist of every intelligence path we scoped. Use existing tools where they work. Automate the rest. Done = tracked down + automated + easy to pull from SC Brain.

---

## Done bar
A path is **DONE** only when all three are true:
1. **Tracked down** — source + method known  
2. **Automated** — keeps updating without someone remembering  
3. **Easy to get** — lives in SC Brain and can be queried/shown without archaeology  

---

## Tool-use rules (Owner, 2026-09-14)
1. **Prefer existing working tools.** Do not reinvent.
2. **citizen-collector — OUT for now.** Not built properly; do not depend on it.
3. **Claude RSI hourly sweep — REROUTE.** Owner shuts down Claude side. Same information becomes a **local automated watcher** (pattern: `roadmap-watcher`), not an AI session every quiet hour.
4. **Erkul / SPViewer — do not scrape.** Match/beat their questions with our own data/math.
5. **Creators — facts only, never verbatim** scripts/monologues. Cite link + timestamp.
6. **Obsidian** = view/graph on the same project disk. **SC Brain** = compiled SC library wing inside Citizen Compass (not a second repo). Smart Second Brain plugin stays OFF by default.

---

## Legend
- **HAVE** — working tool/path exists  
- **PARTIAL** — exists but not fully live/complete/automated  
- **NEED** — still to track down and automate  
- **OUT** — explicitly not used for now  

---

## A. Official CIG firehose (north star)
| Path | Status | Notes |
|---|---|---|
| Patch notes / roundups / DevTracker / Comm-Link / Patchbot | PARTIAL → **REROUTE** | Claude hourly deleted 2026-09-14. Local `rsi-watcher/` built 2026-09-13: build line live, the three feeds NOT CONFIGURED until Research's verified endpoints land (see § RSI local watcher) |
| Roadmap / status boards | PARTIAL | Use **`roadmap-watcher`** (~4h). Do not put roadmap back on Claude. |
| Spectrum (official / full) | PARTIAL | Seed watcher on one post — expand later |
| CIG YouTube (all + CitizenCon + backfill) | NEED | |
| CIG Twitch | NEED | |
| CIG X/Twitter | NEED | |
| CIG Instagram | NEED | |
| LinkedIn job listings | NEED | Hiring = build signal |
| Historical backfill of CIG channels | NEED | Separate from live firehose |

### RSI local watcher (replaces Claude hourly)
Quiet hour (no AI):
- Fetch DevTracker, Comm-Link list, Patchbot  
- Diff post IDs + LIVE build string vs state file  
- Write state; notify only on change  
- Detect staleness (e.g. stuck relative-age strings)

Only on real change (optional wake):
- Classify / summarize the new item — then stop  

Shape already designed in project finding 2026-09-09. Pattern: `roadmap-watcher/` + scheduled task.

---

## B. Build truth (game files)
| Path | Status | Notes |
|---|---|---|
| LIVE P4K / CGA / hardpoints / defaultProfile | PARTIAL | Extractors exist (`extract_p4k_entry`, `decode_cga_nodes`, hardpoint transforms/placement); mostly manual per patch |
| PTU vs LIVE dual track (actually live) | PARTIAL | Designed; must be implemented so LIVE side is really live |
| Post-patch auto refresh (ships/items/shops) | NEED | Own dump path — not Erkul |
| Ship Matrix standing fetcher | NEED | Read once historically; no standing tool |
| StarBreaker | OUT | Not authorized; use existing custom extractors |

---

## C. Economy & shops (own data)
| Path | Status | Notes |
|---|---|---|
| UEX commodities / prices / terminals | PARTIAL | `import_uex_*` + external-sources; keep sealed + schedule |
| Wiki ship fields (additive) | PARTIAL | `tools/import_wiki_ship_fields.py` / wiki API scripts |
| RSI pledge store prices | PARTIAL | CIC price-sweep brief existed; not a forever local automation yet |
| In-verse shop / craft chains over time | NEED | Fill gaps beyond UEX |
| scunpacked.com / scunpacked-data snapshots | PARTIAL | External fetchers + gates exist; keep on a patch cadence |
| Fleetyards models | PARTIAL | `sweep_model_availability` / `import_fleetyards_models` |

---

## D. Creator watchlist (non-verbatim claims)
| Path | Status | Notes |
|---|---|---|
| Space Tomato | NEED | YT + Twitch |
| BoredGamer | NEED | Daily news / patch |
| SaltyMike | NEED | Critical/salty lens — deliberate, not noise |
| The AstroPub | NEED | Lore |
| Active in the Verse | NEED | New-backer / live |
| Subliminal | NEED | Ships / loadouts |
| Morphologis | NEED | Architecture / tours |
| SuperMacBrothers | NEED | Concise news |
| Farrister | NEED | Ships / flight (YT; Twitch not listed) |
| Cross-check graph (creators × CIG × game files) | NEED | Multi-source confidence |

Per video/stream file: entities, actions, numbers, patch stamp, stance (fact/opinion/speculation), evidence pointer — **no verbatim republish**.

---

## E. Bugs & workarounds
| Path | Status | Notes |
|---|---|---|
| CIG known-issues / patch bug lists | PARTIAL | Via patch/DevTracker paths once local RSI watcher lands |
| Live gameplay bugs (esp. Twitch) | NEED | Symptom, where/when, patch, workaround, still true? |
| Workarounds library | NEED | |

---

## F. Active orgs
| Path | Status | Notes |
|---|---|---|
| Day-to-day orgs (pirate, shipping, rescue, etc.) | NEED | Verify real ops; skip vanity/empty shells |

---

## G. Pipeline board
| Path | Status | Notes |
|---|---|---|
| Announced \| Teased \| Speculated | NEED | Ships/features; never mix columns |

---

## H. Historian / continuity
| Path | Status | Notes |
|---|---|---|
| Retired/replaced locations (e.g. Port Olisar → successor) | NEED | Verify names from sources |
| Discontinued pledges (e.g. Aurora Mk I store sunset vs Mk II) | NEED | Store vs in-game are separate questions |
| “What used to be true” timeline | NEED | AI historian track |

---

## I. Lore / languages / SQ42
| Path | Status | Notes |
|---|---|---|
| Alien languages + lore Discords | NEED | Glossaries, where to learn; credit communities |
| SQ42 cast / Hollywood credits | NEED | Spoiler-gated; high Owner interest |
| SQ42 trailer / dev signal track | NEED | Spoiler-gated |

---

## J. Fresh pillars
| Path | Status | Notes |
|---|---|---|
| Corporate / IP filings (trademarks, patents, companies) | NEED | |
| Canon outside client (novels, art books, soundtracks, credits) | NEED | |
| Engine / industry tech talks | NEED | |
| Diegetic in-world media (billboards, datapads, ads) | NEED | Without depending on broken collector — use other capture/text-asset paths |
| Player-science methods (procedures we re-run ourselves) | NEED | Copy methods, not third-party sites |

---

## K. Soft community leads
| Path | Status | Notes |
|---|---|---|
| Reddit lead scavenger | NEED | Rumor-tagged until verified |
| Full Star Citizen Wiki API sync | NEED | Archive/cross-check — **not** breaking-news (wiki lags editors) |

---

## L. SC Brain plumbing (makes “easy to get” real)
| Path | Status | Notes |
|---|---|---|
| One compiled SC Brain folder tree | HAVE | Root `sc-brain/` landed 2026-09-14; see README + INDEX |
| Index / ask surface over SC Brain | NEED | Required for done bar |
| Obsidian graph on SC Brain | PARTIAL | Vault on CC disk; SC Brain root not compiled |
| Local RSI watcher (Claude replacement) | PARTIAL | Built 2026-09-13 by Build: `rsi-watcher/` (no AI; `-check`; cards to `cig-firehose/`; wake marker only on change). LIVE/PTU build line READ from the roadmap board. DevTracker / Comm-Link / Patchbot NOT CONFIGURED - endpoints routed to Research, wired as config when verified. Scheduling: `setup_rsi_watcher_task.ps1`, Owner runs it. |
| citizen-collector | OUT | Not ready |

---

## Existing instruments to CALL (not clone)
- `roadmap-watcher/` (+ scheduled task)  
- P4K/CGA extractors + hardpoint transform/placement pipeline  
- `scripts/external_sources/*` (wiki, UEX, scunpacked)  
- `import_uex_*`, wiki import tools  
- Fleetyards sweep/import  
- patch-diff / weapon-diff builders  
- Spectrum seed watcher (expand later)  
- Inbox/roadmap scheduled-task pattern for new watchers  

**Do not call for acquisition:** citizen-collector (OUT), Claude RSI hourly (being shut down), Erkul/SPViewer scrapes, StarBreaker (unauthorized).

---

## Suggested execution order
1. **Local RSI watcher** (Claude sweep replacement) — Owner kills Claude side  
2. **SC Brain folder map + index** (easy-to-get unlock)  
3. LIVE/PTU auto extract on build change  
4. Creator watchlist claim pipeline  
5. Historian + pipeline board  
6. Bugs, orgs, lore/languages, SQ42 credits  
7. Fresh pillars + Reddit/wiki soft layers  
8. Full CIG social/video firehose + historical backfill  

---

## Related docs
- `docs/CONSTITUTION_god-mode-sc-intelligence-2026-09-13.md`  
- `docs/SC-BRAIN_named-subsystem-2026-09-14.md`  
- `claude/FINDING_the-rsi-watcher-pays-an-ai-to-do-a-diff-2026-09-09.md`  

**Amendment rule:** add paths under sections; changing done bar or tool-use rules needs a dated note.

## Map pack (2026-09-14)
Steps 2–8 flushed: docs/SC-BRAIN_acquisition-maps-steps-2-8-2026-09-14.md (copy under sc-brain/_meta/).

## Endpoint verification (2026-09-14)
DevTracker RSI HTML, Comm-Link wiki JSON, Patchbot JSON-LD — verified + manual -check green. Settings example: si-watcher/rsi-watcher-settings.example.json. Scheduled task **not** registered yet (Owner).
