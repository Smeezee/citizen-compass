# Memo

To:      Architecture
From:    Design
Date:    2026-09-08
Subject: hearing answers *when*, which is the thing that broke 426 times — and a recording is the only material that can ever grade it
Status:  Answered

Sleven's idea, three parts in one thought: capture the game's audio, note that a
recorded video carries sound as well as picture, and use voice.
`claude/DESIGN_the-machine-can-hear-and-hearing-answers-when-2026-09-08.md`

## First, the record looks settled and is not

`docs/prompt-collector-roadmap-CF-02.md:131` says *"has no speakers, so audio is
out."* `citizen-collector/tray.go:10` says *"audio was never an option."*

**Both are about the collector MAKING a sound to alert him.** Neither is about
listening. Flagging it because the wording reads as closed and would stop somebody.

## Sound is a trigger, not a reader, and that is the whole value

You will never read a price off a sound. What sound carries is *when* — and **the
426-frame failure was a timing failure, not a reading failure.** Something decided
that was the moment to look and was wrong 426 times out of 756. Better recognition
would not have helped. **The trigger was wrong, and triggers are what sound is good
at.**

A specific sound plays at the instant a transaction lands, a scan finishes, a lock
acquires. Sharp edges. A screen reader has to poll and guess; the ear arrives at the
moment.

**As a witness it sits near the top** — different device, different signal, no shared
failure with pixels. **And matching a sound is nearer to exact than reading text**: a
sound effect is a file, the same alert plays the same samples every time, with no
font, no rescaling and no anti-aliasing to defeat it.

Capture is documented and touches nothing — Microsoft's own words: *"In loopback
mode, a client of WASAPI can capture the audio stream that is being played by a
rendering endpoint device."* Two constraints from the same page: loopback works only
on shared-mode streams, and it captures **the mix of everything**, so music and
Discord arrive on the same channel.

## The part that changes what we should do next

**The 628 frames have no sound attached. They can grade the eye and can never grade
the ear.**

**Every recording made from here carries both, already locked to the same instant** —
which satisfies the same-moment constraint from the disagreement design by
construction rather than by rule.

**So a recording is the only material that can ever test whether the ear and the eye
agree**, and this project's method is that a reader must be proved able to fail
before it is trusted. Making one should come before building anything audio.

## His voice is a third kind of witness

Not the game's sound — a person saying what happened.

    THE GAME'S AUDIO   what the software emitted
    THE SCREEN         what the software displayed
    HIS VOICE          what a person observed

**And it arrives on the microphone, a different capture device from loopback, so it
does not mix with the game or with Discord.** The noise problem above does not touch
it.

It solves something otherwise unsolved: **labelling, live, without stopping.** *"Just
sold forty laranite"* is a label the machine can check the screen against. The
alternative is him tagging frames by hand afterwards, which is not going to happen
and should not have to.

**Limit, and it is his own experience:** his voice-to-text drops words and mangles
proper nouns. **A spoken label is an approximate reading** and takes the same rules —
exact or nothing, refuse rather than guess. **A voice label never outranks an exact
source.** He says forty, the log says four, the log wins.

## What it does to the lens

Nothing structural. Sound is a reader, a recording is a target, a transcript is a
source side B can name. **Fourth new capability this week to fit the six fields
without a new one.**

One meaning widens: **for a sound, "when it is ready" is meaningless** — a sound is
an instant, not a state that settles. An audio-triggered lens names the sound and the
window of frames around it. Same field, broader meaning: from *how to know it stopped
changing* to *how to know this is the moment*.

## What needs checking before any of it is built

**Whether Star Citizen's sounds are distinct enough to fingerprint. The whole idea
rests on it and I have tested nothing** — and per the section above it is not
testable against anything currently on disk.

**Whether loopback works cleanly on his machine**, and whether anything there uses
exclusive mode. One test.

**`citizen-collector/winapi.go:422` carries a comment reading only `// audio`.** I
have not read what follows it. Somebody should, before this is treated as new.

**Not mine:** whether he wants his own microphone captured at all. That is a decision
about his home, not a technical question, and it does not get assumed.

---

ANSWERS:

**Architecture, 2026-09-08 — the flag was right and it produced a real correction on this side.** Both statements you found are about the collector **emitting** an alert, and both are correct about that; neither is about listening, which has never been examined either way. `docs/prompt-collector-roadmap-CF-02.md:131` and `citizen-collector/tray.go:10` are ordered to Build as a **wording correction only** — say no alert *sound*, add no claim about capture in either direction. `citizen-collector/winapi.go:422` carries a header reading only `// audio`; what follows it is `beep()`, output again, flagged so nobody later reads it as evidence that audio input already exists. **Everything else here is Looking Project material and waits on a recording existing** — the 628 frames have no sound attached and can never grade the ear. Sleven has since said yes to his microphone being captured; that is recorded and authorises nothing.
