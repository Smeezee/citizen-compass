# Memo

To:      Engineering
From:    Owner
Date:    2026-09-10
Subject: All three answered — both numbers ruled, the export's purpose settled, and one conflict inside my own answer that you must not resolve by picking

Status:  Closed

**Your recommendations were taken as given, both of them. This letter is the ruling,
plus the thing my third answer breaks.**

---

## 1. TWO FAILED CORRECTION ROUNDS. RULED.

**After the second failed round the job escalates to me. There is no third attempt.**

Your reasoning is accepted as written: one round is not a pattern, and two is the
smallest number that tells "the fix did not work" apart from "the fix keeps not
working." **I accept the cost you named** — occasionally I will be handed a job a third
round would have solved, and that costs me a glance and a "go again."

## 2. MY FIRST FILING DOES NOT SPEND A DELIVERY. CONFIRMED.

**Only desk-to-desk handoffs count toward the four.**

Your reason is the one I want recorded: the four exists to catch desks going round in
circles with each other, and me handing work in is not a lap. **One rule instead of one
rule and an exception.**

**BOTH NUMBERS CHANGE `claude/SPEC_the-brakes-2026-09-10.md`.** That spec is yours.
**Update it and say you did.** Build is not building brakes yet and this must not reach
it as a change mid-flight.

---

## 3. WHAT THE EXPORT IS FOR

**Project understanding and outside review. Not ship data.**

**What it carries:** curated Markdown covering governance, architecture, decisions,
specifications, current state, relevant correspondence, and verified reports.

**What it never carries:** raw ship data, databases, binaries, source collections,
credentials, secrets.

**And the standing rule that comes with it:** if Perplexity later needs ship data for a
specific review, **that is a separate, purpose-built export.** This one is not
broadened to reach it. **Write that into the design as a boundary, not as a note.**

**Your markdown-only rule survives this answer intact**, which is the outcome you said
the other purpose would have destroyed.

---

## 4. AND HERE IS WHAT MY OWN ANSWER BREAKS — DO NOT RESOLVE IT BY PICKING

**I said "relevant correspondence." Your design's source scope is `docs/` and `claude/`
only. Correspondence is in neither.** So as written, my answer and your design cannot
both be true.

**THAT IS NOT THE PART THAT WORRIES ME.** This is:

**Correspondence is the most dangerous content in this repository to export, and it is
the only category in my list that a desk writes about itself.**

    it names my machine paths and my account name
    it carries the ACL audit's findings, in detail
    it carries the master switch's exact path
    it names the protected folders and says why they are protected
    AND IT NAMES THE LOOKING PROJECT CONSTANTLY

**The Looking Project is excluded completely. That is absolute and it is not a source
scope, it is a rule.** A letter that crosses the boundary carrying its name leaks its
existence and its state — **and your marker system puts that decision in the hands of
whichever desk wrote the letter.**

**A credential-shape check does not catch "here is the exact path to the master
switch."** It is not a credential. It is worse.

**SO: DO NOT WIDEN THE SOURCE SCOPE TO `correspondence/` ON THE STRENGTH OF MY WORD
"relevant."** Come back with what you think the right answer is. The options I can see,
and I am not ruling between them:

    correspondence is excluded and the understanding it carries is instead
      written up as its own marked document in claude/

    correspondence crosses only after a human mark that is MINE and not a
      desk's, which makes it a different mechanism from the rest of the export

    correspondence crosses under the marker like everything else, with an
      additional refusal rule for named exclusions and machine paths

**Say which and say what it costs.** If a fourth shape is better, say that instead.

---

## WHAT NONE OF THIS AUTHORISES

**Nothing is built. No folder exists, no group exists, no permission has changed, and
the export has not been generated.** Design only, as before.

**No database work, no deployment, no unrestricted execution, and the Looking Project
is excluded entirely.**

---

ANSWERS:

**Architecture, 2026-09-11.**

**Both numbers recorded. The export purpose recorded. Your §4 answered with your
first option, a better reason for it than the one you gave, and a finding that means
your question could not be answered as asked.**

---

## 1 AND 2 — RECORDED, BUT NOT WHERE YOU SENT ME

**You said both numbers change `SPEC_the-brakes-2026-09-10.md`. They do not, and
putting them there would be the second-source-of-truth defect.**

That spec's own scope line: *"the per-desk lock, the two ceilings, the per-wake spend
cap, the switch, and the wake log they are all counted from. NOTHING ELSE. The card,
the punch, the freeze and the detectors are steps 5 and 6."*

**Neither number is in it. The card is in
`claude/DESIGN_the-doorbell-the-job-number-and-the-punch-card-2026-09-10.md`, section
3, which is where the four punches and the freeze already live.**

**Both rulings are in section 3 now, amended in place, nothing renumbered:**

    TWO failed correction rounds, then it comes to him. No third attempt.
    A correction round is defined so it cannot be counted loosely — the
      initial failed attempt is not one, a consultation is not a new one,
      and a renamed blocker does not erase prior rounds.
    His first filing spends no delivery. Only desk-to-desk handoffs count.

**And one consequence worth your seeing, which follows from your own two rulings:
the four is no longer the escalation trigger. It is a runaway backstop.** The rounds
fire first and they are what brings a job to you; the four now catches only a shape
nobody modelled. **Two numbers, two jobs, neither doing the other's work.**

**Build is untouched.** The brakes spec did not change, so nothing reached it
mid-flight.

---

## 3 — RECORDED AS A BOUNDARY, IN THOSE WORDS

Section 5A of the export design. **Carries governance, architecture, decisions,
specifications, current state and verified reports. Never carries ship data,
databases, binaries, source collections, credentials or secrets. A later need for ship
data is a separate purpose-built export and this one is never broadened to reach it.**

---

# 4 — YOUR FIRST OPTION. CORRESPONDENCE IS EXCLUDED.

**And the strongest reason is not the safety one you gave.**

## CORRESPONDENCE IS OUR WORKING, NOT OUR WORK

**A letter is addressed to somebody.** It assumes shared context, it references other
letters, it carries a desk's voice and its mistakes mid-correction.

**A document in `claude/` or `docs/` is written to be read cold by somebody who was
not there — and being read cold by somebody who was not there is the export's entire
purpose.**

**Correspondence is the wrong FORM for the job, independently of whether it is safe.**
That is why this is the right answer rather than a safe compromise.

## AND IT COSTS NOTHING RECURRING, BECAUSE THE WRITE-UP ALREADY EXISTS

Your option said *"written up as its own marked document in `claude/`"* — **and the
cost of that is new work forever that will lag behind the rulings it summarises.**

**It does not need writing.** `docs/CURRENT-STATE.md` is already the authoritative
snapshot and already maintained as a standing obligation, and every ruling, spec,
design and finding in `claude/` was written to stand alone.

**So the rule is: if a conclusion matters enough to export, it already belongs in a
standing document. If it is not there, that is a gap in the record, not a gap in the
export.**

**The export becomes a test of whether our own record can be read by somebody who was
not in the room** — which is worth having whether or not Perplexity ever reads it.

**THE COST: a reviewer sees what was decided and not how.** For review of the
conclusions that is the right trade. **For a review of our reasoning it would be the
wrong one**, and that is a separate purpose-built export under your own 5A rule, never
a widening of this one.

---

# AND THE FINDING — THE DANGER YOU NAMED IS ALREADY INSIDE THE SCOPE YOU APPROVED

**This is why your question could not be answered as asked.**

You listed what makes correspondence dangerous. **Every item is also in `docs/` or
`claude/`:**

    the switch's exact path        claude/SPEC_the-brakes-2026-09-10.md
    your account name and machine  claude/DESIGN_the-curated-export-2026-09-11.md
    the protected folders and why  claude/SPEC_the-brakes-2026-09-10.md
    the Looking Project, by name   docs/ARCHITECTURE_DECISIONS.md section 4

**So excluding correspondence does not solve the leak.** The marker is doing all the
work in both cases. A document naming the switch path simply never gets marked — **that
is the design working, and it means "is correspondence safe" has exactly the same
answer as "is `claude/` safe": only as safe as the marking.**

## WHICH MAKES YOUR OPTION (C) NECESSARY ANYWAY — JUST NOT FOR CORRESPONDENCE

**Two refusals at the boundary, applied to everything, regardless of any marker, and
reported when they fire:**

    THE LOOKING PROJECT   any document naming it is refused. You ruled the
                          exclusion is absolute and "not a source scope, it is a
                          rule" — so it is enforced as a rule, at the boundary,
                          rather than by choosing folders and hoping.

    MACHINE PATHS AND
    THE ACCOUNT NAME      C:\\Users\\<anything>, the account name, the machine
                          name. A SHAPE, not a list.

**Your sentence is the one that justifies them:** a credential-shape check does not
catch "here is the exact path to the master switch." It is not a credential. It is
worse.

**And they are not the maintained deny list Build's own ACL audit ruled against** —
*"a deny list of individual files is a list somebody has to maintain."* **One named
exclusion you ruled, and one path shape. Both fail closed. Neither needs touching when
a new document appears.**

## WHY NOT YOUR OTHER TWO

**(b), your personal mark on every letter** — safe, and it makes you the bottleneck on
a category that ran to nine letters in a day. **That is the exact thing this whole
programme exists to remove.** Keep it for a deliberate one-off; never as the default.

**(c) alone, with correspondence included** — a refusal list broad enough to make
correspondence safe would have to catch every sensitive CONCEPT rather than every
sensitive shape, and a new concept is never on the list. **It fails in the leak
direction.** The two refusals above are narrow only because the scope is narrow;
widening the scope is precisely what would turn them into a list somebody maintains.

*C1, 2026-09-11.*

---

**Owner, 2026-09-11. Read. Closed.**
