# WORK ORDER — move the edge tabs to the bottom

    id       WO-TABS-01
    from     C2, 2026-08-02
    for      C1 -> Claude Code
    ruling   Sleven: put them along the bottom, icons for tools
    size     small. CSS only. The bottom layout is already written.

---

## 1. THE GOOD NEWS — this is not new work

**The bottom arrangement already exists in the source.** It is written, it works
(Sleven's screenshot shows it), and it is only gated behind a screen-width
condition.

Read from `testing/_src/_layer.src.html`, 139,649 bytes, 2026-08-02 20:10:

    line  956   #cc-kb-tab{position:fixed;top:calc(44% + 290px);right:0; ...}
    line  963   @media (max-width:820px){
    line  964     #cc-kb-tab{top:auto !important;bottom:10px;right:124px;
                    writing-mode:horizontal-tb;padding:11px 14px;border-radius:7px}

    line 1684   #cc-fi-tab{position:fixed;top:calc(44% + 570px);right:0; ...}
    line 1691   @media (max-width:820px){
    line 1692     #cc-fi-tab{top:auto !important;bottom:10px;right:376px; ...}

**The change is to stop gating it**, not to write it.

---

## 2. CURRENT STATE — measured, not assumed

**Right edge, top to bottom:**

| id | label | position | colour |
|---|---|---|---|
| `#cc-tab` | DISPLAY | `top:44%` (absolute, in a container) | `#00C9A7` |
| `#cc-fb-tab` | FEEDBACK | `top:calc(44% + 150px)` | `#FF6B00` |
| `#cc-kb-tab` | KEYBINDS | `top:calc(44% + 290px)` | `#00C9A7` |
| `#cc-fi-tab` | FIND IT | `top:calc(44% + 570px)` | `#FFC24D` |

**Left edge:** `#cc-mtab` MANUFACTURERS — `left:46px; top:44%`

**Three defects visible in that table:**

1. **There is a 140px hole at +430px** where LOADOUT used to sit. FIND IT is
   still at +570 as though the gap were filled. **Close it or the spacing is
   wrong however this is resolved.**
2. **Only KEYBINDS and FIND IT have a bottom rule.** DISPLAY and FEEDBACK have
   none — so on a narrow window two tabs move to the bottom and two stay on the
   right. **That is the inconsistency in Sleven's screenshot.**
3. **`#cc-lo-tab` is still listed in the `IDS` array at line 385** though the
   element is gone. Dead reference. Remove it.

**The LOADOUT removal is correct and documented** — the source comment reads
*"loadout.src.html and its PAGES copy step are deliberately untouched — the page
stays reachable, only the floating tab is gone."* **Do not restore it.**

---

## 3. THE CHANGE

**3a. Make the bottom layout unconditional.** Move the rules currently inside
`@media (max-width:820px)` out of the media query so they apply at every width.

**3b. Give `#cc-tab` and `#cc-fb-tab` the same treatment**, so all four sit on
the bottom bar together. `#cc-tab` is `position:absolute` inside a container and
will need converting to `position:fixed` like the other three.

**3c. Space them evenly rather than at the current hard-coded 124px / 376px.**
Those numbers assume two tabs. With four, use a flex row container rather than
four fixed `right:` values — adding a fifth then costs nothing, which was the
original complaint.

**3d. Icons for tools, words for pages** (Sleven's ruling). The bottom already
carries the site's own nav — *Ship Purchase Matrix · Development Progress · Sale
Calendar · Legend & Sources*. Those keep their words. DISPLAY, FEEDBACK,
KEYBINDS and FIND IT become icons with the name on hover and an `aria-label`.

**MANUFACTURERS on the left edge is a separate question — leave it alone in this
order.** Sleven has not ruled on it.

---

## 4. THE COMPLIANCE RISK — check this before shipping

**The Fan Kit disclaimer is a fixed bar at the bottom of the page.** From line
~948:

    background:rgba(6,12,20,.95);border-top:1px solid rgba(0,201,167,.22);
    ... pointer-events:none;z-index:6
    #cc-grid{padding-bottom:36px}

**It sits at `z-index:6`. The tabs sit at `z-index:100002` and `bottom:10px`.**
A bottom tab row will land on top of the disclaimer.

**This already happened once** — the ship overlay covered the disclaimer and had
to be fixed on 2026-08-02 with `#cc-ship::after` plus the 36px padding.

**Required:** the disclaimer must remain fully visible with the bottom bar
present. Either sit the tabs above it, or increase `#cc-grid`'s bottom padding
to clear both. **This is a Fan Kit Agreement requirement, not a design
preference.**

---

## 5. VERIFICATION — HARD RULE 12

- **Assert all four tabs are visible and clickable at 1920×1080**, which is where
  FIND IT currently starts at 1045px on a 1080px viewport and is unreachable.
- **Assert the disclaimer text is fully visible** with the bar present, at
  1920×1080 and at 1366×768.
- **Assert the same four are visible on a phone viewport** — 390×844 — without
  colliding with the site's own nav row.
- **Assert `cc-lo-tab` appears nowhere**, including the `IDS` array at line 385.
- **Assert adding a fifth tab needs one list entry and no repositioning.** That
  is the actual point of the change.

---

## 6. NOT VERIFIED

- **Whether `testing/index.html` is still stale.** It was 2026-08-02 08:48
  against 20:10 for the source and the deploy — **12 hours behind. Rebuild it.**
- **What breakpoint Sleven's screenshot was taken at.** The bottom layout appears,
  so the window was at or under 820px wide, or zoomed. Not measured.
- **Whether the site's own bottom nav is fixed or scrolls with the page.** It
  matters for stacking and was not checked.
- **Whether MANUFACTURERS on the left edge has the same off-screen problem.** It
  is at `top:44%` with no bottom rule, so probably not, but it was not tested.
