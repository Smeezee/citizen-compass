# Update — item 1 done. The watcher now has three states and a last-successful-check timestamp, and STALE has been observed rather than assumed.

`roadmap-watcher/`. Builds, vets, formats clean. 15 tests green. **Not committed.**

## The addendum's gap, closed

A tripwire that died three weeks ago and one that ran an hour ago and found
nothing produce identical silence. That was true of this watcher until now.

```
NEW CARD FOUND        something appeared, here it is
CHECKED, NOTHING NEW  ran, parsed, diffed, clean - WITH the timestamp
STALE / FAILING       has not completed a good run since <when>, and why
```

**Two separate marks, not one.** `last_good_run` is any successful check;
`last_good_scheduled_run` is a successful TIMER run. They are tracked apart
because a hand-run must not paper over a dead scheduler - which is exactly the
failure the addendum describes, and it is the default behaviour if you keep one
timestamp.

**A pass that polled nothing does NOT advance either mark.** A run that did not
look has not looked. That is the lifecycle rule the project adopted after the
874-findings incident, applied here: CLOSED only by a run that looked.

**The threshold is in CYCLES, not hours** - `stale_after_cycles`, default 3. A
threshold in absolute hours silently becomes wrong the moment the cadence moves.

## STALE observed, not reasoned about

The addendum is explicit that a staleness detector never seen reporting stale is
the same category of thing it exists to catch. So:

```
$ roadmap-watcher -check          (scheduled timer has never run)
STALE / FAILING - this manual check succeeded, but the scheduled watcher has
NEVER completed a good run - only manual checks have ever succeeded (threshold 12h)
CHECKED, NOTHING NEW at 2026-08-15T00:32:34Z. checked boards [1 2] ...

$ (backdate the scheduled mark 13h, then check)
STALE / FAILING - this manual check succeeded, but the scheduled watcher has not
completed a good run since 2026-08-14T11:32:34Z (13h0m0s ago, threshold 12h0m0s)
- the timer may be dead

$ roadmap-watcher -status
state      : STALE / FAILING - ... the timer may be dead
```

**Both lines appear together on purpose.** The manual check still reports its own
honest result AND says the timer is dead. Reporting only one of those is how
"nothing new" becomes reassurance nobody earned.

Four tests, each with the negative control that stops the detector being a
constant: 13h is stale, 1h is not; never-scheduled is stale; an unreadable
timestamp is stale rather than assumed healthy; and the threshold moves with the
cadence.

## What did NOT change

Cadence, endpoints, staged rollout, the baseline rule, transport, parser traps,
what to key on - all C3's, all untouched. The addendum said it adds a state and a
timestamp and should not become a redesign, and it did not.

## Two mistakes of mine worth recording

**A patch script did all its replacements in memory and wrote at the end**, so a
`sys.exit` on the third anchor discarded the two that had already succeeded -
while printing "ok" for both. I believed them and moved on, and only the compiler
caught it. Scripts that report success before writing are a small silent-success
factory; the rewrite writes or fails as one unit.

**The routing prefix list was written from memory, not from the directory.** It
covered `prompt-` and `WORKORDER_` but not `ADDENDUM_` - which is why Sleven's
third document was bitten by the same bug I had just "fixed". Enumerating
`docs/` found `ADDENDUM_`, `URGENT_`, `PROJECT-`, `ARCHITECTURE_` and lowercase
`workorder-` all missing. The list now comes from the directory and a test pins
the real filenames.

Next: item 2, the Worker and version feed.
