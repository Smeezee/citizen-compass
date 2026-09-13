# RULING — the recommendation against a live screen watcher is withdrawn. Two things it was right about are not.

    from      Sleven, 2026-09-06. Filed by C1.
    closes    the open conflict C3 named: `plan-what-to-build.md` (2026-08-02)
              recommended AGAINST the live screen watcher in favour of
              recording sessions and mining them afterwards
              (`plan-film-study.md`), and that recommendation had never been
              withdrawn on record.

---

## The ruling

**Sleven: "yes cancel it."**

The live screen reader is the direction. It matches what he has said all along
about the rebuild — *"a screen read as I play and actually see everything I'm
seeing. So that way I'm not storing all those pictures."*

**So `plan-what-to-build.md`'s "what I would NOT build: the live screen watcher"
is withdrawn, and `plan-film-study.md` is no longer the recommended route.**
Neither document is deleted. Both stay readable; neither is a live proposal.

## Why the recommendation was reasonable when written, and why it is not now

**Its cost argument was measured against an RTX 3060 Ti.** The whole "recording
is near-free, live reading steals frames" comparison rests on that card.

He is on a 5070 today, the 5080 is planned, and the 5060 frees up as a **second
card dedicated to running the AI so it never competes with the game.** The
hardware objection that carried most of the argument no longer holds.

## Two things film study was right about, and they do not go away

**These are not reasons to reverse the ruling. They are things the live reader
will lose unless it is designed not to.**

**1. A live reader throws away everything it did not think to capture.** Footage
can be re-mined next year with a better reader, for a question nobody has asked
yet. A live read is one shot, in motion, and what it missed is gone forever.
`plan-film-study.md` put it plainly: *"data not captured is gone forever"* against
*"re-analyse old footage for something we had not thought of."*

**2. The frames were going to be the picture archive.** `plan-film-study.md` §4
noticed that a recorded session already contains a shop photo, a location photo
and a station approach, each stamped with patch, time and place. **That is the
exact problem Sleven spent this morning solving by hand, page by page, on the RSI
store.** Worth knowing the cheaper answer existed on paper.

## The hybrid nobody has ruled on, raised not proposed

A rolling buffer — the last few minutes held in memory, written out only when
something interesting happens. NVIDIA's instant replay already works this way and
`plan-film-study.md` §5 calls it Mode B.

**The collector reads live AND keeps a short tail around the moments it flagged.**
Storage stays small because nothing is kept unless the reader thought it
mattered, and the two losses above mostly close.

**This is C1 raising a question, not proposing a design. The collector rebuild is
still being designed and it is Sleven's.**

## What this does not touch

Nothing about the reading method, the trigger layer, the learning requirement or
the module boundaries. Those are open and his.

*C1, 2026-09-06.*
