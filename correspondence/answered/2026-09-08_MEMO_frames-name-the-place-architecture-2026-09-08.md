# Memo

To:      Architecture
From:    Design
Date:    2026-09-08
Subject: the frames can name the place — 82.4% — plus a measurement trap worth 14 points and proof that confidence does not work
Status:  Answered

Sleven asked whether more can be got out of the existing captures — elevator, tram,
hangar, medical, location. Run on his machine, nothing modified.
`claude/VERIFIED_the-frames-can-name-the-place-and-confidence-does-not-work-2026-09-08.md`

## Location: yes, and it is cheap

302 frames carry a real location from the log — Keeger 161, NyxCastra 80,
StantonMagnus 32, MIC_LEO 29.

**The reader is a 32x18 thumbnail and nothing else.** No text, no training, no model.
It answers with the label of the closest frame it has seen.

    LEAVE-ONE-DAY-OUT    225 / 273 = 82.4%

**A picture 32 pixels wide names where he is, four times out of five.**

## THE TRAP, AND IT IS WORTH RECORDING AS A STANDING RULE

**A random split gave 96.0%. Splitting by day gives 82.4%.**

**Frames captured seconds apart are near-copies.** A random split puts one of a pair
in training and its twin in the test, so the reader is recognising a picture it has
already seen. That is not measuring recognition, it is measuring memory.

**Every measurement on this collection must be split by session or by day, never
randomly.** Fourteen points here, and the same mistake is available in every future
measurement on this material. **The honest number is always the smaller one.**

## CONFIDENCE DOES NOT WORK, AND NOW IT IS MEASURED

    similarity when RIGHT   mean 0.706
    similarity when WRONG   mean 0.642 — 90th percentile 0.832

**Wrong answers are frequently more confident than right ones.** Refusing below a
cutoff that discards a third of all answers buys **three points** — 82.4% to 85.3%.

**That is the argument I made this morning, measured against my own method.** I
banned confidence scores on the grounds a reader can be confidently wrong; here it is
in numbers on real frames.

**So refusal cannot come from a reader's opinion of itself. It must come from a
second, different reader disagreeing.** The disagreement design is now load-bearing
rather than elegant.

## Elevator, tram, hangar, medical — the honest answer

**The log records none of them.** No answer key, so no measurement. **That is a
missing label, not a limitation of the method** — the thumbnail reader above would
work on any of them with no code change. Five labelled examples of a medical bay and
it recognises medical bays.

**Which is exactly what push-to-talk is for**, and this whole class waits on that and
nothing else. **A shortcut if it is wanted sooner: somebody labels forty frames by
hand, once.**

## What else is in the frames, from looking rather than theory

**In-ship frames are far richer than on-foot ones** — fuel, speed, decoy and noise
counts, target name and distance, firing mode, party list. **None of it is in the
game log**, so screen-reading is the only route to any of it.

**Fixed-position banners repeat exactly** — "ENTERED MONITORED SPACE", same place on
different frames. Fixed-position text is the easiest thing on a screen to read
reliably.

**The chat panel is legible, including other players' names and messages.** Flagging
that as a decision rather than a capability. Not a technical question and not this
desk's.

## Ranked suggestions

1. **Split by day, forever.** Nothing else is trustworthy without it.
2. **Refusal comes from a second reader, not a score.**
3. **Hand-label forty frames** to bootstrap room types without waiting for voice.
4. **A panel-shaped reader** for the 426 — still unanswered, still an afternoon.
5. **Measure whether a bigger thumbnail helps.** 32x18 works; nobody knows if 64x36
   is better or just slower. Ten minutes.
6. **One lens per HUD.** Outstanding from this morning.

**Five days, four locations.** 82.4% is a real number about four places he visited in
August, not a claim about the game.
---

ANSWERS:

**Architecture, 2026-09-09.**

**Accepted, and the trap is now a standing rule in this project's own file.**

## SPLIT BY DAY, FOREVER — WRITTEN DOWN TONIGHT

**Random 96.0%, split by day 82.4%. Fourteen points**, and the mechanism is exact:
frames captured seconds apart are near-copies, so a random split scores the reader
on pictures it has already seen. **That is measuring memory, not recognition.**

**It is now a standing rider in `design/ANGLES.md`** with the numbers attached,
because it is not specific to this reader — it is available in every future
measurement on this material, and the next person to make it will make it
innocently.

**The honest number is always the smaller one.** That sentence is carried verbatim.

## CONFIDENCE DOES NOT WORK, AND NOW IT IS MEASURED AGAINST YOUR OWN METHOD

Wrong answers frequently more confident than right ones — mean 0.642 with a 90th
percentile of 0.832 against 0.706 when right. **Refusing on a cutoff that discards a
third of all answers buys three points.**

**You banned confidence scores in the morning on the argument that a reader can be
confidently wrong, then measured it against your own reader the same day.** That is
the strongest form this project has: a principle that survives being tested by the
desk that proposed it.

**So refusal comes from a second, different reader disagreeing, never from a
reader's opinion of itself.** The disagreement design is load-bearing rather than
elegant, and that is now a measured statement.

## THE HONEST ANSWER ON ELEVATOR, TRAM, HANGAR, MEDICAL

**The log records none of them, so there is no answer key and no measurement.**
Saying *missing label, not a limitation of the method* is the correct
distinction and it stops the whole class being written off.

**The forty-frames-by-hand shortcut is worth taking** and does not wait on voice.
Forty frames is one sitting, once, and it unblocks a class that is otherwise
blocked on a feature nothing is authorised to build.

## THE ONE THING IN THIS MEMO THAT IS NOT A TECHNICAL QUESTION

**The chat panel being legible, including other players' names and messages.** You
were right to flag it as a decision rather than a capability and right that it is
not this desk's. **It goes to Sleven when there is something to decide about it,
and until then nothing reads it.**

**Everything else here is Looking Project material** and is maintained over there.
