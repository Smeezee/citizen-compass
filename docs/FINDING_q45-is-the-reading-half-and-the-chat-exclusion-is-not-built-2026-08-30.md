# FINDING — Q45 is the reading half arriving, and the chat-region exclusion it names as a prerequisite does not exist in code

    from    Code, 2026-08-30
    method  read the Go source, the rev 5 handover, and the consent selftest
    status  REPORTED. Nothing edited. Q45 not started on top of it.

---

## 1. THE PROMISE, WHICH IS SHOWN TO THE PERSON

`citizen-collector/consent.go:108`, in the text a user reads before agreeing:

    WHAT IT NEVER READS
      - Any other program. It checks the window belongs to Star Citizen first.
      - Your chat. Chat is never sampled, at all.

`consent_selftest.go:180` guards it, and its own comment says why:

> *"Chat exclusion and the manual-only rule are the two promises this project
> has treated as absolute from the start, and a rewrite that quietly drops one
> is a regression even though nothing false was added."*

## 2. THE SPECIFICATION, WHICH IS UNAMBIGUOUS

`docs/HANDOVER-collector-rev5-COMPLETE.md` §4.12:

> **Hard exclusion, not filtering. A filter can fail open; an excluded zone is
> never read, so there is nothing to leak.**
>
> **Zones overlapping the chat region are never sampled.** Not read and
> discarded — **never read.** Set at first run, part of consent.

## 3. IT IS NOT IMPLEMENTED

    grep chatRegion|chat_region|excludeChat|skipChat|TIER 2.3   ->  nothing
    the only "chat" in Go   consent.go:108        the promise itself
                            consent_selftest.go   asserts the PHRASE survives

**The selftest verifies the sentence is still on the screen. It cannot verify
the behaviour, because there is no behaviour to verify.** That shape - a check
confirming a claim is STATED rather than TRUE - is the one this project calls
silent success, and it is worth naming even when the underlying state is fine.

`cropToWindow` (`capture.go:176`) crops to the Star Citizen **window**. The chat
panel is inside that window, so a capture taken while chat is open contains chat.

## 4. AND TODAY THAT IS FINE, WHICH IS THE PART THAT MAKES THIS FAIR

`main.go:9`:

> *"NO OCR. No atlas. No vocabulary. No zones. Those are the reading half."*

**Nothing in the collector reads text out of a frame.** Captures are images kept
on the person's own disk. "Chat is never sampled" is true in the only sense that
is currently available: nothing is sampled, from anywhere, because the sampler
does not exist.

**No promise is being broken today and nobody shipped anything false.**

## 5. WHY IT MATTERS NOW, AND ONLY NOW

**Q45 is the reading half.** Its DONE-WHEN is a store of

    the image region, the exact text, which screen it came from, the build,
    the moment

**"The exact text" is text read out of a frame.** The day that ships is the day
"chat is never sampled" becomes a claim about behaviour rather than about an
absent feature — and on that day the exclusion has to already exist, or the
sentence on the consent screen stops being true.

**C1 already said this**, and is right: *"the chat-region exclusion (rev 5 TIER
2.3) is a prerequisite rather than a nicety."* What C1 may not know is that it
is a prerequisite that has not been built.

## 6. AND THE SPEC RECORDS AN OPEN QUESTION THAT DECIDES THE DESIGN

§4.12, unanswered:

> **[C1] Is the chat region at a fixed position across UI scales?** If not, the
> exclusion must be drawn by the player at first run. I do not know the answer.

**That is not a detail — it decides whether the exclusion can be computed or
must be consented to.** "Set at first run, part of consent" in the same section
suggests the second, which makes it a consent-flow change rather than a
geometry constant.

## 7. WHAT I AM NOT DOING

**Not editing `consent.go`.** Hard rule 8 puts legal and consent wording with
Sleven and says to report a gap rather than fix it. **The wording is not the
problem** — the wording is a promise worth keeping, and the honest fix is to
build what it describes.

**Not starting Q45's pair store** on top of a missing privacy prerequisite. The
order says build Q45 before the reader; this finding says one specific piece of
the reader has to come first, and that is a question for Sleven rather than a
call I make by starting to type.

## 8. THE THREE ROUTES C1 RE-OPENED, ONE OF WHICH IS RULE 8'S

Q45 records community models, `Data.p4k` extraction and photographing the
inspect view as routes ruled out too fast. **`Data.p4k` extraction carries a
rights question that hard rule 8 puts with Sleven alone**, and C1 flagged it as
such. Recorded here so it is not quietly inherited as settled by whoever builds
the recogniser.
