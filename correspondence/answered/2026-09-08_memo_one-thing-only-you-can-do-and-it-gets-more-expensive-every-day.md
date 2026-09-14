To:      Owner
From:    Engineering
Date:    2026-09-08
Subject: one ask — record a play session with the sound on, next time you are playing anyway
Status:  Answered

**The ask is: press record. That is the whole thing.**

Everything else being designed around the collector can be done next month for the
same cost. **This one gets more expensive every day, because a recording made in
October cannot tell anyone what September looked like.**

## WHY IT IS THE ONLY ITEM THAT CANNOT WAIT

There are 628 captured frames with a game log covering the same day, and they can
grade whether the machine reads a screen correctly. **They have no sound attached, so
they can never grade anything else.**

**A recording carries picture and sound already locked to the same instant.** That
makes it the only material that could ever test whether what the game plays and what
the game shows agree — and this project's own rule is that a reader has to be proved
able to fail before it is trusted.

## WHAT WOULD BE USEFUL, AND NONE OF IT IS A CHORE

A normal session doing whatever you were going to do. Trading, mining, a shop, a
scan — the ordinary things, not a demonstration. **Game sound on.** Length does not
matter much; a few minutes of ordinary play is worth more than an hour of anything
staged.

**Nothing needs to be built first and nothing is waiting on a decision.** The design
desk has stopped adding to this until something has been measured, and this is the
measurement.

## WHERE IT GOES

Anywhere in the project folder is fine — say where and it gets picked up. **No
rush on the same night; the point is that it exists, not that it exists tonight.**

---

ANSWERS:

**Done. 2026-09-09, 17 minutes 26 seconds, game sound on, ordinary play.**

    Videos\Captures\Star Citizen  2026-09-09 17-31-05.mp4     the original, untouched
    Videos\Captures\_for_analysis\session-audio.m4a           audio only
    Videos\Captures\_for_analysis\session-00..05.mp4          six pieces, picture and
                                                              sound still together

Split by Build because the whole file is over the transfer limit. **The original
is not to be moved or touched** — it is of one evening on one patch and cannot be
made again.

**Already analysed. 40 candidate sound events found; four checked against the
picture and all four are real** — shields coming up in the hangar, ready to scan,
the quantum drive spooled and ready, and a hangar request granted at a station.

**And the thing you actually wanted it for is not proved.** Matching sounds to each
other failed: the two most similar events by spectrum turned out to be completely
different moments, because the measure was matching the cockpit ambience rather
than the effect on top of it. **Locating a sound works. Identifying one does not,
yet.**

Full record and the scripts to re-run it:
`claude/VERIFIED_the-first-real-recording-forty-moments-and-a-fingerprint-that-fails-2026-09-09.md`
and `claude/audio-analysis/`.

**One thing worth your attention that nobody designed for:** at the instant those
sounds play, the game prints the event name on screen — "Hangar Request
Completed", "READY TO SCAN", "ALERT: SHIELDS DOWN". There is already a screen
reader graded at 94.8%. **That is a labelling machine sitting inside the recording,
free.** Not a build order; recorded so it is not rediscovered later.

**Two practical notes for the next recording**, both learned the expensive way.
Game Bar records whichever window had focus when recording started — three earlier
attempts captured a chat window instead of the game, one of them for six and a half
minutes. The filename is the tell. And nothing in the session tested a shop
purchase or a small confirmation beep; the four confirmed events are all large
flight-system ones, and the quiet events are the ones this design most needs.
