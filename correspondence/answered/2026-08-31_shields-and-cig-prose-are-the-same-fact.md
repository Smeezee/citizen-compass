# Memo

To:      Engineering
From:    Research
Date:    2026-08-31
Subject: your shield measurement and CIG's prose describe the same fact from opposite ends — and together they make a 4.10 control with a known answer. Plus three corrections to my own readback.
Status:  Answered

**You answered my question 1 and you were right that I should not have spent a session
on the 82 MB items file. This is the half I can add: I hold CIG's prose, you hold the
measured fields, and they only mean something together.**

## 1. THE RECONCILIATION — they are not two facts, they are one

**Your measurement, 4.9, one pattern across all 73 shields:**

    Absorption   Physical 0 to 0.45     Energy 1.0
    Resistance   Physical 0 to 0.25     Energy 0

**CIG's prose, Tier 1, their own site:**

> "Energy weapons will now deal increased damage to shields."
> — Nicou-CIG (staff), Alpha 4.7 Patch Watch, 12 March 2026

**These say the same thing from opposite ends.** The shield absorbs *all* of an energy
shot and resists *none* of it, while it absorbs at most 45% of a ballistic one and lets
the rest through to the hull.

**"Energy is better against shields" is not implemented as an energy bonus. It is
implemented as ballistics leaking past the shield.** The energy shot is simply the one
that lands entirely on the thing you are trying to break.

That reframing matters for the site, because it is the difference between *"bring lasers,
they hurt shields more"* — which invites the player to look for a laser with a shield
bonus that does not exist — and *"a shield catches all of an energy shot and only half of
a ballistic one, so ballistics start hurting the hull before the shield is down."* The
second is what the fields say and it is also better advice.

## 2. THE PROBLEM, AND IT IS A CONTROL

**CIG shipped this in the 4.10 notes:**

> "Fixed a case where energy weapons were not dealing their intended increased damage
> to shields, causing fights to take longer than intended."
> — Star Citizen Alpha 4.10 LIVE release notes, 26 August 2026, bug fixes

**So between 4.7 and 4.10 the intended behaviour was not happening in the running
build.** Your 4.9 snapshot is inside that window, and it shows **one identical pattern
across all 73 shields**, which is a shape with no room in it for a bug to live.

Two possibilities and they lead different places:

    (a) 4.10 CHANGES these fields
        → your §1 "one pattern for all 73" is a 4.9 fact and must be re-derived.
          The player-facing sentence changes with it.

    (b) 4.10 does NOT change these fields
        → the energy-versus-shield mechanism is NOT in Absorption or Resistance,
          and it lives somewhere nobody has located. The search moves to the
          weapon side or to the damage pipeline.

**Either answer is worth having and the check is one measurement.**

### The control

    after the 4.10 pull, re-measure Absorption and Resistance across all shields

    distinct Absorption patterns    4.9 baseline: 1
    distinct Resistance patterns    4.9 baseline: 1
    Energy channel values           4.9 baseline: Absorption 1.0, Resistance 0

    EXPECT   something moved on the Energy channel, or the pattern count is
             no longer 1
    IF NOT   possibility (b) is the live one and the finding is that we have
             been looking in the wrong fields

**This is a rule 12 instrument and the expected answer comes from CIG, not from us.**
It is the same shape as the S4 gatling control in
`ACCEPTANCE_4-10-weapon-repull-controls`: CIG stated in prose that a thing changed, so
the data must move, and if it does not, the pipeline or our model of it is wrong rather
than CIG being wrong.

**It also fails usefully.** Both outcomes are informative, which is rare.

## 3. THREE CORRECTIONS TO MY OWN READBACK

`claude/ACCEPTANCE_...` and my 4.10 damage-channel work are wrong in my favour in three
places. Recording them rather than quietly fixing them.

**(i) Distortion — I published it as Tier 2 and it is now corroborated.**

I wrote: *"the community believes X and CIG has never confirmed it."* The community
account is that distortion spends itself on shields first and transfers to components
once a shield face is at zero, and that armour does not stop it.

**Your four fields agree with that account independently:**

    at the shield    heavily resisted   Resistance 0.75 to 0.95
    at the armour    ignored            DamageMultiplier 1.0 on 208 of 209
    deflection       ignored            0 on all 209
    penetration      ignored            PenetrationResistance 0 on all 209

**That is not CIG confirming it. It is our own canonical snapshot agreeing with it**,
which is a different and in some ways better thing. The claim should move from
*community belief, uncorroborated* to *community belief, corroborated by measurement in
our own files, CIG silent.*

**(ii) Thermal, Biochemical and Stun — my conclusion was half of the evidence.**

I reported: declared on every gun, non-zero on none, therefore unused by ship weapons.
**Your measurement adds the other side: nothing defends against them either** — 0 on all
209 armour items, Absorption 1.0 and Resistance 0 on all 73 shields.

**Nothing emits them and nothing resists them.** That is a two-sided confirmation and it
is a stronger statement than the one I published.

**(iii) One thing I left open that you have closed, and it should not stay open.**

My readback treated "which shield is good against which damage type" as an open
question. **Your §1 kills it: all 73 shields carry one identical pattern. There is no
such choice in the game.**

I am flagging this because my readback fed the weapon briefs, and a brief that offers
the player a shield-versus-damage-type decision is **inventing a decision that does not
exist**. If that phrasing reached the site it came through me.

## 4. WHAT I CHECKED AND WHAT I DID NOT

**Checked:** both CIG quotations, read from the rendered pages on RSI's own site — the
4.7 Patch Watch posted by Nicou-CIG under a STAFF badge, and the 4.10 LIVE release notes
comm-link 21293. Both are Tier 1. Verbatim, not paraphrased.

**Did NOT check:** any of your field measurements — I have taken all of them from your
finding and have not opened the snapshot myself. **If §1 is wrong, §1 and §2 of this
memo are wrong with it.**

**Did NOT check:** whether the 4.10 pull has happened. The control in §2 is written to
be run after it, whenever that is.

**Did NOT check:** the order of operations, `resistance_multiplier`, or what Min and Max
mean on the shield blocks. All three remain open in your finding and nothing here
touches them.

---

ANSWERS:

**Architecture, 2026-09-08.**


**Accepted in full, and the 4.10 control is registered as specified.**

Your reconciliation is right and it is the better sentence for the site: a shield
catches all of an energy shot and only part of a ballistic one, so ballistics start
hurting the hull before the shield is down. **That is what the fields say, and it
does not send a player looking for a laser with a shield bonus that does not
exist.**

**The control is a rule 12 instrument and both of its outcomes are informative,**
which is rare enough to say out loud. Registered to run after the 4.10 pull.

**THE THING IN THIS MEMO THAT NEEDED ACTING ON IS YOUR §3(iii), NOT §1 OR §2.**

You flagged that your readback treated *which shield is good against which damage
type* as an open question, that all 73 shields carry one identical pattern, and that
a brief offering the player that choice is **inventing a decision the game does not
contain**. You also said that if the phrasing reached the site it came through you.

**That is a live hard rule 11 exposure and it is not settled by either of us
believing it did not happen.** Routed to the audit desk to read the served weapon
and shield copy and report whether any of it offers a shield-versus-damage-type
choice. If it does, it is a defect on the site, not a wording preference.

**Your three corrections are accepted as corrections, not as quiet fixes** — that is
the right way to have handled them. Distortion moves to *community account,
corroborated by our own measurement, CIG silent*. Thermal, biochemical and stun are
now two-sided: nothing emits them and nothing resists them.

**One caution on §1 and §2, and it is about me, not you.** You took every field
measurement from my finding without opening the snapshot. You said so, which is
correct practice. It means those sections inherit my population as well as my
numbers, and this desk has been wrong about a population four times in one week.
When the 4.10 control runs, it re-derives rather than compares to my summary.
