# Update — the inbox watcher now gives the plain filename to the NEWEST arrival. And the sibling routing bug is diagnosed: a work order was misfiled because it contained the word "updateDate".

`watcher-go/classify.go`, new `routeto_supersede_test.go`. Builds, vets, formats
clean, all tests green. **Not committed** (rule 2).

## The fix

`routeTo` used to rename the NEWCOMER on a name collision. So a corrected
document landed under a timestamped name while the plain filename kept the
superseded text:

```
AMENDS_tripwire-release-view-only-2026-08-14.md                  rev 1, WRONG
AMENDS_tripwire-release-view-only-2026-08-14__20260814180543.md  rev 2, right
```

Rev 1 attributed a decision to Sleven he never made. The correction existed, was
filed, and went to a name nobody opens.

**Now the INCUMBENT moves aside and the newest takes the plain name.** Nothing is
destroyed - rule 1 is untouched, both versions survive - but the obvious filename
resolves to the latest arrival, which is what every reader already assumed it did.

The archived copy is stamped with **its own modification time**, not "now", so
the timestamp says when that version was current rather than when it happened to
be pushed aside.

The log line says `SUPERSEDES an earlier file of this name - the older one is
kept as X; this name now holds the newest`, so it does not read as an ordinary
filing.

## Tests, and they fail against the old behaviour

```
a correction takes the plain filename          <- the case that happened
NEGATIVE CONTROL: a first arrival is not treated as a supersede
two corrections in one second both survive
```

Rule 12: restoring the genuine pre-fix logic fails two of the three. The first
attempt at that mutation did not compile, which proves nothing - a build failure
is not a caught defect - so it was redone properly.

The one-second case matters because a second-resolution stamp collides, and an
`os.Rename` onto an existing archive would silently destroy the first one.
"We kept both" has to be true every time or it is a probability, not a property.

## The sibling bug, diagnosed but NOT fixed

§7 also names the routing defect: `WORKORDER_rework-tripwire-build-spec-2026-08-14.md`
was filed into `docs/handoff_archive/` instead of `docs/`. Cause, confirmed
rather than guessed:

```go
var updateHeadingHints = []string{"UPDATE", "UPDATES", "CHANGELOG"}
```

matched as a **substring against the title line**. That work order's own title is:

> "...key on card presence and a payload hash, and do NOT key on **updateDate**."

`"UPDATE" in "...UPDATEDATE."` is true. **A work order was classified as an update
doc because it contained the word "updateDate" - in a sentence telling us not to
key on updateDate.**

This is the same defect already on record for the old Python generator, where the
word "handoff" hijacked routing. Substring-matching prose is the mechanism both
times.

**I have not fixed it**, because it was not what was asked and because changing
where documents land has a wider blast radius than changing which name they keep.
The fix I would propose: classify on the document-type PREFIX
(`WORKORDER_`, `FINDING_`, `AMENDS_`, `update-`, `HANDOFF_`) which this project
already uses consistently, and treat title hints as a fallback only when the
prefix is absent - anchored, not substring. That is maybe twenty lines and it
wants its own test. Say the word.

## Also worth saying

**Third stale `.git/index.lock` today.** All three: zero bytes, tens of minutes
old, no `git` process running, moved aside per rule 1. Three in one session is a
pattern, not luck - something takes the lock and does not release it. Worth
finding out what before it costs a real commit.
