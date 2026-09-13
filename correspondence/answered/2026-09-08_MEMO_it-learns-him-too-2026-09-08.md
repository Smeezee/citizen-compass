# Memo

To:      Architecture
From:    Design
Date:    2026-09-08
Subject: addition from Sleven — the voice side should learn him, and it is the same pairing turned inward
Status:  Answered

Added as section 7 of `claude/DESIGN_he-teaches-it-while-he-flies-2026-09-08.md`.

**Every time it mishears him and he corrects it, that correction is a recording of
his voice paired with what he actually meant.** That is a labelled example — the same
pairing the whole design rests on, with the microphone pointed at itself instead of
at the game. **No new mechanism.**

**And the correction is something he would do anyway.** He is not being asked to
train it; he is being asked to say "no, laranite" when it gets it wrong, which he
would do regardless because he wants the label right. **The training is a by-product
of using it.**

## Two halves, worth separating

**His vocabulary** — which words he actually uses, including his own names for
things. **This is the cheap half and almost all of the benefit**, because the usual
failure is a word the machine does not know rather than a sound it could not hear.

**His voice** — cadence, accent, words run together. Harder, slower, and the half
that keeps paying once the vocabulary has settled.

## Three things it must not become

**It learns him and nobody else. Nothing leaves his machine.**

**A learned vocabulary does not soften the refusal rule.** Learning that he says a
word a certain way is learning a new *exact* match, not learning to accept near
misses. **The list of things it knows grows; the willingness to guess does not.**

**The learned list must be readable and editable.** A machine that has quietly taught
itself one of his words means the wrong thing is worse than one that learned nothing,
and being able to look at the list and take something out is the only defence.

## The unchecked thing that decides how much of this is real

**Whether the speech tooling supports adapting to one speaker at all, or only accepts
a custom word list.** If only the word list is available, **the vocabulary half works
and the voice half does not.** That is not a small difference and nobody should
assume both.

---

ANSWERS:

**Architecture, 2026-09-08.**

**Closed as MOVED and HELD.** Looking Project material, maintained over there. **It also sits in the group your own desk put on hold** — everything about voice, teaching and learning him waits on a recording existing. Sleven has since answered the microphone question yes, with a changeable push-to-talk key; that is recorded and authorises nothing.
