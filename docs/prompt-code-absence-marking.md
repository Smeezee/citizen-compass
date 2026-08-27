# PROMPT FOR CODE — the guard stops deletion. Now stop the lie.

    from    C1, 2026-08-08
    for     Code
    basis   docs/FINDING_importer-deletion-audit-2026-08-08.md (C3)
            docs/WORKORDER_preservation-model-and-never-delete-rule.md (C3)
            your own update-never-delete-guard-done-20260808.md

    The guard work was right. Installing it at engine creation rather than per
    importer is the difference between a rule and a habit, and running all 15
    assertions with AND without the guard is the only version of that test worth
    having. Nothing below reopens any of it.

---

## The problem the guard does not solve, in C3's words

> **Nothing in the importers deletes a row.** The Aurora Mk I will survive the
> next patch import. **But because nothing deletes AND nothing marks absence,
> it survives still flagged `purchasable`, still stamped
> `last_verified_patch = 4.9`, and indistinguishable from a ship that still
> exists. The row is not lost, it is quietly turned into a lie.**

That is a sharper statement of the risk than the original work order had, and it
inverts the priority. Losing a fact is recoverable from a snapshot. **Publishing
"you can buy this" about a ship CIG has removed is not** - it is the
`NotForRelease` worry pointed the other way in time, and it lands on the exact
page a newcomer trusts most.

So: an entity absent from the current patch must become *visibly* absent, and it
must happen in the same pass that would otherwise leave it looking current.

---

## The job

### 1. Lifecycle columns

C3 specced these and they are settled - real indexed columns, JSONB only for the
tail, per the standing hybrid-schema decision:

    first_seen_patch    text
    last_seen_patch     text
    status              enum  live | retired | renamed | replaced | never_released | unknown
    successor_id        fk    nullable
    removal_note        text  Citizen Compass's own words
    evidence_tier       enum  sealed | external | testimony

`status` and `evidence_tier` are **indexed**, not JSONB - both will be filtered
on constantly ("show me everything retired", "show me only what we can prove").

**`unknown` is load-bearing, not a placeholder.** An entity that vanished before
we started sealing must NOT be labelled `retired`, because we do not know it was
retired rather than renamed. Guessing there manufactures false history on a site
whose whole premise is being trustworthy about provenance.

### 2. The absence pass, in the same transaction as the import

After an import, every preserved row NOT present in the incoming patch gets
`last_seen_patch` left where it is and `status` moved off `live`. Two rules:

- **It runs in the same transaction as the import.** An absence pass that can be
  skipped, or that runs later, is one an interrupted import silently omits -
  and the result looks exactly like a successful run.
- **A row already `retired` is not re-stamped.** `last_seen_patch` records when
  it was last SEEN, not when it was last looked for.

### 3. Backfill from what is already sealed

`first_seen_patch` and `last_seen_patch` come from the snapshots already on
disk. Mechanical, no judgement calls. Snapshots begin 2026-07-31, so anything
present in the earliest one gets `first_seen_patch` = that patch **and a note
saying the true first-seen is unknown** - do not imply we watched it appear.

### 4. The disclaimer is generated, never written by hand

From `status` + `last_seen_patch` + `evidence_tier`, so it cannot drift out of
sync and cannot be forgotten on a new page type:

    retired  "The Aurora Mk I was removed from Star Citizen. Last seen in patch
              4.9. These figures are preserved from our sealed 4.9 snapshot and
              are not current."
    unknown  "This existed in Star Citizen and no longer does. We hold no sealed
              data for it; the details below are not verified against a game file."

The second shape matters more: **it tells the reader how much to trust the
page**, which is the same discipline as `location_pattern_verified` on the
collector sidecars, applied to time.

### 5. Pilot it on retired paints first

C3's recommendation and it is a good one: **498 of 1,099 liveries already have
no store URL.** A ready-made, already-verified retired set with real names, and
it proves the whole pattern end to end without needing a single external source
or a single rights decision.

---

## Acceptance, with the negative control hard rule 12 requires

1. Import a patch with a deliberately removed entity. The row **survives**, with
   `status` off `live` and `last_seen_patch` at the previous patch.
2. **Break the absence pass and confirm the row stays `live`** - a check that
   cannot fail is not a check, and this one's failure shape is a row that looks
   perfectly fine.
3. A row already `retired` does not have `last_seen_patch` moved by a later
   import that also does not contain it.
4. Interrupt an import midway; confirm no row is left half-marked.
5. The generated disclaimer changes when `status` changes, on a page nobody
   edited.

## Constraints

- C1 is sole writer in `citizen-collector/` and is active there. This is
  database and site only.
- C3 is on the mount-name vocabulary and does not build code.
- Do not `git add -A` - CRLF churn. Nothing pushes without Sleven's go-ahead.
- `pipeline_check_results` stays unpreserved, exactly as you had it.
