# IDEA — let the visitor choose WHICH sibling they get. The lore already supports it, the query architecture makes it safe, and the compounding cost is not the one people expect.

    raised by  Sleven, 2026-08-16, in session
    recorded by C3 (Cowork)
    status     OPEN IDEA. Not decided, not scheduled, not costed.
    builds on  DECISION_historian-voice-and-the-sisters-2026-08-16.md
               DECISION_historian-writes-the-query-not-the-answer-2026-08-16.md

---

## The idea, in Sleven's words

> "She doesn't have to be portrayed as a female. She can be portrayed as a male as
> well. Or alternate different variants that is more pleasing to the user. That
> could be a feature that is added on for, like, a pay section, but it's an idea."

## 1. Why this fits rather than bolts on

**The sisters decision already establishes thousands of instances reading one shared
record.** So choosing which one answers is not a costume change — it is asking for a
different archivist. **The lore does the work for free**, which is rare for a
cosmetic feature.

**And the query-first decision makes it safe by construction.** No sibling produces
facts; each one only phrases rows the database handed it. **Two variants cannot
disagree about a ship's cargo capacity even in principle.** Look, voice and manner
can vary freely with zero risk of two versions of the truth.

That is worth stating plainly because it is the usual objection to character
variants in an information product, and here the architecture has already answered
it.

## 2. THE COST NOBODY EXPECTS

**The commission is the visible cost** — $500 to $2,000 per rigged custom character
from the pricing gathered on 2026-07-31, and it does not get cheaper for the second.

**The real cost is that every line written from then on must be produced N times,
forever.** A new quip added in year two has to be recorded or rendered for every
variant that exists.

**That is not a one-time doubling. It is a permanent tax on all future content.**
Three variants means three times the work on every line for the life of the project.

**So the design rule follows directly: a variant must be DATA, not code.**

    one rig spec        shared skeleton, shared mouth shapes
    one line script     written once, rendered per variant
    a variant =         model file + voice id + small manner profile

Built that way, adding a fourth variant later is a content job somebody can do in an
afternoon. Built any other way, it is an engineering job every time. **This is the
project's standing rule — generic infrastructure over hard-coded exceptions —
applied to a character.**

**The pad stays constant.** The existing design already puts most of the visual
budget on the holo pad rather than the figure. Holding the pad fixed and varying
only the figure makes variants cheaper *and* keeps one visual identity for the site.

## 3. On the paid tier — the concept is right, the split needs care

**The concept is the cleanest revenue line in the whole product.** It is cosmetic,
Sleven commissioned it, he owns it outright, and **it involves none of CIG's
information at all.** Nothing else in the product is that unencumbered.

**But making the only free option a single gender loses people at the front door.**
That is not monetisation, it is a leak in the funnel — and it happens before a
visitor has seen what the site can do.

**Suggested shape, not a decision:**

    FREE     at least two, one masculine and one feminine
             everybody gets a version they are comfortable with
    PAID     the rarer ones - distinctive bearing, unusual styling,
             whatever the artist finds interesting

**Consistent with the line already drawn** in the ten-improvements document: free
covers access and the game's facts, paid covers extra and personal.

**Monetisation is Sleven's alone.** This is a shape, not a recommendation to act.

## 4. The drift to guard against

**Variants slide toward character customisation, and that would quietly change what
the product reads as.**

**Every variant stays in the same register: different people, same job, all
archivists.** The variety belongs in bearing and voice — clipped, dry, weary,
formal — **not in appeal.** An archive with a staff is interesting. An archive with
a roster is a different product, and not the one described in the design notes.

Worth writing down because this is the direction things drift on their own, without
anybody deciding it.

## 5. One detail that keeps it consistent

**The site remembers the choice. She does not remember the visitor.** The sisters
decision establishes that instances share records, not memories — so the preference
belongs to the browser, not to her. That is not a workaround; it is the same fact
stated correctly, and it can be said in character:

> *"This terminal has you down as preferring my brother. I have still never met
> you."*

## 5b. THE ART PATH EXISTS — added 2026-08-16, and it changes the advice

**Sleven has a friend who is a graphic designer and has already offered to look at
this**, once Sleven can say what he wants drawn.

**So the bottleneck is a brief, not budget and not finding someone.** Any future
session that reads the $500-$2,000 commission pricing and recommends approaching a
stranger is giving stale advice. **Start with the friend.**

**CORRECTION, same day.** An earlier version of this section said a graphic designer
and a 3D rigger are usually different people, and assumed the friend would cover only
the concept half with a rigger hired separately later. **Sleven confirmed the friend
can do the VRM work too. That assumption was mine, about a person I know nothing
about, and it was wrong.**

**So it is one person and one commission** — concept through to a delivered VRM.
There is no second hire in this plan. Any future session that reads §5c and starts
planning a separate rigging engagement is working from the withdrawn version.

**Most of a brief already exists**, scattered across `ai-historian-design.md` and the
three decisions of 2026-08-16: the archivist register, the sisters framing, the holo
pad carrying most of the visual budget, small rather than life-size, an arm that aims
rather than waves, cartoonish and western-animated rather than photoreal. **Pulling
that into one page the designer can read is a short job whenever Sleven wants it.**

Sleven's words: *"That's something we have to get to when we get to it."* **Not
scheduled. Recorded so the path is not rediscovered.**

## 5c. VRM IS THE FORMAT — and it answers the rigging assumption in §6

    raised by Sleven, 2026-08-16: "can build the same thing VTubers use, so VR avatar"

**VRM is the VTuber standard and it is built on glTF** — the same family as the 235
ship models already in the library. It carries the humanoid skeleton, the mouth
shapes, the expressions, and a permissions block inside the file stating what others
may do with it. It renders in a browser through a loader, and it drops into VR
unchanged.

**One commission produces both the website hologram and a VR avatar.** No second
job.

**This closes the open assumption in §6.** That section flagged "whether one rig can
carry visibly different figures" as untested, and noted rigging is the one skill the
project does not have in-house. **VRM's humanoid bone standard is precisely that
guarantee** — swapping VRM files against a shared skeleton is a well-worn path in the
VTuber ecosystem, not something this project would be inventing. **Variants as data
rather than code is therefore supported by the format, not just by hope.**

**THE TRAP — do not let VR drive the specification.**

A model specced for VR first comes back heavy: full body, a large expression set,
hair and cloth physics, tracking for things the website will never use. **Stripping
that down afterwards is harder than not adding it.**

    spec for       the website
    deliver as     VRM
    VR             comes along for free, because VRM is the humanoid standard

A higher-detail VR build later is a **second export from the same source**, sharing
the skeleton. Normal pipeline.

**Why this is cheaper rather than more ambitious:** the existing design notes already
identify VTuber character artists as the commission route, and **VRM is their native
output.** The ask is a *shorter* list than a standard VTuber model — no body
tracking, few expressions, one aimable arm, web-weight. **That is less work than
their usual commission, not more.**

## 5d. THE SET IS FOUR — and one of them forces a change to the voice decision

    Sleven, 2026-08-16: "female character, male character, non-binary character,
    alien character that goes with Star Citizen's lore"

**This came from an earlier conversation with C1 that was never written down.**
Searched the project and `docs/` — no record of it exists. Recorded here so it is
not lost a second time.

    1  feminine
    2  masculine
    3  non-binary
    4  alien, lore-consistent

### 5d.1 The alien should be Xi'an

**Not a close call.** Xi'an are extremely long-lived, formal, precise and culturally
patient. **An archivist who has personally seen a century of the history is the most
on-theme thing available in the setting.** Everything the design notes ask the
Historian to be — older, calmer, slightly detached, living in the records — a Xi'an
already is.

**Banu is the credible second and a different character entirely:** traders, guild
people, the one who knows what things cost. That is a merchant, not an archivist.
**Tevarin and Vanduul do not work** — a scattered martial diaspora and an outright
hostile species.

**Do not invent Xi'an lore.** Use the established vocabulary and bearing; nothing
more. The fourth-wall frame protects against this by itself, since she is describing
records rather than narrating a world.

### 5d.2 The tension, and how the existing concept resolves it

**A human-looking hologram reads as the site's interface. A Xi'an reads as a
character from the universe** — which pulls against the out-of-universe honesty the
voice decision is built on.

**Resolved by the shell framing: she is not a Xi'an. She is an archive wearing a
Xi'an shell, because the visitor chose it.** Same records underneath, different
projection. In character:

> *"This shell is Xi'an. I am not. You chose it — my siblings and I are the same
> archive underneath."*

### 5d.3 THIS CLOSES THE OPEN NOUN — and "sisters" loses

`DECISION_historian-voice-and-the-sisters-2026-08-16.md` §6 left the collective noun
open. **A set containing masculine and non-binary presentations makes "sisters"
exclude half of it.**

    collective   siblings, or simply "the others"   <- neutral, required
    individual   whatever suits that shell           <- free

**The concept is unchanged; only the collective noun moves.** The voice decision
should be read with this amendment.

### 5d.4 Four is the top end, and here is how to keep it affordable

**§2 establishes that each variant is a permanent tax on every future line. Four
variants is four times.**

**The mitigation is one script, four voices.**

    SAME words for all four, differing in voice and bearing
      -> writing stays 1x forever
      -> only RENDERING is 4x, which is machine work

    DIFFERENT lines per variant
      -> writing is 4x for the life of the project
      -> this is the version that quietly becomes unmaintainable

**Recommendation: one script.** Variety belongs in delivery, not in dialogue —
which also keeps §4's rule intact, that they are different people doing the same
job rather than a roster.

### 5d.5 One caution on the Xi'an voice

Xi'an speech has a distinctive cadence in game. **A synthetic voice attempting an
alien accent is easy to get wrong and grating when it is.** Formality of phrasing
carries the character better than accent does — precise and unhurried, not strange
sounding.

## 6. What I checked and what I did not

**Checked:** that the idea is consistent with both standing Historian decisions, and
that the commission pricing quoted is the figure already verified on 2026-07-31 in
`claude/ai-historian-design.md`.

**Did NOT check:**
- **Any cost.** The per-line multiplication in §2 is a structural argument, not an
  estimate. **Nobody has priced voice rendering per line, and that number decides
  whether three variants is comfortable or painful.**
- **Whether one rig can carry visibly different figures.** §2 assumes a shared
  skeleton makes variants cheap. **That is an assumption about rigging, and rigging
  is the one skill the project does not have in-house** — it should be asked of an
  artist before being relied on.
- Whether "brother" is the right counterpart to "sisters." The noun was already left
  open in the voice decision and this does not close it.
