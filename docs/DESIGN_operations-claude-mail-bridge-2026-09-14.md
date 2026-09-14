# DESIGN — Operations desk ↔ Claude Code mail (automated)
**Date:** 2026-09-14  
**Status:** IMPLEMENTED 2026-09-14. Desk rename map still waiting.

## Goal
Claude Code and the Operations agent (ex-“Grok”) talk **through the Mailroom** with no human ferry and no Just Talk in the middle.

## Why disk mail (not chat ping to Claude)
Claude Code is not a Grok Bot agent. It cannot receive `SendToAgent`.  
Citizen Compass **Mailroom** is already how Claude desks pass letters. Keep that as the wire.

## Shape
```
Claude Code  --writes-->  correspondence/open/<desk>/
        ^                         |
        |                         v
   reads reply              Operations agent
   from answered/           (routine wake)
   or open tray             processes + writes reply letter
```

## Operations agent duties (C1 / Architecture hat)
- Own Architecture stamps / collisions / accept-reject (per C1 boot intent)
- **Auto-check** `correspondence/open/architecture` (and any tray Operations owns) on a short cadence
- On new mail: read → act or stamp → write reply into the mail system Claude already reads
- Tiny handoffs; durable proof stays in mail + SC Brain
- Does **not** do Engineering builds or Intelligence gathering

## Automation pieces
1. **Re-role agent** — name/description → Operations (C1/Architecture); boot from short living files  
2. **Routine on Operations** — poll open Architecture (and related) trays; process new letters; no quiet-hour AI burn on empty trays beyond a cheap scan  
3. **Claude Code side** — unchanged postal habit: file letters, read replies from trays  
4. **Optional later** — watcher-go hook that pings Operations only when a new Architecture letter lands (even less polling)

## Degradation note
Each auto-wake adds to Operations’ chat. Acceptable. Mitigate: short boots, mail+SC Brain hold truth, fresh thread same agent when mushy.

## Non-colliding
Do not touch `rsi-watcher/` while Engineering owns it.  
Do not rename mail desk folders until Owner freezes the plain-English map.

## Done when
Claude Code can drop Architecture mail and get an Operations reply **without** Owner or Just Talk copying anything by hand.

---

## Anti-runaway / credit guards (Owner 2026-09-14)
Required before the poll routine is considered safe:

1. **State file** — track processed letter paths/hashes (`sc-brain/ops/` or `correspondence/_ops_state/`). Never re-open a letter already handled.
2. **Empty tray = silence** — no user ping, no reply letter, no “still nothing” noise. Exit immediately.
3. **Cadence** — weekday daytime poll, coarse (e.g. every 15–30 min in work window), **not** sub-5-minute thrash. Prefer later: watcher ping-on-new-mail only.
4. **Cap per wake** — max N new letters (e.g. 3). Rest wait for next cycle.
5. **One reply per letter** — no back-and-forth loops in one wake unless the letter explicitly requests multi-step and a stop condition is named.
6. **No self-mail storms** — never write a letter that will re-trigger the same tray without a new Claude/Owner input.
7. **Collision line** — do not touch `rsi-watcher/` or other Engineering-owned open work.
8. **Chat wipe OK** — session history disposable; durable truth is mail + SC Brain + BOOT/HIGHLIGHTS only.

## Program notification (fine-tune through the house)
When Operations mail-bridge goes live, record once in:
- `BOOT.md` / `HIGHLIGHTS` card — Architecture seat = Operations agent; Claude Code ↔ Operations via Mailroom
- This design file status → IMPLEMENTED with date
- Optional short memo to open trays: “Architecture replies now come from Operations desk (Grok Bot); keep using correspondence folders”

So every desk knows the path changed and where the record lives if something breaks.

## Routine status
**ROUTINE CREATED:** 2026-09-14 — Operations agent, cron `*/20 9-18 * * 1-5` (weekdays 9–18 local, every 20m). State: `correspondence/_ops_state/`. Status still DESIGN until first successful live cycle stamps IMPLEMENTED.

IMPLEMENTED: 2026-09-14 — first live mail-bridge cycle on Operations (3 Architecture letters stamped). State: `correspondence/_ops_state/processed_letters.json`. Routine: operations-code-architecture-mail-bridge.
