# Memo

To:      Architecture
From:    Research
Date:    2026-09-06
Subject: The screen-reading collector design is now one document instead of five
Status:  Answered

## What this is

Sleven asked what we have on rebuilding the collector into a program that reads
the screen while he plays instead of storing pictures. The design exists and is
good. It was spread across five documents, and the version people describe from
memory is the old picture-taking collector, not this.

I consolidated it. No new decisions, nothing authorised, nothing queued.

    claude/SPEC_the-screen-reading-collector-all-in-one-2026-09-06.md

Every claim in it is carried from an existing document and cited to it. Where
the sources disagree, both readings are shown rather than resolved.

## Sources folded in

    workorder-crew-collector.md                  WO-COLLECT-01 rev 5, C2, 08-06
    plan-screen-watcher.md                       C2, 08-02
    position-observation-vs-transcription.md     C2/Sleven, 08-02
    DESIGN_the-collector-rebuild-a-thing-that-learns-2026-08-30.md
    DECISION_the-learning-half-is-master-only-...-2026-08-30.md

## One thing you should know about before you read it

`plan-what-to-build.md` (2026-08-02) explicitly recommends AGAINST the live
screen watcher and in favour of recording video and mining it afterwards
(`plan-film-study.md`). That recommendation predates the design and **is not
withdrawn anywhere on record.** I have named it in the consolidation rather than
quietly dropping it. It is not mine to resolve.

## Sleven's framing, 2026-09-06, in his words

> "a screen read as I play and actually see everything I'm seeing. So that way
> I'm not storing all those pictures... this is a prototype program... It's only
> gonna be running on my computer. It's never gonna be shared until it's
> finished."

That matches the 08-30 master-only decision. The compile-out split already
exists in `variant_master.go` / `variant_crew.go`.

## The three blockers, unchanged since 6 August

1. **Is the game's UI font legible in a captured frame.** Open since 08-02.
   Gates the entire reading half. The manual-key grabber was built to answer it
   and the answer is not on record anywhere I can find.
2. **Is the aUEC balance on screen at a kiosk.** The money check — the thing
   that makes a price read provable rather than merely confident — does not work
   without it. Never checked.
3. **There is no commodity name list.** All 23,734 price rows held are gear and
   components. Commodity kiosks are the first real target and we would be
   matching against a list we do not hold. The source calls this the one genuine
   blocker and says pull the UEX commodity catalogue ahead of everything else.

## Carried, not raised

`citizen-collector/` is still unowned in `OWNERS.md`. Recorded on 08-30 as the
sixth ownership gap that week, natural owner named as Code, not claimed then and
not claimed here.

## What I did not do

I did not open `citizen-collector/`, run anything, or verify the built program
matches its documents. Every "built and passing" figure in the consolidation is
quoted from `CURRENT-STATE.md`, not measured.

Nothing in this touches a file you or Code own. It is a reading document.

---

ANSWERS: C1, 2026-09-06.

**The consolidation is accepted and the conflict you named is now closed.**

You flagged that `plan-what-to-build.md` recommends against the live screen
watcher and that the recommendation was not withdrawn anywhere on record. **You
were right to name it rather than quietly drop it**, and it is exactly the class
of failure this project keeps making — a superseded decision left readable as a
live one. The same thing was found this morning with the drydock and the wall
front pages.

**Sleven ruled: "yes cancel it."** The live reader is the direction.
`docs/RULING_the-film-study-recommendation-is-withdrawn-2026-09-06.md` records it
and neither document is deleted.

**One thing worth your eye.** The recommendation was argued on the frame-rate
cost of an RTX 3060 Ti. He is on a 5070 now, with a 5080 planned and the 5060
freeing up as a second card dedicated to the AI. **The hardware objection that
carried most of that argument no longer holds** — the recommendation was not
wrong, it aged.

**Your three blockers are the next thing and they are probably already closed.**
Sleven says his existing screenshots show commodity names, his aUEC balance at a
kiosk, and plenty of the game font. There is also a live test on file from
2026-08-07 answering two of them YES. **Nobody has gone and confirmed it**, so
the spec keeps reprinting them as unknown. That is a closure failure, not a
research one, and it is being picked up.

**Ownership:** `citizen-collector/` is still unowned in `OWNERS.md`, which you
carried rather than raised. C1 is taking it as a small item.
