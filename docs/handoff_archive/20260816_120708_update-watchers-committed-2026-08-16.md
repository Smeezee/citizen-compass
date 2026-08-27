# Update: the roadmap watcher and the routing fixes are committed and pushed

    a9ff223  A tripwire that expires by itself, and says when it has stopped looking
    2798840  The newest correction is the one under the plain filename

Both pushed. `origin/main` is `2798840`, nothing unpushed.

Built and tested fresh before committing, not from cache:

    citizencompass/roadmapwatcher   ok  0.821s
    citizencompass/watcher          ok  0.545s  (all routing tests PASS)

## What was kept out of the commit

`roadmap-watcher/` held two `.exe` files and two per-machine JSON files. Added a
`.gitignore` for them, and checked the staged list for `.exe`/state/settings
before committing rather than after.

`roadmap-watcher-state.json` matters most: it holds the baseline of cards this
machine has already seen. Committing it would ship one machine's idea of
"already known" to every other, so a card somebody else had never seen would
arrive pre-marked as old - which is the one thing a tripwire must never do.

## The lesson worth keeping

**Uncommitted work is invisible work.** Both of these were built, tested and
reported days ago and then left in the working tree waiting for a go-ahead. A
state document written this morning recorded the roadmap watcher as "specced and
unstarted", and it was right to - from outside the repo there was nothing to see.

That is on me. Reporting a thing as done and leaving it uncommitted means the
next person has to take my word for it, and the repo says otherwise.

## Correction to docs/CURRENT-STATE.md

That document says **"0.3.3 was cut and published without Sleven authorising a
release."** It was authorised - Sleven said "cut 0.3.3" in as many words, and it
had been held back twice before that with an explicit statement that it needed
his word.

The principle in that note is right and worth keeping. The specific claim is not,
and C1 was writing without sight of the session. Recorded here so the two
documents do not disagree silently.
