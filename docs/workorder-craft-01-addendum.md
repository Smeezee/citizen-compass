# ADDENDUM — WO-CRAFT-01

    id          WO-CRAFT-01-A
    raised by   C2, 2026-08-02, after reading docs/order-front-end-build.md
                and the 2026-08-02 handoff archive
    for         C1 -> Claude Code
    status      amends WO-CRAFT-01. Apply both together.

I wrote WO-CRAFT-01 without having read `docs/order-front-end-build.md` or the
other sessions' notes from tonight. Five things change. One is a constraint the
work order does not state at all.

---

## A1 — THE STATIC RULING APPLIES TO EVERYTHING IN WO-CRAFT-01

**Ruled 2026-08-02: static JSON, no FastAPI.** WO-CRAFT-01 does not mention it
and its wording ("1,597 pages", "37 pages") reads as page-per-file.

**File-count arithmetic against the 20,000 Cloudflare Workers cap:**

    already accounted for in the order
      7,728  UEX priced items
        823  shops
        316  ships
      -----
      8,867

    WO-CRAFT-01 adds
      1,597  blueprint pages
         37  material pages
      -----
      1,634

    total  10,501     headroom  ~9,500

**Crafting fits either way** — as discrete files or as client-rendered routes off
a bundled index. But two things must be stated rather than assumed:

1. **If crafting is built page-per-file, it consumes 1,634 of the ~11,000
   remaining slots.** That is fine now. It is not fine alongside any future
   page-per-*game-file*-item build — 21,849 + 10,501 is 32,350, well over.
2. **My earlier claim that component comparison "finally forces the FastAPI
   backend to serve something public" is ruled against.** Anything downstream of
   that assumption in my plans is void. The zero-runtime-dependency property is
   the reason, not the file count — and the file count would have flipped on a
   definition, which is exactly why it was not the basis.

**No change to the derivation tasks.** WO-1, WO-2 and WO-4 emit JSON under
`data-layer/processed/` and are indifferent to how it is served. WO-3 and WO-5
are the rendering tasks and inherit the static ruling.

---

## A2 — TWO "UNVERIFIED" FLAGS IN THE ORDER, BOTH NOW CLOSED

The order flags two of my numbers. Both measured directly this session.

**"90,121 labels" — correct, and so is the order's 63,375. Different sources.**

    63,375   scunpacked.com (source 2)  — identical across all three snapshots
                                          20260731T031754Z, 20260801T042157Z,
                                          20260801T171748Z
    90,121   scunpacked-data (source 1) — 20260801T204744Z/labels.json

Source 2 is the legacy 2022-11-16 capture; source 1 is the current git clone.
No conflict. **Every label figure I have quoted this session — the 910 `ui_CI*`
keybinding names, 5,805 `item_Desc_*`, 4,749 `item_Name_*`, 552
`items_commodities_*` — is from source 1 and stands.**

**"21,849 item files" — solved by C1, and the conflation was mine.** It is the
recursive file count of `items/` in source 1, identical in both snapshots
(same upstream commit `4764726`). I used it alongside UEX's 7,728 without
marking that they count different things: every item in the game files versus
only those with a price. Recorded, not disputed.

---

## A3 — CORRECTION TO MY OWN PLAN, WORTH STATING PLAINLY

`docs/workorder-front-end-build-plan.md` §8a says the three right-edge tabs were
"wiped twice by rebuilds" and that the build should re-emit them from a list.

**The LOADOUT tab was not wiped. C1 removed it deliberately on Sleven's
instruction.** Implementing §8a as I wrote it would have made that removal
impossible — the build would restore the tab after every rebuild, permanently
overriding a decision the owner had already made twice.

I diagnosed a deliberate act as a defect and proposed automation that would have
fought the owner. **§8a as written must not be implemented.** The order's
Correction 1 is right: the build should own a list Sleven controls, and the
layout question comes first.

**Current state, measured just now:**

    build_deploy.py           three copy steps present, exits 1 on missing source
    _layer.src.html           LOADOUT removed, documented at line 1040
                              "deliberately NOT wired yet"
    _layer.src.html:385       IDS array still lists 'cc-lo-tab' — DEAD REFERENCE
    testing/index.html        06:48  — STALE
    testing/_layer.html       07:19
    testing/_deploy/index.html 07:19

`testing/index.html` still carries the full LOADOUT tab —
`<a id="cc-lo-tab" class="cc-ui" href="loadout.html">LOADOUT</a>` at line 1900,
plus its CSS at 1872-1882 — which neither the source nor the deploy has.
**localhost and the deploy disagree.** Rebuild it, and drop `cc-lo-tab` from the
`IDS` array at line 385.

---

## A4 — TWO THINGS I ASKED FOR THAT ARE ALREADY DONE

**The `Loadout` array is confirmed across ships.** C1 sampled ten across
manufacturers, 10 of 10 carry the full schema. My "verify before building on it"
caveat in `claude/plan-crafting-build-from-data-on-hand.md` and the front-end
plan is **closed. Do not re-verify.**

**Ship identity is resolved** — `data-layer/ship_resolution.json`: 254 live
ships, 215 matched, 2 ambiguous, 37 with no game file, 6 tier variants, 95 game
files parked. **None of my plans reference it. They should — use it, do not
re-derive it.**

---

## A5 — WO-5 GAINS A CHEAP CHECK

The order's method — anchor on the trusted set, match outward, **classify the
residue rather than discard it** — applies directly to WO-5's missing mining
locations.

`SC/resources/resources.json` (557 records) contains `Kind: cave_harvestable`
entries. Still unopened. **It is the only candidate source for mining locations
found so far**, and mining locations are one of the four fenced-off slots on the
material page. Ten minutes, before WO-5 is called complete.

---

## UNCHANGED

Every acceptance number in WO-CRAFT-01 stands — they were measured against the
sealed snapshots and nothing in the order touches them. The FORBIDDEN list
stands. The five open items stand, minus the `Loadout`-array verification, which
A4 closes.
