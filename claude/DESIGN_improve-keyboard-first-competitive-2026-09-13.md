# DESIGN — improve Keyboard First (competitive pass) — 2026-09-13

From: Architecture / Design (Grok covering C1 + Design)
On: C3 mock `design/keybindings/keys.html` + `docs/DESIGN_the-easiest-keybinding-setup-2026-09-06.md` + `docs/CIC_survey-keybind-tools-and-the-gap-2026-09-06.md`
Status: propose improvements; do not replace C3 look.

## ELI10

Everyone else builds an **editor** (change a bind, export XML).
C3 already nailed the pretty keyboard.
Press-to-find is **table stakes** (Star Binder already has Finder).
**Our unfair win** is a **check-up / coach**: ships you fly, plain English actions, “this layout is awkward,” starter packs — data only Citizen Compass holds.

## Star Citizen tools (good / bad / steal)

| Tool | Good | Bad | Steal |
|---|---|---|---|
| **Star Binder** (starbinder.space) | Browser; search; **Finder** (press input → see actions); XML in/out; activation modes | Chromium quirks; some inputs missing; no judgment/teaching | Finder as requirement; keep export path clear |
| **Boxxy Binder** | Visual stick templates; stack devices; template editor; live deploy into installs; input debugger | Desktop-only; still an editor, not a coach | Side-by-side list + device picture; bind from the picture |
| **HCS Keybind Editor** | Search; combos; backup/restore; premium sticks | Free tier keyboard-heavy; paid wall for full stick | Backup before wipe; combo clarity |
| **SC Profile Editor** | Themes; GUID device match; PDF templates | Another editor | Reliable device identity (GUID), printable card |
| **Joystick Diagrams** | Hardware-accurate **printable** cards; multi-game | Read-only (no edit) | “Print my stick card” export |
| **In-game SC options** | Source of truth | Slow, nested, silent conflicts | Never compete on raw nested lists |

## Outside SC (good / bad / steal)

| Tool | Domain | Steal |
|---|---|---|
| **Steam Input** | Layers / action sets / radial menus | **Modes**: Flight vs On-foot vs EVA as layers, not 691 flat rows |
| **reWASD** | Deep remap, activators, hold-for-layer | Hold-to-shift layer for “combat set” without leaving the page |
| **AntiMicroX / JoyToKey** | Simple pad→key | Keep simple path for pad users; don’t force HOTAS UX on them |
| **DCS / ED culture** | Per-ship / per-module binds | **Bind for the ship you fly** (we have the fleet DB) |
| **Joystick Diagrams** (again) | Reference cards | Same — glanceable physical map |

## What Keyboard First already does well (keep)

- Looks like real keys (dopamine + clarity)
- Dark CC visual language
- Sticky control strip + search
- Device-segment vibe (flight/foot colors in CSS)

## Gaps vs best of breed (fix these)

1. **Coach, not only editor** — conflict / awkward-reach / unused binds / ship-relevant actions
2. **Modes/layers** — Steam-style Flight | FPS | Vehicle (not one endless list)
3. **Stick picture path** — Boxxy-style device face for HOTAS (keyboard board stays king for MKB)
4. **Plain English** — we hold labels; put them on the key/detail panel
5. **Ship check-up** — “you fly Gladius — these 12 combat binds unbound”
6. **Printable / share card** — Joystick Diagrams energy for sticks; our share-card muscle for “my layout”
7. **Small screens** — patched 2026-09-13 (scroll, don’t smash)

## Ranked improvements (preserve C3 look)

### P0 — before / with P15 stamp+link
1. **Modes chips** on the strip: Flight / On-foot / Vehicles / EVA (filter the board + search)
2. **Detail panel** when a key is selected: plain-English action, category, “also bound on…”
3. **Conflict badge** on keys with >1 action or silent steal risk
4. Keep **Finder** (press to highlight) — required, not the slogan

### P1 — next pass
5. **Ship check-up** drawer using Compass fleet data (our moat)
6. **Starter pack** “40 that matter” applied as a guided set (opinionated)
7. Stick/pad **face templates** for common HOTAS (or deep-link to printable export)

### P2 — later
8. Live deploy (Boxxy-class) — only if Owner wants desktop helper
9. Usage learning from collector — privacy-sensitive, Owner machine only

## Do NOT copy

- Building “yet another XML editor” as the product story
- Claiming press-to-find as unique
- HID-button-number identity for stick controls (Architecture ruled against)
- Smashing the keyboard on narrow screens

## Sources
- docs/CIC_survey-keybind-tools-and-the-gap-2026-09-06.md (C3)
- https://starbinder.space/
- https://github.com/BoxximusPrime/Boxxy-Binder
- https://github.com/Rexeh/joystick-diagrams
- https://www.hcsvoicepacks.com/ (HCS editors)
- https://github.com/Osiris-DevWorks/sc-profile-editor
- https://www.rewasd.com/ ; Steam Input action layers

*Grok (Design / Architecture cover), 2026-09-13.*