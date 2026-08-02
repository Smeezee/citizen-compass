# Testing area — PTU patch notes now have their own link — 2026-08-02

Cowork session. Testing area only. `testing/_layer.html` and `testing/_deploy/index.html` updated. No repo code outside `testing/` touched.

## The defect

The version banner showed two tags — LIVE 4.9.0 and PTU 4.10.0 — wrapped in **one** anchor pointing at `https://robertsspaceindustries.com/en/patch-notes`.

**That index lists LIVE releases only.** Verified: 20 entries, Alpha 4.9 back to 3.24.0, no PTU among them. So clicking the PTU tag took a visitor to a page that did not contain what the tag named. Not a broken link — a link to the wrong thing, which is worse, because nothing signals the mistake.

## What was found about where PTU notes actually live

RSI publishes no PTU page on the patch-notes index or as a comm-link. PTU notes exist **only** as Spectrum threads in the Patch Notes channel, forum `190048`.

Two facts that decide the implementation:

1. **Thread slugs are not stable across builds.** Alpha 4.10 alone has at least five separate threads — builds 12311913, 12326622, 12335477, 12358556, 12368639 — at `…/star-citizen-alpha-4-10-ptu-patch-notes`, `-1`, `-2`, `-4`, `-5`. A link to any one of them is stale within days and there is no derivable pattern to chase. **So the link goes to the channel**, where the newest build is always the top thread.
2. **Spectrum is a client-rendered SPA.** A fetch of forum 190048 returns meta tags and no thread list. Irrelevant for a link — a real browser runs the JS — but it rules out scraping PTU notes server-side later without a headless browser. Recorded now so a future session does not rediscover it.

LIVE is the opposite case: per-release comm-link pages are stable once published — `https://robertsspaceindustries.com/comm-link/Patch-Notes/21245-Star-Citizen-Alpha-49` for 4.9 — but **the ID is assigned by RSI and cannot be derived from the version string.** So it has to be a lookup table.

## What was built

The banner's single anchor is replaced by two, each carrying its own tag:

- **LIVE tag** → `CC_PATCH.live[version]`, read from the DOM's own `.sc-live .sc-ver` text, falling back to the index when the version is unmapped.
- **PTU tag** → the Spectrum channel, with a title attribute saying the newest build is the top thread.

Config block is `CC_PATCH` at the top of the script. Adding a release is one line.

**The fallback is the point.** An unmapped version yields the index — less specific, never wrong. A stale table degrades to today's behaviour rather than to a wrong destination.

**Bails out rather than guessing.** If `.sc-tag.sc-live` or `.sc-tag.sc-ptu` is absent — the live page changed shape — `split()` returns false and the banner is left exactly as the live page rendered it. Only `<a>` elements are removed; anything else on the banner survives.

## Two things that broke on the way

**The "Star Citizen" label was inside the anchor being replaced.** Item 16 injected `.cc-scgame` into `.sc-banner a`. Replacing that anchor would have deleted the label, and the two blocks would have raced depending on which retry interval fired last. Fixed by moving the label onto `.sc-banner` itself as first child. Both blocks are idempotent and now converge on the same DOM regardless of order.

**`width:100%` did nothing on mobile.** `.sc-banner` is a flex row with no `flex-wrap`, so two 100%-width children just shared one line and ran off the right edge — measured at 390px, the second link ended at x=474 in a 390px viewport. Adding `flex-wrap:wrap` at ≤640px fixed it. Verified after: two full-width rows at y=291 and y=329, `scrollWidth` 390 against `innerWidth` 390 — no horizontal overflow.

*A width that a flex parent is free to ignore is not a width.* Same shape as the earlier lesson about checks that cannot fail.

## Verification

Headless, against the built deploy file, not against the source:

- Anchor count, `href`, `title`, tag text and label text read back from the DOM — both correct, LIVE resolving to the 4.9 comm-link rather than the fallback.
- Bounding boxes at 390, 820 and 1400px. No overlap at any width; stacked at 390, side by side above.
- `pageerror` listener attached for the whole run — zero errors.

**One verification bug worth recording:** the first run reported all-zero rects and looked like a layout failure. The real cause was the harness writing `localStorage.ccGate = 'apples'` when the gate stores `'1'` — so the page was still locked and every element measured zero. *A test that measures a hidden page reports plausible-looking numbers rather than failing.* Fixed the harness, not the layer.

## Maintenance this creates

`CC_PATCH.live` needs one line when a release goes LIVE. Currently mapped: 4.9.0 → comm-link 21245. When 4.10 goes LIVE its comm-link ID must be read off the patch-notes index — it cannot be computed.

If that maintenance is unwanted, deleting the `live` map entirely leaves LIVE pointing at the index, which is still correct for LIVE. The PTU link needs no maintenance at all.
