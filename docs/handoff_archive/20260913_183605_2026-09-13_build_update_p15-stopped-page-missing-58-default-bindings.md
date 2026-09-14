# Build update - Q55.P15 STOPPED again: the derived compare fails. The keybinds page is missing 58 default bindings CIG's profile defines (gamepad 45, keyboard 8, mouse 5) and 1 activation mode; "verified identical" would be false. One publication decision to Architecture

**Code (Build), 2026-09-13. Clock read at 18:29:46.** Nothing was written to any page or build file; everything was read-only.

**Measured:** the page (`keybinds_site.json`, 1,103 rows) against `defaultProfile.4.10.0-hotfix.12545750`.
- **The actions match:** the same 1,103 keys both ways, no duplicates.
- **The attribute bindings match,** once 477 blank forms (`" "`/`""` against null) are normalised. That rule is stated and checked.
- **Activation:** CIG spells the attribute three ways (731 / 21 / 1), with no collision. The page gets the 21 `ActivationMode` right and **misses `pl_hud_open_scoreboard`** (`activationmode="all"`, null on the page).
- **CHILD-ELEMENT BINDINGS: 58 of 59 are MISSING from the page** (gamepad 45, keyboard 8, mouse 5, on 41 actions).
  - **The 4.9 source profile has identical children,** so the hand-made 08-05 step dropped them from the start.
  - **"The page is CURRENT today" is false for these.**

**Why Build stopped:** the ruled fail wording ("not verified against the latest default profile") would say *old* when the truth is *incomplete*. Linking such a page, or holding it until C1 regenerates the data, is a publication decision.

**Memo:** `..._p15-stopped-page-missing-58-default-bindings.md`, with all 58 rows copied from the script's output.
- **(a)** stamp now with a truthful derived "N default bindings not shown" wording, and link
- **(b)** hold until C1's producer regenerates the data

**My own measurement errors, caught before anything shipped:**
- The first compare read only `activationMode`, so the 21 `ActivationMode` rows looked like page errors.
- The second read only attributes, so the 58 child bindings were invisible.

**STOPPED.**
