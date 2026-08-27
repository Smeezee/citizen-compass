# ORDER — Twelve of the fifteen "no model anywhere" ships have a model

**Written by C1, 2026-08-27. For Code.**

**Sleven was right and I was wrong.** He asked, more than once, why ships with
no model on our site have one everywhere else, and I answered about formats and
lineage instead of going and looking. He said today:

> *"You should have checked the RSI holoviewer for every single fucking ship."*

I checked the fifteen this morning. **Twelve of them have a model.**

---

## What was found, and how

Source: the **Fleetyards public API**, `api.fleetyards.net/v1/models/<slug>`.
No key, no login, not under `/media/`, and it is the same asset lineage as the
RSI holoviewer — recorded in `FINDING_beating-the-flat-mesh-baseline-2026-08-23.md`
as *"`media.holo` → a glTF blob, confirmed live. Same lineage as our 234."*

So this is not a different well. It is **the** well, on a host that answers.

| our ship | Fleetyards | model |
|---|---|---|
| Mantis | Mantis | **glTF** |
| Tiburon | Tiburon | **glb** |
| MOTH | MOTH | **glTF** |
| Pitbull | Pitbull | **glTF** |
| Tyilui | Tyilui | **glTF** |
| Basher | Basher | **glTF** |
| PTV | PTV | **glTF** |
| UTV | UTV | **glTF** |
| Starlite | Starlite | **glTF** |
| 85X Limited | **85X** — `85x-limited` 404s, `85x` is a *different record* | **glTF v2** |
| M80 | M80 | **glTF** |
| Hermes | Hermes | **glTF** |
| Command Module | — | **not found** |
| Power Suit | — | **not found** |
| Vanduul Mauler | — | **not found** (`vanduul-mauler`, `mauler` both 404) |

**Twelve found. Three not found.** The three are plausibly not ships at all —
Command Module and Power Suit read as equipment, and the Mauler is Vanduul
concept — but that is a guess and is written down as one. Do not record them as
"does not exist" until somebody has looked.

**The 85X row is the one to be careful with.** `85x-limited` 404s and `85x`
returned a different model record. That is a NAME COLLISION, not a match. It is
in the table because a model was found at that slug; it is **not** cleared for
import until somebody confirms the 85X Limited shares the 85X's external shape.
Same standard as `DECISION_shared-hulls-are-fine-unless-the-shape-differs`.

---

## M4 — SWEEP THE WHOLE FLEET, NOT THE FIFTEEN

The fifteen were checked because they were the known gap. **The fleet was not
swept, and I could not sweep it from here** — my fetch tool summarises pages
through a small model and truncated every paginated response to 2-3 of 12
entries. Three agents hit that ceiling identically. That is reported as a tool
limit, not as a result: **do not treat the 46 fleet names I collected as data.**

Code has no such limit. On his machine the API answers directly.

### M4a
Pull the full model list from `api.fleetyards.net/v1/models`, paginated to
exhaustion, and record for every entry: name, slug, `media.holo.url`, and the
file extension the URL ends in.

### M4b
Join it to our own fleet by the same standard everything else in this project
uses: **exact match, no fuzzy matching.** Names that do not join exactly go to a
review list, exactly like `needs_human_review.json`. The 85X collision above is
the reason this is not negotiable — a fuzzy join would have "matched" it.

### M4c
Output `data-layer/derived/model-availability/` with the joined table, the
unjoined residue, and a MANIFEST naming the source, the date, and the join rule.

### M4d
**Cross-check the 234 we already have.** If Fleetyards holds a model for a hull
where ours is a stand-in or an inherited base, that is worth knowing. This is
not an instruction to replace anything — it is an instruction to find out.

---

## M5 — BRING THE TWELVE IN

### M5a
Fetch the twelve, into the same pipeline the existing models go through. Not a
special case, not a side folder — if they cannot go through the normal path,
that is a defect in the normal path and it gets fixed instead.

### M5b
**Every one gets `last_verified_patch` and a provenance record naming the
source.** Standing rule, no exceptions, and it matters more here than usual
because these came from a third party rather than our own extraction.

### M5c
Attribution follows `RULING_community-practice-is-the-standard-2026-08-22.md`
as it already does for every other model: credited to Cloud Imperium Games,
unofficial-fan-site notice, working contact route, taken down on request. The
disclosure bar ordered in `ORDER_the-disclosure-bar-2026-08-27.md` is where it
shows.

### M5d
**Not the 85X Limited** until the shape question in the table above is answered.
Eleven go in. The twelfth waits on a human.

### M5e
A check that fails if any of the eleven renders an empty scene. **The control:
it must also fail when pointed at one of the three not-found ships.** A check
that passes on a ship with no model is not checking anything.

---

## What this does NOT change

**It does not fix the hardpoints.** These are the same single welded meshes with
no node hierarchy. A ship that had no model now has one, and its markers will be
derived from mount names exactly like every other ship's. That problem is
untouched and is still waiting on the p4k decision.

**It does not mean our existing 234 are wrong.** Same lineage, same files.

---

*C1, 2026-08-27.*
