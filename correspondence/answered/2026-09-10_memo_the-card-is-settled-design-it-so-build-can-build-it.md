# Memo

To:      Engineering
From:    Owner
Date:    2026-09-10
Subject: the card is settled — design it so Build can build it, and here is every number
Status:  Answered

**Your two points were right and both are answered below. Everything you asked for
is decided. Design it; do not re-open it.**

---

## ONE FILE, ONE NUMBER, FOR ITS WHOLE LIFE

**Every job gets a number when it is first filed, and that number never changes.**
It goes **in the filename**, not only in the file — so a person or a program can
find it in storage later without opening anything. **I want to be able to say a
number out loud and have something go and fetch that file.**

**The file is never remade.** It is passed around and edited in place. **A desk
that answers by creating a NEW file starts a fresh count, and the loop then runs
forever with a clean card every lap. That single behaviour makes everything below
decoration.**

**This resolves the conflict in my 2026-09-08 ruling.** That ruling kept returns
out of `inbox/` because the watcher renames what it files. **With the number in the
name, the watcher preserves the number and may change the rest** — so returns can
go through the mail like everything else.

## THE COUNTERS — THERE ARE TWO AND THEY MUST AGREE

**The watcher punches.** Every time it files the job, the count goes up. **The
watcher's punch is the authority.**

**Each desk stamps** before it passes the file back — one line, always the same
shape, machine-readable. **A stamp written as prose cannot be counted and kills
the whole check.** The stamp says which desk and when.

**The punch count and the total stamp count must always be equal. ANY gap is the
flag.** That is one rule instead of thresholds, and it catches a bypass the first
time it happens rather than the ninth. **A gap means a file moved between desks
without going through the mail** — which is the one failure the watcher cannot see
by itself.

**Stamps also give the forensics.** Count per desk, not just the total, so when
something does run away I can see whose hands were on it and how often.

## FOUR, AND THEN IT FREEZES

**Four punches. Then the job stops and comes to my tray with its whole history.**

**FREEZES — not merely forwarded.** If the desks carry on working it while it sits
with me, nothing stopped. It needs a state, not just a destination.

**Only my stamp restarts the counter.** Nothing here can prove a stamp is really
mine, so **every reset is logged where I can see it.** That will not stop a forged
one; it makes one findable afterwards.

**Four is tight and I know it.** A real job might legitimately take four or five
touches, so it will sometimes fire on honest work. **Firing costs me a glance,
which is cheap. Set the number from measurement once there is a week of real jobs
— not from another guess.**

## A DESK ALSO CHECKS THE STAMPS BEFORE IT WORKS

**A desk that opens a file and sees a count already past four sends it to me
instead of working it.** That is the backstop for a bypass the watcher never saw.

**It is a second pair of eyes and it is NOT a control.** It depends on a desk
choosing to obey, and today's own research measured that failing: the rule present,
unchanged, read at startup, with a dedicated tool, and long-running sessions
stopped acting on it anyway. **The watcher's punch is what actually stops it.**

## STUCK IS MEASURED BY SILENCE, NOT BY TIME

**No time limit on a task. Some real work takes hours.**

**Forty-five minutes with nothing written anywhere, and it surfaces to me.** What
separates working from stuck is whether it is still producing. That test worked
twice tonight — a desk that had written nothing for ninety minutes was hung, and
one producing files every few minutes was fine.

**The number is thin and I want that said plainly: twelve gaps from one evening,
and the longest honest gap in them was over an hour and a half. Thirty minutes
would have fired on real work.** Re-set it from measurement, not from argument.

## THE OTHER TWO NUMBERS

**A daily ceiling on total wakes, separate from the four.** Twenty jobs at three
punches each is sixty wakes and every card is legal. Over the ceiling the watcher
stops waking anything and tells me.

**A job with no punch at all never reaches four and never reaches me.** Silence is
invisible — the forty-five minute rule covers a stuck run; **an untouched job
sitting in a tray needs its own age rule.**

## YOUR TWO POINTS

**Rule 9 is not the watcher's job and you are right.** Whatever launches a desk
launches it **without** deploy, commit, push, delete, spend or credential tools.
Anthropic's own reference is explicit that deny rules remove a tool rather than
prompting for it, and that `--allowedTools` restricts nothing. **Prove it by trying
to deploy and being refused. A desk that simply does not try proves nothing.**

**Rule 3 only stops a desk talking to itself and you are right.** The card is the
answer to two desks talking forever. **And it beats counting per desk-pair, which
was the other option: a pair count misses three desks going round in a circle. One
card on the job catches that and everything else.**

---

## ONE PROCESS THING, AND IT IS NOT SMALL

**You asked me three questions in a chat window instead of putting them in my
tray.** I read them thinking they came from somewhere else, and the answers went
where nothing could file them.

**A desk's question to me goes in `correspondence/open/owner/`. Always.** Chat is
me typing live at a desk; it is not a desk's route to me. **The whole point of the
tray is that an answer lands somewhere it can be found again.**

---

## WHAT I WANT

**A design Build can execute, with every number above in it.** Then the rest of
your automation list: the returned state, the wake itself, the RAPTOR ruling that
is blocking B2, the RSI sweep folded in, and the desk list derived from the trays.

**Nothing runs unattended until Build has proved a single headless run and I have
seen the result.** Not tonight.

---

ANSWERS:

**Architecture, 2026-09-10. Designed and filed:
`claude/DESIGN_the-doorbell-the-job-number-and-the-punch-card-2026-09-10.md`.
Every number you gave is in it. One of your rules will fire on normal work as
written, and two numbers are still missing — both in your tray, not here.**

## THE ONE CORRECTION, AND IT WOULD HAVE KILLED THE CONTROL IN ITS FIRST WEEK

**"The punch count and the total stamp count must always be equal."**

**They are never equal while a desk is working.** The watcher punches when it files.
The desk stamps when it finishes. **Between those two moments punches are one ahead
— and that is every job in flight, all the time.**

    punches - stamps == 0     at rest, waiting to be filed onward
    punches - stamps == 1     a desk is holding it. NORMAL.
    anything else             THE FLAG

**As strict equality it goes red on every live job and gets switched off by
Friday.** The intent is exactly right and survives untouched: a gap means a file
moved without going through the mail, which is the one failure the watcher cannot
see by itself. **Only the arithmetic needed the in-flight case.**

**And the two directions mean different things.** Stamps two or more BELOW punches:
a desk was handed the job and passed it on without stamping. Stamps ABOVE punches:
**a desk touched a job the watcher never gave it — that is the bypass, and it is
the worse direction.**

## WHERE YOU BEAT THIS DESK, RECORDED BECAUSE IT MATTERS WHO WAS RIGHT

**The per-pair count is dropped and your reason is better than my proposal.** A
pair count misses three desks going round in a circle. One card on the job catches
that and everything else.

**You found the hole in your own answer before anyone else did** — a new file
starts a fresh count and the loop runs forever with a clean card every lap.

**And the number in the filename resolved a conflict in your own 2026-09-08 ruling.**
Returns were kept out of `inbox/` because the watcher renames what it files. With
the number in the name it preserves the number and may change the rest, so returns
go through the mail like everything else. **One route in, which is what the mail was
for.**

## THREE ADDITIONS, NONE OF THEM RE-OPENING ANYTHING

**A RESET COUNTER THAT NEVER RESETS.** You asked for every reset logged so a forged
one is findable. A counter does better: a forged reset can lie about who did it, **it
cannot hide that a reset happened.** A job showing three resets is loud without
anybody reading a log, and it survives the log being lost.

**"NOTHING WRITTEN ANYWHERE" IS TOO BROAD TO BE A TEST.** A desk writing a scratch
file every minute while achieving nothing looks perfectly alive. **It needs a short
named list of what counts as production** — a memo, a repo file, a deliberate log
line — or the silence rule is satisfied by a process that is only breathing.

**YOUR OWN TRAY IS NOT A LAP.** A job that comes to you and goes back should not
spend a punch on the trip.

## ON THE FREEZE, PRECISELY

**Movement is enforced, tampering is detected.** The watcher refuses to file a
frozen job to any desk and refuses to punch it — that part is real, because movement
is the watcher's. **A desk editing the file in place in your tray cannot be
prevented**, but its stamp then has no punch behind it, which is the flag above.
Stating it exactly so nobody later believes the freeze is stronger than it is.

## AND ONE CHEAP DETECTOR FOR THE NEW-FILE LOOP

Not a rule, and not to be built yet — a number worth watching on the same principle
as your four and your forty-five: **the rate at which new job numbers are issued.**

Six new numbers between the same two desks inside ten minutes, while nothing else
moved, is not work. **Legitimate work does not open six jobs between two desks in
ten minutes; a ping-pong wearing a fresh card every lap does exactly that**, and it
does it long before a daily total is reached.

## THE PROCESS CORRECTION IS TAKEN

**My three questions went in a chat window and the answers landed where nothing
could file them. That was mine.** A desk's question to you goes in
`correspondence/open/owner/`, always. The two numbers still missing are already
there under their own job, and this is the last time a question of mine reaches you
any other way.

## WHAT IS STILL YOURS — IN YOUR TRAY, NOT HERE

The daily wake ceiling, and the untouched-job age rule. **"Eight" was said before the
four-punch card existed and may have meant the punch limit; I have not assumed either
way.** Everything else is decided and Build can execute it.
