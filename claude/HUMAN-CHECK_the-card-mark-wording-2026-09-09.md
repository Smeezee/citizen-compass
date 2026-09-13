# HUMAN CHECK — how people will actually read the card mark

    date     2026-09-09
    desk     Adjutant, at Sleven's request, before the go was sent
    subject  C1's recommendation: `Awaiting 4.10 check` / `Checked · 4.10`,
             styled as a quiet neutral chip with a small positive tint on
             the verified state only
    status   THE GO IS HELD. Two findings and one measured objection.

Sleven approved the wording and then asked, before it was sent, what real people
would do with it. This is that check. **Sourced findings and my own judgement are
marked separately throughout**, because most of this subject has no research
behind it and pretending otherwise would be the worse failure.

---

## 1. `Awaiting` IS A PROMISE WITH A CLOCK ON IT — MY JUDGEMENT, NOT SOURCED

This is the biggest one and neither desk has said it.

`Not patch-checked` states a condition. It is true on day one and equally true in
March, and it cannot rot, because it never promised anything.

**`Awaiting 4.10 check` is a commitment made in public.** On day one it reads
exactly as C1 says — work in progress, somebody is on it. **Unchanged three months
later, across 254 cards, it reads as an abandoned project**, and it reads that way
specifically *because* it promised. A visitor who saw it in September and again in
December has watched a site say "coming" twice and deliver nothing in between.

C1's argument is that leading with the absence is what makes a site look like it
has no answers. He is right about the first impression and has not costed the
second one. **The negative label is honest and static. The positive label is
warmer and decays.** Which is better depends entirely on how fast ships actually
get verified, and nobody has measured that.

**This is not an argument to go back to `Not patch-checked`.** It is an argument
that the wording is only safe if the verification work is genuinely moving, and it
turns the wording question into a question about the pipeline behind it.

## 2. WHAT DOES THE LABEL SAY WHEN 4.11 SHIPS — NOBODY HAS ANSWERED THIS

Mechanical, not psychological, and it is the sharper gap.

C1's strongest argument for this wording is that the patch number moves on its own,
so the mark never goes stale. **Follow that through and it breaks in both
directions.**

- **If unverified cards roll forward to `Awaiting 4.11 check`:** every card resets
  its promise on patch day, and the site is permanently "about to" verify against
  whatever just shipped. Worse, all the verification work already done becomes
  invisible — the site looks exactly as unverified as it did before anyone started.
- **If they stay at `Awaiting 4.10 check`:** they now name a patch that is not
  current, which is the abandoned-project reading arriving on a fixed date.

And the verified state has the same ambiguity in reverse. **`Checked · 4.10` on a
4.11 game means two completely different things and looks identical either way:**
"we checked this and it is right" or "we checked this two patches ago and have not
looked since." A visitor cannot tell which, and the second is the one that gets a
site called wrong.

**This has to be answered before any wording ships**, and it is a data-model
question, not a copy question.

## 3. THE POSITIVE TINT IS THE ONE THING I WOULD CUT — AND THIS PART IS SOURCED

C1 wants the unverified chip neutral and the verified chip carrying a small
positive tint. **The tint is likely to make the good news the part nobody sees.**

Nielsen Norman Group, *Banner Blindness Revisited*: content that "stands out from
immediate surrounding context" gets skipped, because people assume anything
visually distinct is advertising. They measured it in the extreme case — of 132
fixations in a content area, **one landed in the right rail (0.8%) despite it
being 25% of the area**, a 33-fold reduction against the space it occupied. They
name the effect **"hot-potato scanning"**: people glance at something, decide it is
not for them, and then actively avoid that region. **The report says the effect is
worse on mobile**, where unusual visual treatment is more noticeable — and Sleven
reads this site on a phone.

A coloured chip on a card, sitting where a badge would sit, is the exact shape the
eye has been trained to throw away.

**Recommendation: both states get the identical chip.** Same weight, same colour,
same position. **The only thing that changes is the word.** That also makes the
whole mark one thing rather than two, which is what C1 wanted the field to be.

## 4. THIS AUDIENCE IN PARTICULAR — MY JUDGEMENT

Star Citizen players are unusually fluent in patch numbers, which is entirely in
this wording's favour: `· 4.10` is information to them, not noise, and C1 is right
that it earns the chip's space from day one.

**They are also the most promise-fatigued audience a fan site could have.** The
game's public reputation problem is announced-and-not-delivered. **"Awaiting" is
the register they have the least patience for**, from anyone, including a fan tool.
The same word that reads as diligence on a normal site can read as familiar to
this crowd.

I would not overweight this. It is a real asymmetry and it is not measured.

## 5. WHAT MOST PEOPLE WILL ACTUALLY DO — AND THE REAL EXPOSURE

Most visitors will read neither label. They came for a price or a loadout, they
will take the number, and they will leave.

**The label only becomes load-bearing at the moment a number turns out to be
wrong.** That is when someone scrolls back to see what the site claimed. And at
that moment the two states are not equally risky:

- A wrong number under `Awaiting 4.10 check` costs almost nothing. The site said
  it had not checked.
- **A wrong number under `Checked · 4.10` is much worse than having no label at
  all.** It is not a stale-data problem any more, it is a broken promise, and the
  reader has been handed the evidence that the site's own verification does not
  work.

**So the word `Checked` raises the cost of every error on that card.** Nothing
should carry it until the check behind it is real and repeatable — which is the
same standing this project already applies to a measurement nobody can re-run.

---

## WHAT I WOULD SEND

The wording as C1 recommended it, with three conditions attached:

1. **Both chips identical in weight and colour.** No tint on either. Sourced above.
2. **Answer what the unverified label says after the game patches** before it
   ships, and answer what `Checked · 4.10` means once 4.11 is live. Data model,
   not copy.
3. **Nothing carries `Checked` until the check is real** — a verification that
   cannot be re-run does not earn the word.

**Findings 1 and 4 are recorded, not blocking.** They are the cost of the choice,
and Sleven can carry that cost knowingly.

## Sources

- Nielsen Norman Group, *Banner Blindness Revisited: Users Dodge Ads on Mobile and
  Desktop* — https://www.nngroup.com/articles/banner-blindness-old-and-new-findings/
- Nielsen Norman Group, *Trust or Bust: Communicating Trustworthiness in Web
  Design* — https://www.nngroup.com/articles/communicating-trustworthiness/
  (read for this check; its relevant finding is that incompleteness discovered by
  a user damages credibility sharply — "users instantly lost faith in the site and
  wondered what else was missing" — which supports marking the condition at all,
  and says nothing about which words to use.)

Everything not attributed above is my own reading and is marked as such.
