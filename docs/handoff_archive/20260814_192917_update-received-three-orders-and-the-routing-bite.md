# Update — received three orders. The routing fix is extended to cover the exact filenames that misrouted, and it needs a rebuilt watcher to take effect.

Receipt per rule 13, before starting.

```
1  WORKORDER_roadmap-watcher-2026-08-14.md (rev 2)  +  ADDENDUM_...heartbeat-2026-08-15.md
2  prompt-code-worker-and-version-feed-2026-08-15.md
3  prompt-code-onmachine-reader-2026-08-15.md
```

In that order. Rev 2 is already built and reconciled; the addendum adds one
thing. The two AMENDS files and the rework spec stay shut.

## The routing bite, and why it kept happening

Both misrouted orders are still sitting in the archive:

```
docs/handoff_archive/20260814_191346_prompt-code-worker-and-update-feed-2026-08-15.md
docs/handoff_archive/20260814_191742_prompt-code-worker-and-release-feed-2026-08-15.md
```

The first has "update" in the FILENAME. The third bite was the addendum, whose
H1 reads *"a stopped watcher must not look like an update saying nothing"* -
routed on the word "update" in a sentence about not being misread.

**My prefix fix already covered `prompt-` and `WORKORDER_`. It did NOT cover
`ADDENDUM_`**, because I wrote the prefix list from the types I happened to have
seen rather than from the directory. So I enumerated `docs/` and took the list
from there - `ADDENDUM_`, `URGENT_`, `PROJECT-`, `ARCHITECTURE_`, `workorder-`
lowercase and others were all missing.

A test now pins the actual filenames that misrouted, including the two in the
archive, so this specific bite cannot recur silently.

## IT IS NOT LIVE YET, AND THAT MATTERS

The fix is in `watcher-go` source. **The running watcher is the old
`inbox_watcher.exe`.** Nothing changes for Sleven until that binary is rebuilt
and the scheduled task restarted - which is rule 14 territory (one writer, and
the task is registered by `setup_watcher_task.ps1`).

So: he will keep seeing misroutes until the exe is replaced. I am not
rebuilding or re-registering a scheduled task unasked - that is a live pipeline
component and the last two times something re-registered a task in this repo it
was a defect. **Say the word and I will rebuild the exe; restarting the task is
his call.**

## The two archived orders

They are readable where they are and I have not moved them - moving files
between `docs/` and the archive is exactly the kind of quiet reshuffle that
makes the next person doubt the record. Superseded by the version-feed order
anyway.
