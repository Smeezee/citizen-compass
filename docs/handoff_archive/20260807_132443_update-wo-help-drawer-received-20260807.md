# Update — HELP drawer work order received (2026-08-07)

**Received:** build the HELP drawer on the keybind page, driven by
`data-layer/processed/keybind_troubleshooting.json` (17-node branching graph)
and `data-layer/processed/vendor_support.json` (5 vendors, matched on USB
vendor ID alone).

**First question answered before building — existing drawer behaviour:**

Every existing drawer in `testing/_src/_layer.src.html` **overlays**. None of
them reflow page content. Evidence:

- `#cc-panel` (DISPLAY) — `position:fixed; right:-380px; width:380px; z-index:100001`
- `#cc-mdraw` (manufacturer) — `position:fixed; left:-250px; width:250px; z-index:99998`
- `#cc-fb` (FEEDBACK) — `position:fixed; inset:0`, a full-screen modal scrim
- `#cc-kb` (KEYBINDS) — `position:fixed; inset:0 0 0 46px`, a full-screen takeover

The `translateX(-380px)` rules Sleven found on `#cc-fb-tab` / `#cc-kb-tab` /
`#cc-fi-tab`, and `left:296px` on `#cc-mtab`, move **tab furniture only** — so
the tabs are not buried under the panel that just slid over them. A grep for
any content-region resize (`margin-right`, `padding-right:380`,
`width:calc(100% - …)` under `body.cc-drawer-open`) returns nothing.

**So: shrink-the-page is NEW behaviour, not reuse.** Bolting a reflow onto the
existing `body.cc-drawer-open` class would fight the pattern — that class is
currently understood by three tabs to mean "get out of the way", and repurposing
it to also mean "resize content" would make the DISPLAY and FEEDBACK drawers
start reflowing the page too. The HELP drawer gets its own class and its own
mechanism, and the existing drawers are left alone.

**Trap noted before building:** `keybinds.src.html` is *copied verbatim* to
`keybinds.html` by `build_deploy.py` (it is in `PAGES`), so the model/thumbnail
substitution list does not apply to it. The trap that *does* apply is
`inject_engine.py`, which overwrites everything between the DEVICE PANEL rev 2
boundary markers in that file on every build. Any vendor-ID code placed inside
that region would be silently discarded. Also: `check_deploy_clean.enforce`
allows only `index.html` plus the `PAGES` outputs, so new sidecar files would
fail the deploy guard — the JSON will be inlined rather than fetched.

**Next:** build it, then verify against the deployed page, not the source.
