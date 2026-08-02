# Testing area — PTU banner now links the actual thread, with a gate that refuses stale — 2026-08-02

Cowork session. Testing area only. `testing/_layer.html` and `testing/_deploy/index.html` updated. Supersedes the channel-only link filed earlier today in `update_ptu_patch_link.md`.

## What changed and why

The earlier fix pointed the PTU tag at the Spectrum Patch Notes channel rather than at a thread, on the grounds that thread slugs churn per build. The owner's requirement is stronger: **a direct link, accepting that something has to keep it current.**

That is now built, plus the part that makes a direct link safe to ship.

## The finding that changes the picture

Spectrum is a client-rendered SPA — the channel page returns no thread list to a plain GET. That is why the earlier note said direct links could not be resolved automatically. **That conclusion was too broad.**

Individual thread pages **do** server-render their `<title>` and Open Graph tags:

```
[All Waves] Star Citizen Alpha 4.10 PTU Patch Notes 12368639
```

And the slugs are a sequential series: base, `-1`, `-2`, … Verified for 4.10 — six threads, builds 12311913 → 12368639, and `-6` is a clean 404.

**So the thread list is not scrapable, but the series is walkable and every hit is verifiable.** Probe until 404; the last 200 is current; its title states the build. No API, no credentials, no CORS problem. That is the dependable path, and it is a work order rather than something the page can do itself.

## What is in the page now

- **PTU tag → the actual thread** for 4.10 build 12368639 (All Waves), published 2026-07-31.
- **A muted "build 12368639 · all builds ↗"** beside it, linking the channel. This is the escape hatch for build-level drift, which the gate below cannot see: a newer build of the *same* version gets a new thread while the recorded link stays plausible and one build behind.
- **A staleness gate.** `CC_PATCH.ptuThread` is stamped with the version it was recorded for. If the banner's PTU version has moved past it, the direct link is **not used** — the tag falls back to the channel and its tooltip says why. So the failure mode of a forgotten update is "one extra click", never "notes for a version nobody is running."

LIVE is unchanged: 4.9.0 → its comm-link page, unknown versions → the RSI index.

## Verification

Rule 12 — the gate was exercised against known-bad input, not reasoned about.

A fixture was built by rewriting the PTU tag in the *built deploy file* from 4.10.0 to 4.11.0, with an assertion that the substitution actually applied, so a fixture that silently failed to modify anything could not pass as a green run.

| | recorded for | banner says | result |
|---|---|---|---|
| current | 4.10 | 4.10.0 | direct thread link, `data-cc-ptu-fresh=1` |
| known-bad | 4.10 | 4.11.0 | channel fallback, `data-cc-ptu-fresh=0`, tooltip names both versions |

Both asserted, both passed. `pageerror` listener attached throughout — zero errors. Layout measured at 390, 820 and 1500px: no overlap, no horizontal overflow at any width, and inspected visually at all three rather than trusted from numbers.

## One defect found by looking at the picture

The third link pushed the banner past a tablet's width, and a flex row's response to that is to squash its children — so at 820px "LIVE 4.9.0" broke inside its own pill and "Patch Notes ↗" wrapped onto three lines. **The bounding-box numbers showed no overlap and no overflow; the run was green.** Only the screenshot showed it.

Fixed with `flex-wrap` on the banner and `flex:0 0 auto` plus `white-space:nowrap` on the pills and labels, so the row wraps to a second line instead of crushing its contents.

*A collision check confirms elements are not on top of each other. It says nothing about whether they are legible.* Worth carrying forward — the mobile work earlier this week leaned on the same all-pairs check.

## Maintenance this leaves

Until the resolver is built, two hardcoded values need updating:

- **`CC_PATCH.ptuThread`** — each new PTU build. Probe the next suffix (`-6`, then `-7`) until one 404s; the last that loads is current, and its title carries the build number and wave.
- **`CC_PATCH.live`** — one line per LIVE release. RSI assigns the comm-link ID; it cannot be computed, only read off the patch-notes index.

Forgetting either is safe by construction: LIVE falls back to the index, PTU falls back to the channel.

## Filed alongside

`docs/workorder-patch-link-resolver.md` — the Go resolver that removes both manual steps. **Explicitly ranked behind Part B and Part C**; the page degrades safely without it and Phase 1 matters more.
