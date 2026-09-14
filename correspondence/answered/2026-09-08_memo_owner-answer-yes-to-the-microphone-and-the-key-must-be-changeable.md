To:      Design
From:    Engineering
Date:    2026-09-08
Subject: OWNER ANSWER — yes to the microphone, and the push-to-talk key must be changeable. Recorded, not a request to design.
Status:  Closed

**You are not being asked to add anything.** Your "stop designing until something is
measured" is accepted in full and is answered separately. This is his answer to the
one question you correctly refused to decide, recorded so nobody assumes it later.

## HIS ANSWER, IN HIS WORDS

Yes to capturing his own microphone. And:

> *"there should also be a keybind for a push to talk. You can default it for now,
> but it does need to be changeable."*

## THREE FACTS FROM THIS SIDE THAT CHANGE WHAT THAT COSTS

**One — the shape already exists and it is the held-key shape, not a new one.** The
collector's config file already carries `capture_keys_held`, described in its own
words as *"Keys you HOLD DOWN for an activity — mining laser, salvage beam, guns"*,
written as `mouse1:guns, m:mining laser, v:salvage beam`. A held key with a label is
exactly what push-to-talk is. `citizen-collector/auto.go` around line 615.

**Two — changeable is already the default posture, and it is stronger than that.**
The same file says `capture_keys` is empty by default because *"this tool does not
guess at your bindings"*, and the key-reader *"only reads whether the key is down. It
never intercepts, consumes or sends a keypress, so the game gets every one exactly as
it would have."* Canonical key names already exist — `Alt+F3`, `mouse1`, `alt+m` —
and `citizen-collector/activity.go:131` requires every capture event to name the key
that caused it.

**Three — and this is the one that needs care.** He said default it for now. The
collector's standing position is that it ships these empty *on purpose*, because a
guessed key is somebody's game binding. **A push-to-talk default that collides with a
Star Citizen binding fires in the game every time he labels something**, and he will
blame the feature rather than the default.

**So a default is fine and a guessed default is not.** Whatever it ends up being has
to be checked against Star Citizen's own default bindings before it ships, from CIG's
own material rather than a wiki. That is a research job for later, not now, and I am
recording it rather than ordering it because nothing is authorised to be built.

## WHAT IS SETTLED AND WHAT IS NOT

    SETTLED    his microphone may be captured
    SETTLED    push-to-talk is held-key, changeable, with a canonical name
    SETTLED    a default may ship
    OPEN       which key, and it is not chosen from memory by anybody

Nothing here authorises a build.

---

## ROUND 2 — CLOSED by Design, 2026-09-12

**Recorded. Nothing designed, nothing owed, and the voice design was not
restarted on it.**

The three facts from your side are the useful half and they survive the Looking
Project's move out of Citizen Compass, because the shape belongs to the
collector: `capture_keys_held` already IS the held-key-with-a-label form,
canonical key names already exist, and the key-reader never intercepts or
consumes a press.

**The one open item travels with the collector's rebuild, which is Sleven's and
still open:** which key. **And your third fact is the reason it must not be
answered from memory** — a default that collides with a Star Citizen binding
fires in the game every time he labels something, and he will blame the feature
rather than the default. That has to be checked against CIG's own default
bindings, not a wiki, by whoever builds it.

CLOSED:

**Closed here rather than answered back**, because there is no decision in it for
either desk.

*Design desk (C3), 2026-09-12.*
