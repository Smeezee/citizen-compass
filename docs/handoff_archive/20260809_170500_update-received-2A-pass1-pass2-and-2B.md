# Update — received three sequenced orders: 2A pass 1, 2A pass 2, and 2B

Received from C1, 2026-08-09. Logging receipt before starting, per rule 13.

## Correcting a stale precondition in pass 1

Pass 1's `depends` block states order 1 "has not landed" — that
`sc_export.js` is still the pre-fix version, `test_sc_export.js` is still
present, and `roundtrip.js` / `mutate.js` / `fixtures/` do not exist.

**That was true when C1 wrote it and is not true now.** Order 1 landed earlier
in this same session — see
`docs/handoff_archive/20260809_164150_update-exporter-landed-roundtrip-and-mutation-green.md`.
Re-verifying §7 before starting rather than assuming my own earlier work still
holds, since another session has been active in this repo today.

## Order of work

Sequential, as specified: pass 1 → pass 2 → 2B. Each has its own acceptance
list; I will file an update per pass rather than one at the end.

## Two things I am carrying into pass 2 that need flagging now

Pass 2 says fonts are decided and cites Sleven's ruling. **The ruling I recorded
today (`docs/RULING_holo-viewer-models-keybind-overlay-and-fonts-2026-08-09.md`)
left one sub-question explicitly open**, and pass 2 does not answer it:

`_layer.src.html` ships a user-facing accessibility font switcher — five modes
including Atkinson Hyperlegible (Braille Institute, low-vision) and Lexend —
applied with `!important` and scoped `*:not(.cc-ui):not(.cc-ui *)`. If the
builder's dense action content is marked `.cc-ui` to pick up the Star Citizen
faces, that content becomes permanently exempt from the switcher.

My recommendation stands: **SC faces on chrome only** (headings, tabs, buttons,
panel titles), action-table content left following the reader's chosen font.
That satisfies the ruling as made without disabling an accessibility feature.
I will implement it that way in pass 2 and flag it prominently rather than block
on it — it is reversible and the alternative is stalling three orders on a
styling scope question.

Second: pass 2 asks for fonts served as files from a new `_deploy/fonts/`. The
three faces are open-licensed as far as I know, but **font licensing is in the
class of thing I report rather than decide (rule 8)** — Sleven should confirm
the licence before this ships publicly, and I will note it in the write-up.
