# Citizen Compass — Project Handoff

**Purpose of this doc:** you're picking up work on this project with a different AI assistant. Paste/upload this whole document to them first so they have full context before you start.

---

## 1. What this project is

**Citizen Compass** is a free, community-made Star Citizen ship purchase reference — a single self-contained webpage listing every ship in the game (232 total), where to buy each one in-game with aUEC, its real-money pledge price, and a direct link to its official RSI store page where verified.

- **Live at:** https://citizencompass.netlify.app/
- **Current version:** v0.2.5
- **Tagline:** "Know where to buy, before you fly."
- **Not affiliated with CIG/RSI** — it carries the required unofficial-fan-site disclaimer per CIG's Fan Content Policy, with a link back to robertsspaceindustries.com.
- **Not for profit.** No ads, no monetization, ever (this is a hard rule under CIG's fan policy anyway — donations/ads count as "commercial use" and are prohibited).
- **Hosting:** Netlify Drop, free tier, claimed account. To push an update: drag the new `index.html`-renamed file onto the *same claimed site* (not a fresh drop) so the URL stays permanent.
- **File format:** HTML only. The Excel/xlsx version was retired — don't bring it back unless explicitly asked.

## 2. Who you're working with (the user)

- Goes by Sleven. Wants blunt, no-filler communication — see his stored preferences if your new AI has access to them; if not, the short version: direct, profanity-tolerant, hates repeated questions or confident guessing, wants accuracy over speed.
- This is a genuine passion project — loves Star Citizen, wants to give the community accurate info, explicitly does not want money from it.
- Long-term goal ("phase two") is a real companion app, but that's **currently deprioritized** — the mobile-friendly website already works well, so the priority right now is finishing and polishing the data before any app work starts.
- Has real testers: himself (phone + wife's computer), and a friend named Nash who tested on iPhone and confirmed readability + working links.

## 3. Current data snapshot

- **232 total ships.**
- **~179 are "confirmed in-game"** (green rows) — verified aUEC price + a specific in-game dealer location (Astro Armada/Area18, Crusader Showroom/Orison, New Deal/Lorville, Teach's/Levski, Buy & Fly/Ruin Station), sourced from starcitizen.tools' Purchasing Ships page and CStone's live terminal tracker (finder.cstone.space).
- **~53 are "pledge-only"** (orange rows) — split into two real sub-categories, both labeled clearly in the notes:
  - **"Concept."** — not flyable yet at all.
  - **"Flight-ready, no dealer."** — genuinely real, flyable ships (some user-confirmed as owned) that just don't have an in-game aUEC dealer selling them yet. This distinction matters — don't collapse it back into a single "concept" bucket.
- Every ship has a **Role/category** (Fighter, Cargo, Mining, Medical, Racing, Capital/Multi-crew, Support/Repair, Ground Vehicle, Touring/Luxury, Interdiction, Multi-role, Data, Exploration, Salvage, Bomber) — searchable in the page's search bar alongside ship names.
- **80 ships currently have verified direct buy-links** (ship name becomes clickable, goes straight to the real RSI Pledge Store product page). **152 ships still don't have one** — full list below.

## 4. THE CRITICAL RULE for buy-links — read this before doing anything

**Never add a URL to the sheet without independently verifying it's real.** RSI's store URL slugs are NOT predictable (e.g. the 100i lives at `/pledge/ships/origin-100/100i`, not `/pledge/ships/100i/100i`). A wrong/guessed URL is worse than no URL — it actively breaks trust at the exact moment someone's ready to spend real money.

**How to verify a URL is real:**
1. Fetch or search the exact URL.
2. Check the page **title** in the result. A real product page title looks like `"[Ship Name] - [Manufacturer] | Star Citizen Store"`. A broken/wrong URL falls back to a generic page titled `"Ships - Roberts Space Industries | Follow the development of Star Citizen and Squadron 42"` with no ship-specific content.
3. **Known gotcha:** if you're using a fetch tool that caches by URL, retrying a "broken" result can return the exact same stale cached response (same content, sometimes even the same session token) instead of a fresh check — this happened repeatedly in this project and caused ~27 real, valid URLs to get wrongly marked broken on a fetch tool, only confirmed valid when checked through a **search** tool instead, which apparently doesn't share the same cache. **If a fetch comes back "broken," try re-verifying through a web search for the exact URL before concluding it's actually dead.**
4. Only ships with a confirmed-real URL get added. Everything else stays as plain text (no link), no exceptions, no "close enough."

**Known real URL patterns observed so far (not guaranteed to generalize — verify anyway):**
- `/en/pledge/ships/{manufacturer-slug}/{Ship-Name}` — most common, e.g. `/en/pledge/ships/aegis-avenger/Avenger-Titan`
- `/en/pledge/ships/{simple-name}/{Ship-Name}` for single-model manufacturers, e.g. `/en/pledge/ships/carrack/Carrack`, `/en/pledge/ships/gladius/Gladius`
- `/en/pledge/Standalone-Ships/{Ship-Name}` — an alternate format that also works for many ships (found this as a valid fallback for Intrepid)
- Case doesn't seem to matter in the slug (both `ROC` and `roc` variants resolved to the same real page)
- Multi-word manufacturer families sometimes share one slug across several ships (e.g. all Aurora Mk I variants live under `/rsi-aurora/`, all X1 variants under `/x1/`)

## 5. Ships that already have verified links (don't re-verify these — just don't duplicate)

- Aegis Dynamics — Avenger Stalker: https://robertsspaceindustries.com/en/pledge/ships/aegis-avenger/Avenger-Stalker
- Aegis Dynamics — Avenger Titan: https://robertsspaceindustries.com/en/pledge/ships/aegis-avenger/Avenger-Titan
- Aegis Dynamics — Gladius: https://robertsspaceindustries.com/en/pledge/ships/gladius/Gladius
- Aegis Dynamics — Reclaimer: https://robertsspaceindustries.com/en/pledge/ships/reclaimer/Reclaimer
- Anvil Aerospace — Arrow: https://robertsspaceindustries.com/en/pledge/ships/anvil-arrow/Arrow
- Anvil Aerospace — Ballista: https://robertsspaceindustries.com/en/pledge/ships/anvil-ballista/Ballista
- Anvil Aerospace — C8R Pisces Rescue: https://robertsspaceindustries.com/en/pledge/ships/anvil-pisces/C8R-Pisces
- Anvil Aerospace — C8X Pisces Expedition: https://robertsspaceindustries.com/en/pledge/ships/anvil-pisces/C8X-Pisces-Expedition
- Anvil Aerospace — Carrack: https://robertsspaceindustries.com/en/pledge/ships/carrack/Carrack
- Anvil Aerospace — Centurion: https://robertsspaceindustries.com/en/pledge/ships/centurion/Centurion
- Anvil Aerospace — F7C Hornet Mk II: https://robertsspaceindustries.com/en/pledge/ships/anvil-hornet-mkii/F7C-Hornet-Mk-II
- Anvil Aerospace — Terrapin: https://robertsspaceindustries.com/en/pledge/ships/terrapin/Terrapin
- Argo Astronautics — ATLS: https://robertsspaceindustries.com/en/pledge/ships/atls/ATLS
- Argo Astronautics — ATLS GEO: https://robertsspaceindustries.com/en/pledge/ships/atls/ATLS-GEO
- Argo Astronautics — MOLE: https://robertsspaceindustries.com/en/pledge/ships/argo-mole/MOLE
- Argo Astronautics — MOTH: https://robertsspaceindustries.com/en/pledge/ships/moth/MOTH
- Argo Astronautics — RAFT: https://robertsspaceindustries.com/en/pledge/ships/raft/RAFT
- Consolidated Outland — Mustang Alpha: https://robertsspaceindustries.com/en/pledge/ships/mustang/Mustang-Alpha
- Consolidated Outland — Mustang Beta: https://robertsspaceindustries.com/en/pledge/ships/mustang/Mustang-Beta
- Consolidated Outland — Mustang Gamma: https://robertsspaceindustries.com/en/pledge/ships/mustang/Mustang-Gamma
- Consolidated Outland — Nomad: https://robertsspaceindustries.com/en/pledge/ships/nomad/Nomad
- Crusader Industries — C1 Spirit: https://robertsspaceindustries.com/en/pledge/ships/spirit/C1-Spirit
- Crusader Industries — Intrepid: https://robertsspaceindustries.com/en/pledge/Standalone-Ships/Intrepid
- Drake Interplanetary — Cutlass Black: https://robertsspaceindustries.com/en/pledge/ships/drake-cutlass/Cutlass-Black
- Drake Interplanetary — Cutter: https://robertsspaceindustries.com/en/pledge/ships/cutter/Cutter
- Drake Interplanetary — Cutter Scout: https://robertsspaceindustries.com/en/pledge/ships/cutter/Cutter-Scout
- Drake Interplanetary — Dragonfly: https://robertsspaceindustries.com/en/pledge/ships/drake-dragonfly/Dragonfly-Black
- Drake Interplanetary — Golem: https://robertsspaceindustries.com/en/pledge/ships/golem/Golem
- Drake Interplanetary — Golem OX: https://robertsspaceindustries.com/en/pledge/ships/golem/Golem-OX
- Drake Interplanetary — Mule: https://robertsspaceindustries.com/en/pledge/ships/mule/Mule
- Drake Interplanetary — Vulture: https://robertsspaceindustries.com/en/pledge/ships/drake-vulture/Vulture
- Gatac Manufacture — Syulen: https://robertsspaceindustries.com/en/pledge/ships/syulen/Syulen
- Grey's Market — Basher: https://robertsspaceindustries.com/en/pledge/ships/basher/Basher
- Grey's Market — Shiv: https://robertsspaceindustries.com/en/pledge/ships/shiv/Shiv
- Greycat Industrial — PTV: https://robertsspaceindustries.com/en/pledge/ships/ptv/PTV
- Greycat Industrial — ROC: https://robertsspaceindustries.com/en/pledge/ships/roc/ROC
- Greycat Industrial — ROC-DS: https://robertsspaceindustries.com/en/pledge/ships/roc/ROC-DS
- Greycat Industrial — STV: https://robertsspaceindustries.com/en/pledge/ships/stv/STV
- Greycat Industrial — UTV: https://robertsspaceindustries.com/en/pledge/ships/utv/UTV
- Kruger Intergalactic — L-21 Wolf: https://robertsspaceindustries.com/en/pledge/ships/wolf/L-21-Wolf
- MISC — Fortune: https://robertsspaceindustries.com/en/pledge/ships/fortune/Fortune
- MISC — Freelancer: https://robertsspaceindustries.com/en/pledge/ships/misc-freelancer/Freelancer
- MISC — Freelancer DUR: https://robertsspaceindustries.com/en/pledge/ships/misc-freelancer/Freelancer-DUR
- MISC — Freelancer MAX: https://robertsspaceindustries.com/en/pledge/ships/misc-freelancer/Freelancer-MAX
- MISC — Hull A: https://robertsspaceindustries.com/en/pledge/ships/hull/Hull-A
- MISC — Hull B: https://robertsspaceindustries.com/en/pledge/ships/hull/Hull-B
- MISC — Hull C: https://robertsspaceindustries.com/en/pledge/ships/hull/Hull-C
- MISC — Prospector: https://robertsspaceindustries.com/en/pledge/ships/misc-prospector/Prospector
- MISC — Reliant Kore: https://robertsspaceindustries.com/en/pledge/ships/reliant/Reliant-Kore
- Mirai — Fury: https://robertsspaceindustries.com/en/pledge/ships/fury/Fury
- Mirai — Fury LX: https://robertsspaceindustries.com/en/pledge/ships/fury/Fury-LX
- Mirai — Fury MX: https://robertsspaceindustries.com/en/pledge/ships/fury/Fury-MX
- Mirai — Pulse: https://robertsspaceindustries.com/en/pledge/ships/mirai-pulse/Pulse
- Mirai — Pulse LX: https://robertsspaceindustries.com/en/pledge/ships/mirai-pulse/Pulse-LX
- Origin Jumpworks — 100i: https://robertsspaceindustries.com/en/pledge/ships/origin-100/100i
- Origin Jumpworks — 125a: https://robertsspaceindustries.com/en/pledge/ships/origin-100/125a
- Origin Jumpworks — 135c: https://robertsspaceindustries.com/en/pledge/ships/origin-100/135c
- Origin Jumpworks — 300i: https://robertsspaceindustries.com/en/pledge/ships/origin-300/300i
- Origin Jumpworks — 315p: https://robertsspaceindustries.com/en/pledge/ships/origin-300/315p
- Origin Jumpworks — 325a: https://robertsspaceindustries.com/en/pledge/ships/origin-300/325a
- Origin Jumpworks — 350r: https://robertsspaceindustries.com/en/pledge/ships/origin-300/350r
- Origin Jumpworks — 400i: https://robertsspaceindustries.com/en/pledge/ships/400i/400i
- Origin Jumpworks — X1: https://robertsspaceindustries.com/en/pledge/ships/x1/X1
- Origin Jumpworks — X1 Force: https://robertsspaceindustries.com/en/pledge/ships/x1/X1-Force
- Roberts Space Industries — Aurora CL: https://robertsspaceindustries.com/en/pledge/ships/rsi-aurora/Aurora-Mk-I-CL
- Roberts Space Industries — Aurora ES: https://robertsspaceindustries.com/en/pledge/ships/rsi-aurora/Aurora-Mk-I-ES
- Roberts Space Industries — Aurora LN: https://robertsspaceindustries.com/en/pledge/ships/rsi-aurora/Aurora-Mk-I-LN
- Roberts Space Industries — Aurora LX: https://robertsspaceindustries.com/en/pledge/ships/rsi-aurora/Aurora-Mk-I-LX
- Roberts Space Industries — Aurora MR: https://robertsspaceindustries.com/en/pledge/ships/rsi-aurora/Aurora-Mk-I-MR
- Roberts Space Industries — Aurora Mk II: https://robertsspaceindustries.com/en/pledge/ships/aurora-mk-ii/Aurora-Mk-II
- Roberts Space Industries — Constellation Andromeda: https://robertsspaceindustries.com/en/pledge/ships/rsi-constellation/Constellation-Andromeda
- Roberts Space Industries — Constellation Aquila: https://robertsspaceindustries.com/en/pledge/ships/rsi-constellation/Constellation-Aquila
- Roberts Space Industries — Constellation Taurus: https://robertsspaceindustries.com/en/pledge/ships/rsi-constellation/Constellation-Taurus
- Roberts Space Industries — Hermes: https://robertsspaceindustries.com/en/pledge/ships/hermes/Hermes
- Roberts Space Industries — Mantis: https://robertsspaceindustries.com/en/pledge/ships/rsi-mantis/Mantis
- Roberts Space Industries — Polaris: https://robertsspaceindustries.com/en/pledge/ships/polaris/Polaris
- Roberts Space Industries — Salvation: https://robertsspaceindustries.com/en/pledge/ships/salvation/Salvation
- Roberts Space Industries — Ursa: https://robertsspaceindustries.com/en/pledge/ships/ursa/Ursa
- Tumbril Land Systems — Cyclone: https://robertsspaceindustries.com/en/pledge/ships/cyclone/Cyclone
- Tumbril Land Systems — Cyclone RN: https://robertsspaceindustries.com/en/pledge/ships/cyclone/Cyclone-RN


## 6. Ships still needing a verified buy-link (152 total)

Work through these. For each: search/fetch the likely URL, confirm the title matches the specific ship (not the generic fallback), and record `(Manufacturer, Ship Name) -> URL` for confirmed ones only.

- Aegis Dynamics — Avenger Titan Renegade
- Aegis Dynamics — Avenger Warlock
- Aegis Dynamics — Eclipse
- Aegis Dynamics — Gladius Valiant
- Aegis Dynamics — Hammerhead
- Aegis Dynamics — Idris-M
- Aegis Dynamics — Idris-P
- Aegis Dynamics — Javelin
- Aegis Dynamics — Redeemer
- Aegis Dynamics — Retaliator
- Aegis Dynamics — Sabre
- Aegis Dynamics — Sabre Comet
- Aegis Dynamics — Sabre Firebird
- Aegis Dynamics — Sabre Peregrine
- Aegis Dynamics — Tiburon
- Aegis Dynamics — Vanguard Harbinger
- Aegis Dynamics — Vanguard Hoplite
- Aegis Dynamics — Vanguard Sentinel
- Aegis Dynamics — Vanguard Warden
- Aegis Dynamics — Vulcan
- Anvil Aerospace — Asgard
- Anvil Aerospace — C8 Pisces
- Anvil Aerospace — Crucible
- Anvil Aerospace — F7C Hornet Mk I
- Anvil Aerospace — F7C Hornet Wildfire Mk I
- Anvil Aerospace — F7C-M Super Hornet Mk I
- Anvil Aerospace — F7C-R Hornet Tracker Mk I
- Anvil Aerospace — F7C-R Hornet Tracker Mk II
- Anvil Aerospace — F7C-S Hornet Ghost Mk I
- Anvil Aerospace — F7C-S Hornet Ghost Mk II
- Anvil Aerospace — F8C Lightning
- Anvil Aerospace — Gladiator
- Anvil Aerospace — Hawk
- Anvil Aerospace — Hurricane
- Anvil Aerospace — Legionnaire
- Anvil Aerospace — Liberator
- Anvil Aerospace — Nautilus
- Anvil Aerospace — Odin
- Anvil Aerospace — Paladin
- Anvil Aerospace — Spartan
- Anvil Aerospace — Terrapin Medic
- Anvil Aerospace — Valkyrie
- Aopoa — Khartu-al
- Aopoa — Nox
- Aopoa — San'tok.yai
- Argo Astronautics — CSV-FM
- Argo Astronautics — CSV-SM
- Argo Astronautics — MPUV Cargo
- Argo Astronautics — MPUV Personnel
- Argo Astronautics — MPUV Tractor
- Argo Astronautics — SRV
- Banu (Souli) — Defender
- Banu (Souli) — Merchantman
- Consolidated Outland — HoverQuad
- Consolidated Outland — Mustang Delta
- Consolidated Outland — Pioneer
- Crusader Industries — A1 Spirit
- Crusader Industries — A2 Hercules Starlifter
- Crusader Industries — Ares Inferno
- Crusader Industries — Ares Ion
- Crusader Industries — C2 Hercules Starlifter
- Crusader Industries — E1 Spirit
- Crusader Industries — Genesis Starliner
- Crusader Industries — M2 Hercules Starlifter
- Crusader Industries — Mercury Star Runner
- Drake Interplanetary — Buccaneer
- Drake Interplanetary — Caterpillar
- Drake Interplanetary — Clipper
- Drake Interplanetary — Corsair
- Drake Interplanetary — Cutlass Blue
- Drake Interplanetary — Cutlass Red
- Drake Interplanetary — Cutlass Steel
- Drake Interplanetary — Cutter Rambler
- Drake Interplanetary — Herald
- Drake Interplanetary — Ironclad
- Drake Interplanetary — Ironclad Assault
- Drake Interplanetary — Kraken
- Drake Interplanetary — Kraken Privateer
- Drake Interplanetary — Pitbull
- Esperia — Blade
- Esperia — Glaive
- Esperia — Prowler
- Esperia — Prowler Utility
- Esperia — Scythe
- Esperia — Stinger
- Esperia — Talon
- Esperia — Talon Shrike
- Gatac Manufacture — Railen
- Gatac Manufacture — Tyilui
- Greycat Industrial — MDC
- Greycat Industrial — MTC
- Kruger Intergalactic — L-22 Alpha Wolf
- Kruger Intergalactic — P-52 Merlin
- Kruger Intergalactic — P-72 Archimedes
- MISC — Endeavor
- MISC — Expanse
- MISC — Freelancer MIS
- MISC — Hull D
- MISC — Hull E
- MISC — Odyssey
- MISC — RAPTOR
- MISC — Reliant Mako
- MISC — Reliant Sen
- MISC — Reliant Tana
- MISC — Starfarer
- MISC — Starfarer Gemini
- MISC — Starlancer BLD
- MISC — Starlancer MAX
- MISC — Starlancer TAC
- MISC — Starlite
- Mirai — Guardian
- Mirai — Guardian MX
- Mirai — Guardian QI
- Mirai — Razor
- Mirai — Razor EX
- Mirai — Razor LX
- Origin Jumpworks — 600i Explorer
- Origin Jumpworks — 600i Touring
- Origin Jumpworks — 85X
- Origin Jumpworks — 890 Jump
- Origin Jumpworks — G12
- Origin Jumpworks — G12a
- Origin Jumpworks — G12r
- Origin Jumpworks — M50
- Origin Jumpworks — M80
- Origin Jumpworks — X1 Velocity
- Roberts Space Industries — Apollo Medivac
- Roberts Space Industries — Apollo Triage
- Roberts Space Industries — Arrastra
- Roberts Space Industries — Aurora SE
- Roberts Space Industries — Constellation Phoenix
- Roberts Space Industries — Galaxy
- Roberts Space Industries — Lynx
- Roberts Space Industries — Meteor
- Roberts Space Industries — Orion
- Roberts Space Industries — Perseus
- Roberts Space Industries — Scorpius
- Roberts Space Industries — Scorpius Antares
- Roberts Space Industries — Ursa Medivac
- Roberts Space Industries — Zeus Mk II CL
- Roberts Space Industries — Zeus Mk II ES
- Roberts Space Industries — Zeus Mk II MR
- Tumbril Land Systems — Cyclone AA
- Tumbril Land Systems — Cyclone MT
- Tumbril Land Systems — Cyclone RC
- Tumbril Land Systems — Cyclone TR
- Tumbril Land Systems — Nova Tank
- Tumbril Land Systems — Ranger CV
- Tumbril Land Systems — Ranger RC
- Tumbril Land Systems — Ranger TR
- Tumbril Land Systems — Storm
- Tumbril Land Systems — Storm AA

## 7. Known open issues / unresolved flags (worth knowing, not urgent)

- **Aegis Idris-P price conflict:** one source says $1,900, an older community snapshot says $1,500. Currently showing $1,900 with the conflict noted in the row, not silently resolved. If you find a definitive current source, update it — but flag the conflict either way rather than picking silently.
- **Mirai Guardian QI:** listed as its own purchasable ship ($260), but also separately seen described as a temporary bug-workaround loaner for the Mantis. Possibly both are true (different context). Unresolved, noted in its row.
- **5 pledge prices were found stale** against a direct screenshot of the live RSI store (Dragonfly, Golem, Mule, Vulture, Syulen) and corrected. That was from spot-checking just 8 ships. Given that hit rate, other older prices sourced from third-party aggregators (not the live store directly) may also have drifted — a systematic re-check against the live store would be valuable if you have appetite for it.
- **F8C Lightning and RAPTOR** are real ships but gated behind Concierge-tier spending / referral-program requirements respectively — included for completeness, flagged as "not a realistic buy target for most players" in their notes. Don't remove that caveat.

## 8. Versioning and process rules

- Version scheme is **0.x.y** — deliberately not 1.0 yet. 1.0 is reserved for an actual real "this is done" launch milestone, not routine updates. Keep incrementing 0.x.y for everything until told otherwise.
- **Every version bump needs a changelog note** describing what changed (see the version history embedded in the page's Legend & Sources section for the exact format/tone used so far).
- **After any data change:** re-verify total ship count is still 232 (unless you're intentionally adding a genuinely new ship), check for duplicate (manufacturer, ship) pairs, and confirm no row lost its price/dealer/role data. This project had a real bug once where dealer checkmarks silently overwrote price cells due to a column-index mistake — any time the table's column structure is touched, audit carefully before shipping.
- **Mobile matters.** A missing viewport meta tag once caused the whole page to render tiny on phones, not just the wide table (which is expected to need horizontal scrolling — that's fine and intentional. The rest of the page — header, nav, search box — should never need zooming).
- The search bar matches both ship name AND category/role — don't break that dual matching if you touch the search JS.

## 9. How to bring results back

Since a different AI session won't have access to the actual data files running this site, the practical workflow is:
1. Have the other AI verify URLs (or gather whatever other info you're after) and produce a clean list: `Manufacturer | Ship Name | URL` (or whatever the task is).
2. Bring that list back to this conversation.
3. I'll independently re-verify anything I haven't already confirmed myself before adding it to the real file — that's not distrust of the other AI, it's the same standard applied to everything in this project so far, including your own submitted URLs.

---
*Generated as a handoff snapshot at v0.2.5. If you're reading this significantly later, ask the current assistant to confirm the live version at citizencompass.netlify.app hasn't moved further ahead of what's described here.*
