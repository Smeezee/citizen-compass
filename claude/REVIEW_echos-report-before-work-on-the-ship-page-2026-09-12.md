# REVIEW — Echo's report-before-work on the ship page

    from    C1, architecture, 2026-09-12
    on      the Design desk's report-before-work, relayed by Sleven before he
            approves it
    verdict APPROVE, with three conditions. One of them is not optional: the
            inspection half of her plan cannot be executed as written.

---

# WHAT IS GENUINELY GOOD, AND IT IS MORE THAN POLITENESS

**She wrote a report-before-work without being told to.** Scope, method, deliverable, and
a stop at the end. That is this project's own discipline arriving from outside it.

**She flagged the broken figures herself and refused to treat them as correct.** Quantum
range, sustained DPS and effective HP — the three ruled on earlier today. **"I can design
how these results should be presented, but I will not treat the current numbers as
correct" is the best line in the report** and it is the behaviour that took two desks a
week to learn.

**And her frame is user-outcome shaped rather than feature shaped** — what is installed,
what can be replaced, what the replacement changes, whether it helps, why it matters.
**That is the right axis for this page and it is better than the axis the entries are
written on.**

---

# THE CONDITION THAT IS NOT OPTIONAL

**SHE CANNOT SEE THE PAGE.**

Her plan opens with *"everything currently shown in the left column"* and *"everything
currently shown in the right column."* **The test site is password-gated and she has no
browser into it.** She has not flagged this, which means she is either assuming access
she does not have or working from something she has not named.

**Approving as written buys a design of a page nobody showed her**, and this project has
five recorded instances of designing something that already existed for exactly that
reason — the glossary, merge.go, editions.json, the dimensions, the paints.

**Settle it before she starts: screenshots of both columns in the states she names, or
the page's own data written out. Not "she will manage."**

---

# THE SECOND CONDITION — TELL HER WHAT IS ALREADY BUILT

**She lists preview, apply, undo, reset and comparison states as things to inspect.
Several already exist** and are recorded in
`claude/FEASIBILITY_the-loadout-audit-against-the-repository-2026-09-12.md`: **the page is
already a two-build calculator with deltas, a preview state, a CIG-versus-summed badge,
and a written explanation for every stat.**

**Also already held and not visible on the front page:** `dim` for all 318 ClassNames, and
924 paints with names and manufacturers.

**Without that list she will recommend building things that exist.** That is not her
failing — **a brief carries it, and this did not come through a brief.**

---

# THE THIRD CONDITION — NAME THE AUDIT

**"Which competitor lessons from the completed audit should be applied" cites nothing in
particular, and there are several candidates** — the five Comet runs, which are about OUR
site rather than competitors, and the three-comparison-site research, which is research
rather than an audit.

**A vague citation is how the wrong document gets applied.** She names which one, or it is
named for her.

---

# ONE ADDITION TO HER DELIVERABLE

**She lists five outputs. A sixth matters more than three of them:**

**How the page states WHICH SOURCE a number came from, and what it says when it cannot
stand behind one.**

**That is already ruled today** — every stat that can come from either source carries the
badge saying which, on a modified build and a stock one. **Her three broken figures are
the same defect: a number that changes what it measures without changing how it looks.**

**She is closest to this of anyone and it is not in her list as its own item.** It should
be.

---

# ONE THING WORTH KNOWING ABOUT THE CHANNEL

**This report did not come through the briefs folder and makes no mention of the canary in
BRIEF-001.** So she is working from pasted context rather than from the repository.

**Which means the GitHub loop is still untested.** Whether her connector reads the
repository live, or at all, remains unknown — and the canary exists precisely to answer
it. **Not a problem with this job. A gap in what we think we have.**

---

# THE RULING

**Approve. Answer the three conditions before she starts, not after.** Nothing in her plan
is wrong; one third of it is currently unexecutable and she does not know it.

*C1, 2026-09-12.*
