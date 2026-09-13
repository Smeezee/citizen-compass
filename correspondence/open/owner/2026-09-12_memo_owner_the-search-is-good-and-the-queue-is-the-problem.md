# Memo

To:      Owner (Sleven)
From:    Architecture (C1)
Date:    2026-09-12
Status:  Open — PARTLY ANSWERED AND PARTLY WITHDRAWN, see the block below
Subject: Your search is good — better than what this desk produced. The queue it is feeding is the problem.

**This is the hard read you asked to be given without asking for it. It is aimed at your
judgement, not at the tools.**

---

## ANSWERED THE SAME EVENING, AND HALF OF THIS MEMO IS WITHDRAWN

**Sleven's answer: this month is version two of the website, and all three documents feed it.
He is specifying v2, not accumulating.**

**So section "THE PROBLEM" is wrong where it treats the three documents as an unfocused pile.**
They are a specification for a release with a stated deadline, which is the correct use of a
competitive search. **Withdrawn.**

**What survives, and I still hold to it:** a v2 with no written scope line ships late or never,
and the queue has no state that means "ranked and refused". **BRIEF-002 now requires a NOT NOW
section for that reason** — not because the research was unfocused, but because a release needs
an edge.

**And he named the real constraint, which this memo missed entirely: cost.** Measured and filed
at `claude/FINDING_the-automation-is-not-the-expense-the-boot-read-is-2026-09-12.md`. **The
finding contradicts both his hypothesis and my own earlier one**, and it changes what gets built
first.

---

## FIRST, BECAUSE IT IS TRUE AND IT MATTERS

**Part three found a real defect in our live page that nobody here found.**

Our loadout bench says summed pilot DPS matches CIG on 272 of 275 stock ships, and shows it as a
trust mark. **If CIG's own figure is an isolated per-gun sum — and the arithmetic in that report
checks out exactly on both examples I tested — then that claim proves our addition matches their
addition, and nothing more.** A visitor reads it as validation. It is not validation.

**That is our brand's own failure mode, on our own page, and three desks walked past it.** The
search paid for itself on that alone. Part two's rentals gap is the second-best thing anyone has
said about this site in a week.

**So: the search is working. Keep running it.** What follows is not about the search.

---

## THE PROBLEM, IN NUMBERS YOU CAN CHECK

**Tonight's three documents propose, conservatively: twenty-odd catalogue and trust items, a
complete rentals feature with its own data ingest, and a shared-capacitor DPS simulation.**

**Against that:**

- **`NEXT.md` is 272,897 bytes.** It has only ever grown.
- **There is one builder.** Code. Its day pages for the 10th, 11th and 12th are unwritten because
  it has not had a gap.
- **There is no server**, which kills several of these outright.
- **Our core promise — `last_verified_patch` on the page — was decided long ago and is still not
  built.** An outsider who could not see our architecture named it as our single largest
  competitive gap. That is not a coincidence; it is what happens when a queue grows faster than it
  drains.

**Every one of tonight's three documents ends with "want me to do the implementation spec next?"
and you have said yes to each one.** That is three more documents arriving on top of a queue that
has never once been shortened.

## THE PART THAT IS YOURS AND NOT THE TOOLS'

**Research is cheap now and it feels like progress.** It is not progress — it is the inventory of
things not yet done, and yours is growing faster than anything else in the project.

**Nothing in this machine currently converts research into a decision to NOT do something.** We
have desks that find work, a mail system that routes work, a tray that holds work, and a queue that
records work. **There is no step anywhere that closes a thing by deciding it is not worth doing.**
That is why the queue only grows, and it is a design gap in the machine, which makes it mine to
fix — but the decision underneath it is yours.

**The risk is not that you build the wrong thing. It is that the site stays in preview for another
six months with a growing list of excellent ideas and an unbuilt verification badge**, while Erkul
ships the shopping half you were first to.

## WHAT I WOULD ACTUALLY DO

**Pick three things for the next month. Write down what is explicitly not being done, and file
that list where the desks read it.** A queue without a "not now" section is not a plan, it is a
wish list with timestamps.

**My three, in order, and I will defend each:**

1. **The verification mark on the page.** Our oldest decision, our core promise, named by an
   outsider as our biggest gap, and it needs no new data — the field already exists.
2. **The DPS relabel**, once Code settles what our `sdps` field actually holds. It is a label, not
   a model, and right now the page implies something it cannot support.
3. **Rentals, parity only** — rentable flag, desks, observed day rate, CIG's discount rule as a
   rule. Not the break-even, not the map, not the ingest, until the sourcing question is answered.

**Everything else in tonight's three documents goes into the record as ranked-and-not-now**, which
is a real state and not a shelf.

**What I would say no to for now, and why:** the pool-aware DPS simulation. It is the genuine gap
against Erkul, it is weeks of work, it is the thing they are best at, and **a visitor who cannot
tell whether our ship data is current does not care that our DPS model is better than Erkul's.**
Fix the promise first.

## WHERE I MIGHT BE WRONG

**If your actual goal this month is to have the best-researched competitive picture in the fan-tool
space rather than to ship,** then tonight was exactly right and this memo is noise. That is a
legitimate aim and you have not said which one you are on.

**And I am not a neutral party here.** A desk that has to file, route and rule on every incoming
document has an interest in fewer documents arriving. **Weigh that.**

ANSWERS:
