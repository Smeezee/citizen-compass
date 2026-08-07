# HANDOVER TO C1 — everything ready to execute, in order

    from     C2 (Cowork), 2026-08-05
    to       C1 -> Claude Code
    scope    six work orders, ordered. Nothing here is half-finished.
    state    machine live in Minnesota. HEAD == origin/main == 5cda5d1.

**Read `inbox/update_session_c2_20260805_full.md` first** — it is the session
record and it carries the findings these orders rest on.

---

## READ BEFORE TOUCHING ANYTHING

**1. Do not `git add -A`.** 50 files are pure CRLF line-ending churn — 191,317
insertions against 191,317 deletions, identical counts, 11 of 12 sampled files
byte-identical after stripping CR. **`releases/latest.html` and
`static/preview.html` are in that list.** Settle the line endings separately
before any sweep commit.

**2. Mount mtimes are not reliable.** C2 misread `testing/index.html` as stale
from a file date read through the Cowork mount. **Judge currency by rebuild and
hash, not by timestamp.** `testing/index.html` specifically cannot be
byte-verified — `build.py:26` injects a UTC timestamp on every run.

**3. `blueprint_index.json` is 10.91 MB.** Claude Code flagged this against the
static ruling. **It must be sharded before WO-3 builds 1,597 pages that each
fetch it.** Cause is the `sources[]` arrays — up to 127 contracts per blueprint.

---

## THE ORDER

### 0 — RULE 14 ENFORCEMENT (not a C2 order, but it goes first)

`docs/proposal-rule14-single-writer-enforcement.md` — written and committed,
**not implemented**, deliberately. C1's own closing note calls it "the right
first thing to pick up, and a clean starting point rather than a half-finished
one." **C2 agrees. Do this before adding new writers to anything.**

### 1 — WO-BACKUP-01 · `inbox/workorder-backup-01-external-drive.md`

**Time-sensitive: the WD MyBook is attached now.**

`Backup-CitizenCompass.ps1` already exists and is thorough — free-space checks,
HEAD capture, `git fsck` judged by exit code, robocopy without `/MIR`, and **a
real database restore into a throwaway DB with a ship count.** Do not write a new
one.

**Two things the order insists on:** read the log from the **2026-07-30 run that
failed with exit code 1 and was never diagnosed**, and **include
`data-layer\external-sources`** — the script excludes it as "re-pullable" but
re-pulling UEX gives today's prices, not 2026-08-01's. Those snapshots are the
start of the historical record.

**Closes the largest standing risk:** `.env`, three secrets, one machine, no copy.

### 2 — WO-DEVICE-01 rev 2 · `inbox/workorder-device-01-rev2.md`

**D1 is the only actual defect in the whole handover.** `keybinds.src.html`
line 689: any axis moving >0.015 calls `renderDevice()`, which rebuilds the panel
via `innerHTML` — 256 button tiles across two devices, potentially every frame.
**Build the DOM once, then mutate. No `innerHTML` after first render.**

Then D4 layout (both sticks visible, unused buttons collapsed), D2 hats
(`hat1_up/down/left/right`, the sevenths classifier, circle widget), D3 data
model (**one control can be an axis AND a button**), D5 guided mapping.

### 3 — WO-TABS-01 · `inbox/workorder-tabs-01-bottom-bar.md`

**Sleven has ruled: bottom bar, icons for tools, words for pages.**

**The bottom CSS already exists** inside `@media (max-width:820px)` at
`_layer.src.html` lines 963 and 1691. **The change is to stop gating it**, extend
it to `#cc-tab` and `#cc-fb-tab`, and replace the hard-coded `right:` offsets
with a flex row so a fifth tab costs one list entry.

**Compliance check, not optional:** the Fan Kit disclaimer is a fixed bar at
`z-index:6`; the tabs sit at `z-index:100002`, `bottom:10px`. **A bottom bar will
cover it.** It has been broken once already.

### 4 — WO-KEYBIND-01 (+A) · `inbox/workorder-keybind-01-extraction-done.md`

**The blocker is gone.** `defaultProfile.xml` is extracted and joined. **Two
files are in `Downloads\` and need moving into the repo — C2 cannot write there.**

    Downloads\defaultProfile.plain.xml    218,387 bytes
    Downloads\keybinds_site.json          311,854 bytes

Replace the invented data in `keybinds.src.html`. The extraction method is in the
order and **must be re-run every patch.**

**Correction to carry:** the useful-description count is **86**, not 130, not
210, not 674. See `inbox/update_session_c2_20260805_full.md` §2.

### 5 — WO-CRAFT-01 + addendum · already in `docs/`

WO-1 and WO-2 are **complete and passing**, including C2's three unverified
numbers (768 / 676 / 127 — all confirmed). **WO-3 onward remains**, gated on the
10.91 MB sharding decision above.

**Hold in force:** do not render `stdItem.DescriptionText` verbatim to any page.
`WO-CRAFT-01-B` — the rights question is parked by Sleven, deliberately, until
much later. **WO-2 through WO-5 are unaffected**; blueprints, ingredients,
contracts and prices are facts and numbers throughout.

---

## PARKED BY SLEVEN — do not raise

- **The RSI legal enquiry on description rights.** Parked deliberately. Focus is
  build and test.
- **Contacting CmdrQuattro or other tool maintainers.** Revisit only after
  commodity prices land.
- **The site-wide design system** (`claude/plan-design-system.md`) — proposal
  filed, no ruling yet. **Tokens and retype are worth doing before Build A ships
  so new pages are born right, but that is Sleven's call.**

---

## WAITING ON SLEVEN, NOT ON C1

    the in-game kiosk / r_DisplayInfo test    gates the whole capture workstream
    modifier export format test               5 min, blocks part of the keybind export
    the tab layout is RULED - see order 3     no longer blocking
    UEX token + Cloudflare token rotation     both exposed, both unrotated
    UEX commodity prices pull                 biggest single data unlock remaining

---

## THE FULL LIST OF C2 DOCS THIS SESSION

On claude.ai, for reasoning rather than execution:

    plan-design-system                   full visual proposal
    plan-site-visual-upgrade             the display-engine route
    plan-keybind-newplayer               two products, export format confirmed
    plan-writing-keybind-descriptions    the 605 -> 75 scope cut
    finding-keybind-descriptions-closed  the 464, closed with evidence
    workorder-keybind-extraction         + the defaultactions.xml addendum
    workorder-device-visual-map          rev 2
