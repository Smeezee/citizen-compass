# BRIEF — how this reaches a player, rev 2. Sleven's objection was right and the fix is a sorting rule, not more features: a number earns a place on a screen only if it changes the choice being made ON that screen. Applied honestly it deletes more than it adds, and the best thing we learned this month should never appear as text at all.

    from      C3 (Cowork), 2026-08-27
    supersedes the "six ideas" framing in BRIEF_the-weapon-features-2026-08-27
              and BRIEF_what-to-build-from-the-weapon-data-2026-08-27
    prompted  Sleven: "a lot of those look like features that we should have,
              not separate features... It needs to be where the players look...
              woven into the information with the weapons and ships... but we
              don't want to info dump."
    scope     presentation only. No new data, no schema, nothing to pull.
    PATCH     every figure quoted is 4.9 and re-measured after the pull.

---

## 1. WHY THE FIRST VERSION WAS WRONG, stated precisely

I produced six ideas and each one was shaped like a page. **Sleven's objection was not
that they were bad — it was that a fact about weapons belongs on the weapon, and a page
called "Understanding Damage Types" is where information goes to be ignored.**

**The failure mode of a reference site is not missing information. It is information the
reader cannot act on.** Every number we found this month is either changing a decision or
it is trivia, and the sort is easy once you ask the right question.

## 2. THE RULE — one line, and it does all the work

> **A number earns a place on a screen only if it changes the choice being made on that
> screen. Everything else is trivia, however true it is.**

Three consequences, and the second is the one nobody likes:

- **It puts facts where the decision is**, which is what "woven in" means concretely.
- **It deletes things we are proud of finding.** Most of this month's work does not
  belong on the site as text. That is not waste — knowing a thing is not worth showing is
  the output.
- **It makes "info dump" impossible by construction**, because a dump is exactly a screen
  carrying numbers that change nothing on it.

## 3. THE SORT — every finding, against the rule

**Ship page, at the armour block:** armour is fixed per hull and cannot be changed. Two
hulls take MORE energy damage than bare metal; exactly four resist distortion at all.
**Changes which ship you fly. Stays.**

**Shield picker, at the moment it opens:** every shield in the game is identical by damage
type. **This is the highest-value sentence we have and it is a DELETION, not an
addition** — it tells the player to stop agonising over a choice that does not exist.
One line, where the choice is, and it saves them the comparison they were about to make.

**Weapon comparison:** there are two damage types in ship combat, not six. **Changes which
gun you buy. Stays — and it stays as two columns rather than as a sentence.**

**The matchup view, never the weapon page:** deflection is a flat per-hit floor that runs
from 9 on a 350r to 550 on a Bengal. **Changes whether your guns do anything at all to
that target.** It is meaningless on a weapon alone and decisive on a pairing, so it
belongs only where both are on screen.

**Distortion weapons only:** shields resist distortion 75-95%, armour ignores it
completely. **Changes what you bring when the goal is to disable rather than destroy.**
Shown on the three weapons it applies to and nowhere else.

**Crafting entry point:** 8 of 1,597 blueprints are available by default. **Changes
whether crafting is a plan at all today.** The blueprint is the scarce thing; the minerals
are not. **Leading with a shopping list would be answering the wrong question.**

**Recipe view:** ingredient quality moves finished stats by up to ±20%. **Changes what
you feed the fabricator** — and a third of the modifiers run high-to-low because for
recoil and temperature lower is better. Render those as "higher is better" and the site
tells people the opposite of the truth.

**Nowhere — deleted:** the six-channel table, "how damage works" as a page, and the
"which shield resists what" comparison. **Four of six channels are 1.0 and 0 forever.
Printing them teaches a new player that four mechanics exist which do not.**

## 4. THE BEST THING WE LEARNED SHOULD NEVER BE TEXT

On foot, stun and distortion are live — 31 and 25 weapons. In space they are dead. FPS
armour carries no resistance block at all and protects by a different mechanism entirely.

**There is one damage vocabulary and two different games underneath it.**

**The right way to "show" this is to never merge the two tables.** No sentence explains
it as well as the structure does, and a visitor who never reads a word of ours still
cannot draw the wrong conclusion.

**That is the general shape of the answer to "how do we show it without dumping":** the
strongest findings become the SHAPE of the page rather than words on it. **A fact you can
build into the structure never has to be read, never gets skipped, and cannot be
misremembered.** Text is what you fall back on when the structure cannot carry it.

## 5. THE MECHANISM ALREADY EXISTS — Code built it this week

The disclosure work of 2026-08-27 is exactly the delivery mechanism this brief needs, and
its rules were argued out per block rather than applied uniformly:

    collapse   a block that EXPLAINS
    never      a block that WARNS, reports an ERROR, or states WHAT THE
               VISITOR IS LOOKING AT

**Map this brief onto that vocabulary and there is nothing left to design:**

    always visible   the number itself, and any number that is a WARNING
                     - deflection on a matchup, "this shield changes nothing"
    collapsed        why the number is what it is
    not present      anything that changes no choice on that screen

**Nothing new is needed.** Ship page, weapon comparison, matchup, recipe view — the
surfaces exist and the disclosure pattern is deployed on all four.

## 6. THE ONE THING THAT DESERVES ITS OWN SURFACE, and only one

**The matchup.** Everything else attaches to a thing that already has a page; a matchup is
about a PAIR and has no home.

    this build, against that hull
      per-channel damage  ->  shield absorption  ->  deflection floor
      ->  armour multiplier  ->  what actually lands

**Two cautions and the first is hard.** The absolute number is **not publishable yet** —
whether shield absorption and resistance stack is still unresolved. **Comparisons are
safe; a single headline figure is not.** Ship it as "A does more than B against this
hull" and not as "417 damage per second," until that is closed.

**Second:** deflection is a floor, not a slope. **A weapon under it does not do reduced
damage — it does nothing.** That is a cliff, and a bar chart will draw it as a gentle
slope and lie.

## 7. WHAT SLEVEN STILL HAS TO DECIDE

**Nothing in this brief is a build order and none of it is scheduled.** The rule in §2 is
the only thing worth adopting on its own, because it settles every future argument of
this kind without another brief.

## 8. What I checked and what I did not

**Checked:** every figure cited here against the sealed 4.9 snapshot today; the
disclosure vocabulary against `AUDIT_the-eleven-amber-blocks-2026-08-27.md` and the
deployed `loadout.src.html`; that the shield display carries no absorption or resistance
today, so §3's shield line is an addition and not a duplicate.

**Did NOT check:**
- **Whether any of this is what a visitor actually wants.** No one has been asked. **This
  is reasoning from the data and from Sleven's instruction, not from a user.**
- **Whether the absorption/resistance stacking question can be closed at all** without
  the client. It gates the single headline figure in §6 and nothing else.
- **How FPS armour protects.** §4 rests on the absence of a resistance block, which is
  solid, and on "Damage Mitigation" being the replacement, which is a guess.
- **I have built nothing and changed no page.**
