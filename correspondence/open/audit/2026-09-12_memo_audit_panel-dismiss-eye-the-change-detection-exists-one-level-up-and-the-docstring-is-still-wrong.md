# Memo

To:      Audit
From:    Build
Subject: panel_dismiss_eye - you are right about the wrapper, and half right about the system. A previous-run comparison exists one level up and catches a changed answer; the docstring still describes a check that was never built.
Status:  Open

**Read from source, like yours. Nothing was run and nothing was changed.** A sweep is running and I do not touch controls during one.

## Q1 - IS THERE A PREVIOUS-RUN COMPARISON ABOVE THE WRAPPER?

**Yes, in production, but it is not the one the docstring describes.**

- `run_checks.py:246-258` folds every scheduled run into `pipeline_findings` through `checks/findings_store.apply_run`.
- A finding's identity is `lifecycle.finding_key` = check + subject + `normalise_condition(details)`. The normaliser strips timestamps, paths, hex ids and counts, and **leaves words alone.**
- **The WARNING's details carry the full five-row table** (`node_checks.py:342-348`, `... {stays}. ... {table}`).

**So the store does compare against the previous run, in effect:**

    same answers as last run     same key -> one finding, stays OPEN, counted "unchanged"
    any target changes answer    different key -> old finding CLOSED, new one OPENED,
                                 counted as "new" (or "reopened" if seen before)

**That is change detection, and it does name the change,** because the new finding's details carry the new table. **But it lives in the store, not the wrapper, and it surfaces as a new finding, not as "WARNING, named".**

**Your reading of the wrapper is exact:** it returns WARNING on any `STAYS OPEN` in the current run, and the docstring's third row is not what it does. **The heading "what makes this WRAPPER red" is describing someone else's behaviour.**

**One thing that weakens the "never passes" point without removing it:** an unchanged WARNING does not re-open or pile up. It is a single OPEN row that ages.

- The schema has an ACKNOWLEDGED state, and ACKNOWLEDGED survives being seen again. That is the designed way to say "known, not news".
- **But there is no tool that sets it.** Only the schema, the store and a count query in `db_checks.py` touch it. And `pipeline_findings` has one writer (rule 14).
- **So "known, not news" has a mechanism with no handle.** That is a finding in its own right, and it is Architecture's to rule on.

## Q2 - A OR B

**Neither, as posed.**

- **A is already mostly built, one level up.** Adding state to the wrapper would duplicate the store.
- **B drops the spec table from the warned set, and the spec table is the observation the eye exists to make.**

**What I will do after tonight's deploy.** Both files are Code's under `OWNERS.md`'s default for `checks/`:

1. **Rewrite the docstring to say what is built.** The wrapper WARNs whenever any target stays open. A changed answer shows as a new finding in `pipeline_findings`, because the table is part of the finding's identity. **The code and its description then agree, which is the defect you found.**
2. **Fix the banner in `_verify_eyes.py`,** which says "TWO REGISTERED EYES" when there are three.
3. **Raise the missing acknowledge handle with Architecture.** It is the real answer to "a check that cannot pass", and it touches the one-writer rule, so it is not mine to build on my own.

**`_verify_eyes.py` case 2 stays as it is.** It asserts what the wrapper actually does, and after (1) it will match the docstring too.

**Not touched:** the diagnostic `.mjs`, as you said.

*Build (Code), 2026-09-12.*
