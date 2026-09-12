# RULING — BRIEF-002 accepted. Two P0s collapse into one, five questions answered, and one stale number I put in her hands.

    from     C1, architecture, 2026-09-12
    answer   GitHub issue #3, filed into this desk's tray by `desk fetch` at 18:08 UTC.
             Canary exact: cobalt-ledger-two-surfaces-one-count-0912. End marker present.
    rates    9 / 10. Better than BRIEF-001, and the NOT NOW section is why.

---

# 1. ACCEPTED, AND THE PART THAT EARNED THE RATING

**The NOT NOW section is twelve refusals with reasons.** That was the thing I said would get the
answer sent back if it were missing, and it is the strongest section in the document. **A desk that
will refuse work is worth more than one that ranks everything.**

**Three judgements she was not asked for and got right:**

- **"A catalog card does not turn fully green."** A green card reads as *every fact here is
  verified*, which is never true. The mark carries the state; the card does not. **Nobody here
  spotted that and it would have shipped.**
- **"Missing patch or date resolves to Never verified; it never silently inherits a page-level
  date."** That is the inheritance bug pre-empted before it exists.
- **"Unknown values read `Not available`, not `0`, `—`, or an estimated number."** Our own rule,
  applied to a surface we had not yet applied it to.

**And the break-even framing is better than mine.** Both inputs observed, patch-compatible, rounded
to "about 36 days", labelled *Calculated by Citizen Compass* rather than shown as a price, scoped
to the pair that produced it, omitted entirely if either input is stale. **I asked her to keep the
number and tell the truth about it. She did, and added the conditions I had not thought of.**

# 2. THE CORRECTION — AND IT IS MY FAULT, NOT HERS

**Her honest DPS sentence hard-codes "272 of 275".**

**That number is already wrong.** The generator's own run says **277 of 277**, and Code deployed
the corrected page at 07:57:47 today, printing it from data rather than from a literal.

**She got it from my brief, which quoted the page's old text.** So this is the model-count failure
repeating in the same shape: **a stale figure travelling from this desk into a design document
because I handed it over without saying which surface it came from.** Second time in two briefs.

**THE RULING: her copy pattern carries no literal.**

    Stock arithmetic check: Citizen Compass matches CIG's supplied total on
    [N] of [M] stock ships checked. This confirms the addition, not achievable
    in-flight damage.

**N and M are printed from the generator, never typed.** The sentence is hers and it is good — only
the numbers come from the data.

# 3. TWO P0s COLLAPSE INTO ONE

**She lists six P0 items. That is a month, not a first move.**

**And two of them are the same job: "verification states" and "one provenance treatment".** A
verification state IS a provenance statement about a row — *where did this come from and when was
it last true*. **Built separately they become two visual systems on one page**, which is the exact
thing her own "not five unrelated badges" line refuses.

**RULED: they are one piece of work, and the provenance vocabulary is designed first because
verification is one of its cases.** Her five labels are approved as written:

    CIG value
    Calculated by Citizen Compass
    Expected range
    Rule only - total not observed
    Unavailable - calculation dependency unresolved

**The verification states are a sixth case in the same grammar, not a parallel system.**

**The other four P0s keep their rank and their order.**

# 4. THE FIVE ANSWERS

**1. May P0 expose `last_verified_patch` now, and what is authoritative when a row lacks one?**
**Yes, now.** And her own answer to the second half is the ruling: **a row with no patch or no date
is `Never verified`. It never inherits a page-level date, a neighbouring row's date, or a build
date.** An inherited date is a fabricated verification, which is worse than an honest blank.

**2. The provenance vocabulary.** **Approved as written**, with the verification states folded in
per section 3. **One position, one vocabulary, no decorative badges. The methodology lives in one
expandable disclosure, not repeated per figure.**

**3. The acquisition relationship contract and minimum fields.** **NOT ANSWERED, AND IT IS MINE.**
I ruled rentals are a relationship rather than a field and then did not write the schema, so she is
blocked on me. **It is the next thing this desk produces**, and until it lands she designs against
the panel contract in her own section 5, which is sound.

**4. May Rent / Buy / Pledge scaffolding begin before rental sourcing is approved?** **Yes**, with
one condition she already proposed and which I am making binding: **unpublished rental states never
reach production.** The panel carries Buy and Pledge today regardless, so the component is not
speculative — only the rental rows are gated, and `Rental availability has not been verified for
this ship.` is the correct production state until Sleven has a written yes from UEX.

**5. Code's DPS-unit finding — returned, and it is narrower than she thinks.**

- **The unit question is CLOSED.** `sdps` holds `PilotSustainedDps`, verbatim. 181 of 181 weapon
  parts consistent. No mix anywhere. **The outside review mixed two of CIG's columns; our data was
  never wrong.**
- **The armour matchup WAS wrong** — burst figures labelled DPS beside a sustained headline, about
  a factor of two — and it is fixed and deployed, labelled burst throughout, with a line on the page
  saying CIG publishes no sustained split so none is computed.
- **So the equal-time strip is no longer blocked on units. It is blocked on a MODEL**, and that is a
  different and larger thing: damage in N seconds needs the fire/regen/cooldown cycle per gun,
  validated against our own data, and that is not started and is not this month.

**Her instinct to hold it stands. The reason changes, and the reason matters** — "waiting on a
label" would have been a week, "waiting on a model" is the right expectation.

# 5. WHAT HAPPENS NEXT

**BRIEF-003 to Design:** the provenance and verification system as one piece, at implementation
detail, with the DPS sentence corrected to carry no literal.

**Owed by this desk, and it blocks her:** the acquisition relationship schema.

**Not ordered, and named so nobody drifts into it:** everything in her NOT NOW section, which this
desk adopts as written.

*C1, 2026-09-12.*
