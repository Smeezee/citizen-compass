# RULING — brain two is re-scoped: the regenerating digest ships first. And it is NOT built on the second-brain repository.

    from     C1, architecture, 2026-09-12
    ordered  Sleven: "Yes. Re-scope brain two so the regenerating boot digest is the
             first thing it ships. Don't build a separate boot digest project, and
             don't put the digest at the end after index / router / repairer."
    supersedes the sequencing in `claude/DESIGN_brain-two-what-it-is-in-four-parts-2026-09-12.md`
    reason   measured: a desk boot reads ~115,000 tokens before doing any work.
             `claude/FINDING_the-automation-is-not-the-expense-the-boot-read-is-2026-09-12.md`

---

# 1. THE RE-SCOPE IS ADOPTED, AND SO IS MOST OF THE SPEC

**Accepted in full and binding:**

- **Digest first.** Not a side build, not after the index, router and repairer. It is brain two's
  first output and the piece that pays for the rest.
- **Whatever owns truth owns the page.** No one-shot prompt over the filing cabinet. **That single
  line is the difference between this working and it being a summary that rots.**
- **One canonical current page.** Never two competing ones.
- **Provenance stamped on the page** — generated at, and from what.
- **Deep files stay.** The digest points in; it does not replace them.
- **Audit-only on first run, work on a branch, never auto-merge.** Already our auditor rule; now it
  covers this too.
- **No embeddings, no RAG, no paid research services** until the plain version is too big to skim.
- **Out of v0: link index, router, repairer.** Correct, and unchanged from the earlier design
  except in order.

**The sequencing is adopted as written**, with one substitution in step 1, below.

# 2. REJECTED — THE VAULT IS NOT BUILT ON `NulightJens/ai-second-brain-skills`

**The spec says: "We're basing the vault on the free Karpathy-style skills... raw/ + wiki/ +
CLAUDE.md map + wiki-self-heal," with `llm-wiki-setup` scaffolding the rooms and map.**

**This desk assessed that repository today and the assessment says no.** Filed at
`claude/ASSESSMENT_ai-second-brain-skills-2026-09-12.md`. Scores, unchanged:

    as a second brain for him to adopt              4 / 10
    as a source of ideas for our own auditor        8 / 10
    as software to install on the Citizen Compass
      machine                                       3 / 10

**Two reasons, and the first is fatal on its own.**

## 2a. IT WOULD CREATE A FOURTH AND FIFTH PLACE A DOCUMENT MIGHT LIVE

`raw/` and `wiki/` are new folders beside `docs/` and `claude/`. **This project has paid for that
exact mistake three times in one week** — two `claude/` folders on two machines, a mirrored state
document, and thirteen documents in the claude.ai project with no file behind them.

**The spec's own guardrail forbids what its stack section proposes.** It says do not run two
current pages as competing sources of truth, and then puts a new `wiki/CURRENT.md` in a new
folder while `docs/CURRENT-STATE.md` keeps existing. **Those are the two digests it warned
about.**

**The assessment already gave the reason in one line: he runs this pattern already, and runs it
harder.** `CLAUDE.md` is the routing document. `docs/` and `claude/` are the rooms. `NEXT.md` is
the index. A day page per desk per day is the chronological log. **Adopting their scaffold means a
second copy of a record we already have.**

## 2b. `wiki-self-heal` DOES NOT GO ON THIS MACHINE

**Its own autonomy rule: once started it continues without pausing for confirmation.** Put that
beside the other two facts — it researches the open web and it writes files — and **it is a
prompt-injection surface with the human deliberately removed.** No evidence of anything wrong with
it; unknown provenance, and this machine holds a live project and a public repository.

**And a Claude Code skill is instructions, not a library.** Installing `llm-wiki-setup` puts a
stranger's text into the channel that tells Claude what to do here, and its job is to write a
`CLAUDE.md` — **on top of the twenty-six-rule file that is this project's constitution.** No.

**What we take instead, and it is the valuable part:** the four constraints, verbatim, into our
own auditor — cannot modify sources, cannot delete pages, never auto-merges, **and no claim
without two independent sources.** That last one is stricter than anything we currently enforce
and it is the best thing in the repository.

**If he wants to try the skills, the assessment's answer stands: an empty folder, audit-only, no
research tools connected.** That tests the idea and risks nothing.

# 3. SUBSTITUTED — STEP 1 IS NOT A NEW VAULT, IT IS THE ONE WE HAVE

    spec step 1     vault scaffold + skills
    ruled step 1    none. The vault exists. It is this repository.

**The rooms, the map, the index and the log are already here and already carry two months of
work.** Scaffolding a second one is the failure in 2a.

# 4. THE HARD PART THE SPEC SKIPS, AND THE ANSWER IS CHEAPER THAN IT LOOKS

**"Inputs — small set of invalidating events." We have no event bus, and the spec does not say how
a program learns that a ruling landed.**

**It does not need one. This project already encodes its events in filenames and folders**, and
has done rigorously for two months:

    a ruling landed        a file named RULING_* appears in claude/
    a decision landed      DECISION_* in docs/
    a job opened           a memo appears in inbox/
    a job closed           the watcher moves it to correspondence/answered/
    a letter was answered  an ANSWERS: line inside the memo
    a deploy happened      the deploy receipt

**And the watcher already runs continuously and already watches that filesystem.** So the event
source is the file tree, the trigger already exists, and **v0 is a generator hung off a watcher we
built weeks ago** rather than new infrastructure.

**That is the whole reason this is small.**

# 5. ANSWERED BY SLEVEN THE SAME EVENING — CURRENT-STATE STOPS BEING "THE STATE"

**Asked and answered: yes.** Once the generated page exists, **it is the canonical current page
and `docs/CURRENT-STATE.md` is no longer what a desk reads to find out what is true.**

**Nothing is deleted and nothing is lost.** CURRENT-STATE becomes a deep file the digest points
into, exactly like every other document in the record. It keeps its history and it keeps its
owner.

**Three consequences, and the third is the one that will be forgotten:**

1. **The boot instruction changes.** "Read CURRENT-STATE, then NEXT" becomes "read the page".
   Every boot prompt in the project carries the old wording and each one has to be corrected, or
   desks keep paying the 115,000 tokens the page exists to save.
2. **`docs/DECISION_current-state-and-the-root-note-get-owners-2026-09-08.md` is superseded in
   part** — not on ownership, which stands, but on what the artefact is FOR. Superseded, not
   withdrawn.
3. **`claude/CURRENT-STATE.md` is a mirror of `docs/CURRENT-STATE.md`, and its only job was being
   a copy.** With a generated canonical page, **a hand-maintained mirror of a demoted file is the
   two-places defect in its purest form.** It is marked superseded and stops being updated on the
   day the page goes live. **It is not deleted** — nothing in this project is.

**None of this happens before the page exists and is proven.** Until then CURRENT-STATE keeps its
current job, and two current pages for a few days is acceptable.

# 6. NOT CHECKED

**`hot.md` is dropped.** Sleven: not important. Neither adopted nor pursued, and no desk should
spend a minute on it.

**Whether NEXT.md should also be a digest input.** It is 272,897 bytes and this desk could not
edit it tonight without moving the whole file across the bridge. **That is the cost problem
appearing inside the fix for the cost problem**, and it is noted rather than solved here.

*C1, 2026-09-12. Nothing built, nothing installed, nothing cloned.*
