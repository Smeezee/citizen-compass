# UPDATE — three pipeline defects fixed in the handoff generator

Fixed the two misfiling defects in `generate_handoff.py`, plus a third that
surfaced while verifying them and was blocking regeneration entirely. Nothing
committed.

## DEFECT 1 — classification keyed off body prose

`is_handoff_doc()` scanned `text[:500]` for the bare word `HANDOFF`, and runs
*before* `is_update_doc()`. So an update whose **prose** merely mentioned a
handoff was treated as a full handoff document: it **replaced
`_latest_raw.md` / the PROJECT NOTES block** instead of appending to
`_updates_log.md` / RECENT UPDATES.

This hit twice in one session. The update correcting the push status was
misfiled this way — it landed in PROJECT NOTES, and never reached the
append-only running log at all.

**Fix:** new `_title_line()` helper. Classification now reads the document's own
title — its first markdown heading, or first non-blank line if it has none —
rather than arbitrary prose. Filename hints are unchanged and still win, which
is deliberate.

## DEFECT 2 — `###` subheadings promoted to phantom entries

`_parse_update_entries()` split `_updates_log.md` on every `\n### `. Any `###`
subheading inside an update body therefore became a top-level entry — inventing
entries that were never logged, **and truncating the real entry they were lifted
out of**, since the parent lost everything after its first subheading.

10 of 45 parsed entries were artifacts. Eight came from one CC-12/CC-10 update
("A1. Actual current state", "B3. The mixin does NOT apply cleanly", ...); two
from a cowork entry ("Ship detail pages", "Display engine").

**Fix:** new `UPDATE_ENTRY_HEADER_RE` matching only the headers
`append_update()` actually writes — `### <YYYY-MM-DD HH:MM:SS> ...`. The
separator after the timestamp is not pinned, so an entry written with a hyphen
instead of an em dash still parses. Content before the first header, and logs
with no recognisable headers at all, are preserved rather than dropped.

**No data migration was needed** — the bug was purely in parsing, so the repair
is retroactive. `_updates_log.md` was not edited.

## DEFECT 3 — UnicodeDecodeError killed regeneration (found while verifying)

Regeneration was failing outright:

```
ccpp.py line 286 -> json.load(f)
UnicodeDecodeError: 'charmap' codec can't decode byte 0x81 in position 73514
```

`ccpp.py` opened JSON with no `encoding=`, so Windows fell back to the ANSI
codepage (cp1252). The offending bytes are `\xc4\x81` — "a" with a macron, in a
Xi'an ship path (`...an'tok.yXi\model.g`).

**The file was always valid UTF-8; the reader was not.** Verified directly:
`citizen-compass.ccpp` (144,771 bytes) decodes as UTF-8 cleanly.

**Fix:** `encoding="utf-8"` on all three unencoded `open()` calls in `ccpp.py`
(lines 116, 277, 285 — the hardpoints read, and the packet save/load pair).
JSON is UTF-8 by spec, RFC 8259. No unencoded `open()` remains in that file.

This is the same family as the known caveat about pipeline `log()` functions
crashing on Unicode symbols. It is a **third** instance of Windows default
encoding breaking this pipeline on real Star Citizen ship names.

## Verification

`_verify_generate_handoff.py` (new, repo root) — characterization test written
**before** the fix so the change is provable.

| | before | after |
|---|---:|---:|
| classification cases failing | 2 | **0** |
| entries parsed from `_updates_log.md` | 45 | **35** |
| phantom entries | 10 | **0** |
| synthetic-log entries (2 real, 2 subheadings) | 4 | **2** |
| parent entry retains its own subheadings | no | **yes** |

7 classification cases pass, including the three that must still be treated as
genuine handoffs (`CITIZEN COMPASS HANDOFF` heading, `SESSION ARCHIVE` heading,
and a filename containing "handoff"). Overall: 6 failures -> 0.

## Note on regeneration timing

`generate_handoff.py` can take over two minutes to run: `build_notes_block()`
calls Ollama with `OLLAMA_TIMEOUT_SECONDS = 120` and only falls back to raw text
after that timeout expires. Not a hang. Worth knowing before assuming it has
stalled.

## Files changed (uncommitted)

- `generate_handoff.py` — `re` import, `UPDATE_ENTRY_HEADER_RE`, `_title_line()`,
  rewritten `_parse_update_entries()`
- `ccpp.py` — three `encoding="utf-8"` additions
- `_verify_generate_handoff.py` — new regression test

Revert path if needed: both edited files were tracked and clean beforehand.

## Still open

- `0ae0514` committed and unpushed; `main` is 1 ahead of `origin/main`.
- Re-gate source 1 (`20260731T041451Z`) with the fixed `integrity_scan.py`.
- Correct the "deterministic" wording in `api_star_citizen_wiki.py` —
  "near-deterministic" is accurate, one success at `page[size]=200` is on record.
- CC-12 / CC-10 remain written proposals awaiting a decision.
