# External source manifest — fixed status vocabulary

**Created 2026-08-01.** Before this date the project had no single canonical
definition of these values anywhere in `docs/` or in code. They existed only as
strings written into `data-layer/external-source-manifests/*/**.json`. This
document is a record of the values already in use plus one addition; it does not
invent new meanings for existing values.

Applies to the `snapshot_status` field in every external source manifest.

---

## `snapshot_status`

| value | meaning |
|---|---|
| `complete` | Everything in scope was retrieved, and the run's own gates verified it. The status is earned by checks that could have failed. |
| `partial` | The run retrieved some but not all of what was in scope, or a gate did not pass. A `.partial` folder suffix accompanies this. **A `.partial` folder is a correct outcome, not a failure.** |
| `failed` | The run did not retrieve usable data. The data itself is absent, unusable, or known bad. |
| `superseded` | **The data is genuine, but the run's verification cannot be trusted; a later verified run replaces it.** |
| `blocked_missing_credentials` | Retrieval could not be attempted because required credentials were unavailable. |
| `blocked_missing_provenance` | Retrieval was possible but withheld because the source's provenance or licensing could not be established. |
| `not_directly_downloadable` | The source exists but cannot be pulled by the documented mechanism (e.g. no API, no bulk export). |

---

## Notes on `superseded`

Added 2026-08-01 for snapshot `20260731T031754Z` (source 2, scunpacked.com).

`superseded` exists because `complete` and `failed` were both wrong for that
case. The retrieval script of the time (`scunpacked_com.py`, pre-CC-07) had
`main()` return `None`, so the process exited 0 unconditionally — no endpoint
outcome could ever have failed the run. It also wrote each response body to its
final filename before examining `resp.status_code`, so an HTTP error page would
have been saved as `ships.json` and reported as a successful landing.

The data turned out to be genuine: a later verified run re-fetched both
endpoints and got byte-identical content, matching SHA-256 *and* ETag. So:

- `complete` would be wrong — nothing verified it at the time.
- `failed` would be equally wrong — the data is fine.

The distinction this vocabulary must preserve is **between the quality of the
data and the quality of the process that obtained it.** `superseded` says the
bytes are trustworthy while the run that produced them is not, and points at the
run that does carry the verification.

### What `superseded` does *not* mean

It does not mean the old data was wrong, and it does not retroactively verify
the old run. A superseded snapshot is trustworthy **by inheritance** from its
successor, never by its own process. If the successor is later found faulty, the
superseded snapshot has no independent verification to fall back on.

### When to use it

Use `superseded` when **all** of these hold:

1. The snapshot's data is established as genuine — by a later verified run, or
   by another independent check.
2. The run that produced it did not, or could not, verify what it retrieved.
3. A specific successor run exists and is named in the manifest.

If (1) does not hold, the correct value is `partial` or `failed`. If (3) does
not hold, leave the status as it is and record the concern instead — do not mark
something superseded by nothing.

---

## Rules for changing a status

`snapshot_status` is an **assessment** of a run, not a record of it, so it may
be corrected as evidence changes. Every other field in a manifest records what
happened during acquisition and is **append-only** — see CLAUDE.md rule 11.

When changing a status:

- Change `snapshot_status` and nothing else.
- Append a note recording the old value, the new value, why, and what evidence
  drove it.
- Never rewrite an acquisition-time field to make a run look better than it was.
  A manifest that contradicts itself between its acquisition block and a later
  assessment block is doing its job — the discrepancy *is* the record.
