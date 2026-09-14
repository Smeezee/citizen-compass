# Build update - P15 decision (b): hold stamp and link; regenerate keybinds_site.json with the nested bindings first. Reading the page's format before any write

**Code (Build), 2026-09-13. Clock read at 18:56:59.** Sleven's message: "go". Tray listed: `2026-09-13_memo_build_p15-hold-link-go-fix-nested-bindings.md` (18:48), and the answer on my stop memo (`88558d9`).

**The order, in order:**
1. regenerate `data-layer/processed/keybinds_site.json` to include the child-element bindings and the `activationmode` spelling
2. re-run the derived compare
3. when it is clean, the verified stamp plus the link, as ordered before
4. STOP with a receipt

**Never ship the incomplete stamp.**

**DELEGATION (`OWNERS.md`):** Architecture names `keybinds_site.json`, `build_kb_actions.py` and `extract_default_profile.py` (all C1's; "sitting exception while Grok covers C1"), and states the change. The earlier P15 delegation stands: the `keybinds.src.html` marker, the `build_deploy.py` fill, and one `next.src.html` link.

**Why reading comes first:**
- **Nothing in the repository produces `keybinds_site.json` from a profile.** It was hand-built on 08-05, labels, descriptions and groups included, and those come from outside the profile. So a "regenerate" has to keep those fields and take every binding from the profile.
- **Some of the 58 may not fit the page's format at all:**
  - a device with TWO inputs (for example `flashui_down` on the gamepad: `dpad_down` and `thumbr_down`)
  - per-device activation modes in child elements, where the page has one per action
- **If the format cannot hold them, that is a page-format decision,** and it comes back to Architecture rather than being guessed.

**Now, read-only:**
- how `build_kb_actions.py` and the page consume each field
- existing separator conventions in the values
- the 58 broken down by shape
