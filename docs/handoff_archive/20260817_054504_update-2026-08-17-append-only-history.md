# Update - the history starts today. Item 1 done, committed, pushed.

`3c98235` **Keep what it was, not only that it changed.** Pushed
`c46c524..3c98235`.

Both halves of §1 now append every observation to a durable log, one row per
subject per run, never rewritten. Current-state maps untouched - the diff
depends on them and they work.

    roadmap-watcher/roadmap-watcher-history.jsonl                 3 rows
    data-layer/derived/model-fingerprints/model_fingerprint_history.jsonl  235 rows

**The first rows are in the commit**, which is the only part that could not be
recovered later. The watcher ran for real: three Constellation cards on Release
View, fingerprinted and dated.

## Decisions I made, and why

**JSONL rather than a table.** The order left it to me. A table is better where
the writer already has a database; this one does not - it is a standalone exe on
a desktop whose job is to keep running unattended for years. A DB dependency
means it stops recording on the day Postgres is down, moved or upgraded, and the
one property this file must have is that it never stops. Importing JSONL into a
table later costs nothing; the reverse is a migration.

**Appended BEFORE the diff runs.** `Diff` mutates the stored fingerprints - that
is how it works. Writing history afterwards would record the state the diff had
already moved to, so the run that changed a card would be the one run whose
"before" was never kept.

**A shared spine: at, kind, subject, name, fingerprint, source.** Boards mean
nothing to a .glb and vertex counts mean nothing to a card, so each side adds
its own fields after those six. The verifier checks the Python rows against the
Go struct's own json tags, because neither side can check that alone.

## Rule 12

The order names the check and both halves are driven with it: a CHANGED subject
produces two rows with different fingerprints and both survive. Plus the control
that makes it mean anything - a history truncated the way a rewriting writer
would leave it, confirming the same assertion detects the loss.

    go test ./roadmap-watcher    ok  (5 tests)
    checks/_verify_fingerprint_history.py    11 checks, all passing

Also proven: a run where nothing changed still appends (no holes where a card
sat still); a truncated line is skipped and counted rather than making the
archive unreadable; a run that measured nothing REFUSES to append.

## Not done, deliberately

§2 and §3 of that order are decisions for C1 and Sleven, not builds, and §0 says
so. Nothing of the Historian herself was built.

Next down the queue unless redirected.
