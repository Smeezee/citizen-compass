# Update - sweep run: 116 ok, 4 failed, 0 NOT RUN. Two of the four fixed and proven; two are not mine. No deploy.

## The sweep

    116 ok, 4 failed, 3 skipped, 0 NOT RUN, in 1606s
    payload 53676ee77da95f1f

**All 12 files whose exit codes I changed passed.** No control's pass path
broke, which is the half the failure-path proofs could not tell me. 0 NOT RUN
means nothing regressed into "could not look" either.

## The four reds, and who each belongs to

### 1. `_verify_placer_candidates.py` - MINE, FIXED, PROVEN

    90 markers moved on 7 previously-placed hulls

Not a regression. C1's memo predicted exactly this: "7 of them already had
markers on the site fitted to the wrong one". The negative control assumes a
change is ADDITIVE; this one was CORRECTIVE by design.

**Verified before declaring, and my first attempt at verifying was wrong.** I
matched the 7 ship names to the 31 regenerated hulls by substring - which is
fuzzy matching, rule 17, and two of them only "matched" because of a
manufacturer prefix. Redone against the pipeline's own `matched.json` mapping,
exact equality on the hull each ship names: **all 7 map into the 31 C1
regenerated. Zero unexplained.**

The 7 are declared by name with their port counts - 9, 11, 18, 1, 31, 13, 7 =
**90, which is exactly the number reported.** An eighth hull moving still fails.
Following the file's own Asgard precedent: reported by name with the reason,
never swallowed.

Two guards, both proven:
- undeclared movement fails - proven by the pre-change run, which went red
  naming all seven.
- **a declaration cannot outlive its reason** - proven by mutation: a declared
  hull that never moves is REFUSED.

    17 assertions, 0 failed

### 2. `_verify_hardpoint_join.py` - MINE, FIXED, PROVEN

Pinned 5, got 3: 85X and Starlite left, nothing was added.

**This is where the order's "gains 5" figure came from** - it is this file's
EXPECTED map, not a measured gain. The measured gain was always 3.

`in_scope` is model stems NOT already in `fleet_stems`, so a ship leaves it the
moment the fleet gains an entry - a graduation, not a loss. C1's marker batch
gave 85X and Starlite fleet entries ("85X Limited", "MISC Starlite"), so they
left. **Verified in `hardpoints_fleet.json`: both present, and the other three
absent.**

Split into two questions instead of shrinking one map:
- `G3_RESOLVES_TO` keeps all five, so the assertion that catches a WRONG match
  is not silently retired when a ship graduates.
- `G3_INSCOPE_EXPECTED` is the three still asked about.
- and **each graduate must actually be in the fleet** - proven by mutation: a
  stem in neither the in-scope set nor the fleet is caught as "a loss, not a
  graduation".

    VERIFY PASSED

### 3. `_verify_holo_render.mjs` - ESCALATED TO C1, see the previous update

The pre-pass negative control. Not re-pinning it: the repair changes what the
control MEANS and rests on C1's own E7b floor reasoning.

### 4. `_verify_marker_census.py` - C1'S FILE, NOT TOUCHED

    REFUSED - 8 declaration(s) no longer describe anything:
      AEGS_Tiburon    declared, but 57 -> 65
      RSI_Mantis      declared, but 12 -> 18
      DRAK_Pitbull, GLSN_Basher, MISC_Starlite,
      ORIG_600i_Executive_Edition, RSI_Aurora_Mk2, RSI_Hermes  (all unchanged)

Six declare a loss that has stopped happening; two now move by a different
amount than declared. That is her own "a declaration that outlives its reason"
rule firing on her file. **Reported, not edited** - rule 14, OWNERS.md.

## NOT DEPLOYED

The sweep cannot be green while 3 and 4 are red, and neither is mine to close.
Per the order and rule 25 Part B this is filed rather than worked around, and I
have not gone looking for different work. A confirming sweep is running to check
the two fixes in context; the deploy stays blocked either way.

**Two things are needed from C1:** the pre-pass decision, and her census
declarations.

## One more instance of the exit-code defect, noted not fixed

`_verify_placer_candidates.py` raises a bare `FileNotFoundError` when
`build_matched.py` is absent, where a NOT PERFORMED belongs - same class as the
ENOENT I closed in `_verify_model_scale.mjs`. Left alone: it was not in the
surveyed set and I am not widening scope mid-job.
