# Update — your deploy is good and it predates my last change by half an hour. One more build when convenient.

**2026-08-27 19:05 local · C1**

## First, a correction of mine

**My last two notes carry wrong timestamps** — I wrote "19:05" and "20:20 local"
when the machine clock read 18:14 and 18:55. I read the clock at the start of
the session and then estimated instead of re-reading it. The content stands; the
times on it do not. This one is read from `date`.

## Your deploy was correct and is not superseded in substance

    client marker records added for 29 hull(s)
    client hardpoint overlay: 952 port(s) moved onto CIG positions
    disclosure CSS: ... index.html, keybinds.html, loadout.html, find.html
    hull markers 6,284 on 264 hulls, up from 5,490 on 232
    the Mantis: 6 dots on the served page

That is the morning's work live, and the Mantis check is the one that mattered.
**Nothing there needs undoing.**

## What landed after it

Build receipt `ok` at **18:22**. My last placement and overlay runs finished at
**18:56**. So the deploy carries everything except the last half hour:

    now on disk    30 records / 2,612 ports · overlay 93 hulls / 955 ports
    you deployed   29 records / 952 ports

The difference is the frame fix: the acceptance test was measuring each hull's
mounts against its bounding box **as stored**, while `cc_viewer` recentres every
hull on that box before drawing. **71 of 258 models are not centred on their own
origin.** The M2 Hercules is 13.11 units off while its A2 and C2 siblings are
not — same base hull, same 149 ports, same scale to four decimals, and only the
M2 was refused. It now gets 12 markers on a ship that had no marker record at
all.

Also in that window: the case-collision fix (the same ship placed twice under
two spellings, 182 manifest entries for 180 files) and a stale-output guard on
the placement directory.

## So: one more build and deploy, no urgency

    client marker records added for 30 hull(s) the dataset had none for
    client hardpoint overlay: 955 port(s) moved onto CIG positions

**One thing to know before you run it.** The placement script now reconciles its
own output directory and **exits fatally if it cannot delete a stale file**. On
this Linux mount deletion is blocked, so I moved 93 stale files by hand into
`_to_delete/hardpoint-placement-stale-2026-08-27/`. On your machine deletion
works and it will simply print `removed N output(s) from an earlier run`. If it
stops you instead, that is the guard firing correctly and the message names the
files.

Full working:
`docs/FINDING_the-acceptance-test-was-judging-a-frame-nobody-renders-2026-08-27.md`

— C1
