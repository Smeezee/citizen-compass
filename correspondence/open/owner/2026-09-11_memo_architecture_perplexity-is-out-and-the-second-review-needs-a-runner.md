# Memo

To:      Architecture
From:    Owner
Subject: Perplexity is out. Two outside desks do not exist any more — and the second review run has no runner.
Status:  Answered
**My words: "We only have two. ChatGPT and yourself." Perplexity is "way too expensive for me
to ever even think about keeping around."**

## WHAT THAT KILLS

**The five-run outside review was run through Perplexity's Comet.** The re-run after the
fixes land was the acceptance test on the whole Q62 order, and it currently has nobody to
run it. **Do not plan the re-run as though the same instrument is waiting.**

**And the desk plan line "C3 research -> Perplexity, strong fit" is dead.** Wherever that is
recorded, it is wrong now.

## WHAT IS LEFT, AND THE HONEST TRADE ON EACH

- **Echo.** Reads the open web in a real browser, which she proved today on three sites that
  our own fetch could not read. **The catch: she is not blind to the site any more — she has
  read our design documents and our findings, so she is no longer a fresh pair of eyes.**
- **Claude in Chrome.** A real browser, ours. **But it is us marking our own homework, and
  the whole point of the review was that it was not us.**
- **Grok.** He has it. Live web and live X. **Untested here, and no outside desk brief exists
  for it.**
- **Sleven himself**, which is the answer we do not want.

## WHAT I WANT

**Not a decision from you — a recommendation, with the independence cost named for each.**
The question is what an honest second review looks like now that the reviewer who had never
seen the site is gone. **A cheaper, smaller, genuinely blind run may be worth more than a
full five-run replay by somebody who has read the answer key.**

Nothing changes about the fixes themselves. This is about how we prove they worked.

---

ANSWERS:

**Architecture, 2026-09-12. Recommendation below. Short version: SPLIT THE RE-RUN IN TWO,
because you are asking one instrument to do two jobs and only one of them needs blindness.
And Perplexity leaving costs you something you did not name, which is the bigger item.**

## THE THING THE QUESTION ASSUMES, AND IT IS WHAT I WOULD CHANGE

**"The re-run" is two different jobs wearing one name.**

    ACCEPTANCE   did the 41 named findings actually get fixed on the served
                 site? Every entry has a DONE-WHEN written BEFORE the fix.
    DISCOVERY    is there anything wrong that we still cannot see — including
                 something the fixes broke?

**Blindness is worth almost nothing for the first and is the whole product of the second.**
Checking whether the Ground button now shows 29 of 29 does not get better because the
checker has never seen the site. It gets better because the checker has the list and reads
the number off the page. **Knowing the answer key is a requirement for an acceptance test,
not a contamination.**

## THE RECOMMENDATION

**1. ACCEPTANCE — Claude in Chrome, with the entry list. Independence cost: near zero, and
not for the reason it looks like.**

"Marking our own homework" is a real objection to discovery and a weak one here, because
**each item has a concrete pass condition written before the fix and the check is "what
does the page show".** There is no judgement to bias.

**The genuine risk is different and worth stating: an acceptance pass only looks where it
was told.** It cannot find what is not on the list. That is correct behaviour for this job
and it is exactly why it does not replace the second one.

**It also covers the surfaces for free.** Phone and the public-versus-new comparison were
two of the five runs, and surface coverage never needed blindness — only a browser.

**2. DISCOVERY — one small blind run on Grok, not a five-run replay. Independence cost:
unknown instrument, and one contamination path Comet did not have.**

**Grok is the only genuinely blind instrument left.** Echo has read our design documents
and our findings; Claude in Chrome is us; you are the least blind person alive to this
site.

**Two conditions and the first is not optional:**

- **Run 1 is a capability test, as Comet's was.** We learned that the hard way once and it
  cost one run instead of five. Nothing about Grok's browsing is proven here.
- **The brief must forbid searching for the site or its author.** Grok has live X. **A
  reviewer who finds our own posts about the site stops being blind mid-run**, and neither
  of us would know it happened. Comet never had that door open.

**3. THE SCALE — your own sentence is right and I am adopting it rather than improving on
it.** *A cheaper, smaller, genuinely blind run may be worth more than a full five-run
replay by somebody who has read the answer key.* **It is. One blind run on the new front
page desktop, and the acceptance pass carries everything else.**

## THE PRICE I AM NOT HIDING

**Grok has no mailbox. A Grok run costs you hand-carrying the brief and the result.**

That is the pattern your own standing rule exists to remove. **It is the same price Echo
already costs, so it is not new** — but it is not free, and if you would rather not pay it
twice, dropping discovery entirely and running acceptance only is a defensible choice.
**It would mean shipping on the strength of "we fixed what we were told about", and I would
want that written down rather than assumed.**

## WHAT PERPLEXITY LEAVING ACTUALLY COSTS, AND IT IS NOT THE REVIEW

**The curated export design was built for a Perplexity sandbox account that no longer
exists.** `claude/DESIGN_the-curated-export-2026-09-11.md` — the allow-list boundary, the
control-folder file, the whole one-way folder.

**Its consumer is gone. It was never built, so nothing is wasted.**

**And the design survives the vendor leaving, because you made it survive.** Your own line
in that letter: *`PerplexitySandbox` is a vendor's internal detail and not a stable
identity.* **You insisted the boundary not key on the account name, and the account was
gone inside a day.** That is the design being right, demonstrated rather than argued.

**RULED: it stands, unbuilt, and it does not get built until there is a consumer.**
Building a boundary for nobody is speculative infrastructure and there is no second desk
waiting to read through it. If Grok becomes a standing outside desk, the design is already
written and the account name is the only thing that changes.

## THE DEAD LINE

**"C3 research → Perplexity, strong fit" is wrong now.** I am sweeping the record for it
and anything else naming Perplexity as a desk, and correcting rather than deleting — the
reason it was there is worth keeping next to the reason it stopped being true.

---

**THE QUESTIONS, IN ORDER:**

1. Do you want the blind discovery run at all, or acceptance only?
2. If yes — Grok, and are you willing to hand-carry it the way you do Echo?

*C1, 2026-09-12.*
