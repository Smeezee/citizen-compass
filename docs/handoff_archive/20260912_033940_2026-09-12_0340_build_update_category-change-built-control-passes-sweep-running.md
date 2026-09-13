# Build update - the category change is built and its control passes; the sweep is running alone

**Code (Build), 2026-09-12. The chain ran 03:38:04 to 03:38:26 CDT, and the control ran at 03:38:55.**

**The order:** Architecture's build order, `2026-09-12_memo_build_your-three-answers-the-clearing-is-released-and-one-new-job.md`, section 1. **That order is the delegation for the three C1-owned files touched.**

## What changed

**`build_frontpage_data.py`** (C1's):

- It joins RSI's roles file on the exact site name, and refuses if the file is missing or contains a duplicate name.
- Each row gains:
  - `rrole` - RSI's role, verbatim
  - `cat` - RSI's first segment, with only two merges: Transport becomes Transporter, and Multi-role becomes Multi-Role
  - `cat_src` - `rsi`, `ours` or none
- **The result:** 225 rows from RSI, 24 ours, and 5 with none.

**`tools/frontpage/build_next_frontpage.py`** (C1's):

- The chips, the filter, the search and the suggestions now use the category.
- Search also matches RSI's exact role string.
- **One source line sits under the chip bar:** "Categories from RSI's published ship roles." It is hidden on the other tabs.
- It refuses data that predates this change.

**`testing/_src/build_deploy.py`** (mine):

- The category and its source reach the ship page through `LOADOUT_INFO`, by record id. There is no second name join.
- It refuses stale data, and it refuses a join that carried nothing.
- **197 ship pages get RSI's role, and 24 get ours.**

**`testing/_src/loadout.src.html`** (C1's) gains one Category row on the ship page:

- RSI's exact role, marked "RSI's published ship role", **or**
- the career, marked "our own category, from game data - no RSI role joined for this ship".

## The result on the built page

- **10 chips:** Combat, Transporter, Exploration, Industrial, Competition, Support, Ground, Multi-Role, Starter and Destroyer.
- **Gone:** Gunship and Snub Fighter. Paladin and Pitbull now sit under Combat, which is RSI's first segment for both.
- **Uncategorised cards: 34 before, 4 now** - CSV-FM, Genesis Starliner, RAPTOR and Starlancer BLD.

## The new control

`checks/_verify_category_source.py`, `RULE16: INDEPENDENT`.

- It recomputes every card's category from the roles file and the career, and compares that with what ships.
- **PASS on the real data.**
- **All 5 planted mutations were caught.** Each run plants them.
- The sweep discovers it automatically.

## In flight

**The solo sweep.** If it is green, deploy, then check on the served site, with a check that is first proven to fail against the current live site.
