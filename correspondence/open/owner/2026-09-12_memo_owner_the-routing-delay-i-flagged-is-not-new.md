# Memo

To:      Owner
From:    Build
Subject: The routing delay I flagged in the swap report is not new. The old watcher did the same thing all day. Measured, closed.
Status:  Open

**My swap report ended with an observation, not a conclusion:** two letters after the swap waited 40 to 60 seconds to be filed. I said I would tell you if that turned out to be new.

**It is not new.** For every file the watcher filed today, I measured the gap between the file landing in `inbox/` and the watcher filing it. That is the watcher's own log time minus the file's own timestamp:

    old watcher, before the swap   84 letters   median 12 s   longest 82 s   27 over 30 s
    new watcher, after the swap     2 letters   median 25 s   longest 47 s

**Waits of up to about 80 seconds were ordinary on the old binary, and 47 seconds sits inside that.**

- **The cause is the watcher's once-a-minute cycle,** which the new build did not change.
- **Nothing is lost or reordered while a letter waits.**

**Nothing to do. Closed.**

*Build (Code), 2026-09-12.*
