# AUDIT — which of this desk's documents are on disk, which are only in the claude.ai project, and one that is only in a chat

    from    Design (C3), 2026-09-12
    asked   by Sleven: "are all the projects that have been worked on actually
            put into the files? Are they just still sitting here in this chat?"
    method  `docs/` listed directly on the machine and compared name by name
            against this desk's documents in the claude.ai project. Not sampled.
    answer  NO. Three states exist and only one of them is safe.

---

## WHY IT MATTERS, IN ONE LINE

**Code reads the repo. The watcher reads the repo. A desk booted with file access
reads the repo.** A document that exists only in the claude.ai project is invisible
to all three, and the project's own rule already says so: *a work order that exists
in the claude.ai project but not in the repo has not been delivered.*

**The same shape is already a recorded finding** —
`claude/FINDING_the-documents-are-not-on-disk-and-the-memos-announcing-them-are-2026-09-10.md`
— which cost two desks nine and a half hours. This audit is that finding applied to
this desk's own record.

---

## STATE 1 — ON DISK AND SAFE

Everything this desk wrote about the front page, the ship page, mining and the fact
engine is in `docs/` and always was:

    DESIGN_ten-mining-page-concepts-2026-08-28
    ERRATUM_the-mining-figures-2026-08-29
    ORDER-C3-design-ten-mining-page-concepts-2026-08-28
    DESIGN_the-front-page-and-the-url-defect-2026-08-30
    PROPOSAL_make-the-ship-the-page-2026-08-30
    SPEC_the-ship-page-becomes-an-instrument-2026-08-30
    DECISION_the-main-page-is-the-drydock-2026-08-30
    PROPOSAL_the-fact-engine-2026-08-31
    RESPONSE-CIC-our-map-is-the-thing-that-is-wrong-2026-08-31

**It is not a date cutoff.** Two documents written on 2026-08-31 are on disk and
three more written the same day are not. **Whether a document reached the disk was
decided one document at a time, by hand, which is why it is inconsistent.**

## STATE 2 — PUT ON DISK TODAY

Five, written to `docs/` on 2026-09-12, each carrying a line saying it was
project-only until then:

    CHARTER-C3-design-and-imagination
    DESIGN_the-easiest-keybinding-setup-2026-09-06
    CIC_survey-keybind-tools-and-the-gap-2026-09-06
    FINDING_i-have-now-seen-the-games-own-keybinding-screen-2026-09-07
    DESIGN_tap-lights-the-key-hold-opens-it-2026-09-07

**The charter is the sharpest case in the whole audit.** It is the standing brief for
every C3 session, it opens with *"read this at the start of every C3 session"*, and
until today **a C3 booted with file access could not read its own charter.**

**Two of the five gained correction blocks on the way to disk**, rather than being
copied as they stood: the keybinding plan's §2 is marked withdrawn where it sits, and
the tap/hold document now records that "the key opens" was chosen. A document copied
forward with a claim its author has since withdrawn is worse on disk than off it.

## STATE 3 — STILL CLAUDE.AI PROJECT ONLY

Measured against the `docs/` listing today. These exist in the project and nowhere on
the machine:

    SPEC_the-front-page-becomes-the-wall-2026-08-31
    FINDING_nothing-in-the-browser-knows-where-a-stick-button-is-2026-08-31
    DESIGN_dont-draw-the-stick-2026-08-31
    FINDING_the-stick-panel-is-the-hardpoint-viewer-2026-08-31
    FINDING_a-window-can-let-the-mouse-through-and-this-is-how-2026-09-07
    FINDING_no-rule-says-yes-and-no-rule-says-no-about-overlays-2026-09-08
    FINDING_cig-names-the-overlays-that-break-and-ours-is-not-one-of-them-2026-09-08
    DESIGN_ten-eyes-2026-09-08
    DOCTRINE_sixty-angles-2026-09-08
    FINDING_this-project-keeps-reinventing-the-same-idea-2026-09-08
    ASSESSMENT_ux-doctrine-v6.1-adoption-2026-09-08
    RULINGS_the-design-tray-worked-to-empty-2026-09-12
    GATHER_the-design-desks-citizen-compass-work-2026-09-12

**AND ONE OF THEM IS CITED WITH A `docs/` PATH THAT DOES NOT EXIST.**
`CURRENT-STATE.md` names `docs/SPEC_the-front-page-becomes-the-wall-2026-08-31.md`.
**There is no file of that name in `docs/`.** Anyone following that citation finds
nothing and has no way to tell whether the document was lost or never arrived.
**That is a pointer to a file rather than a file, which is the exact shape the
2026-09-10 finding is about.** Reported here; `CURRENT-STATE.md` is C1's.

**`DOCTRINE_sixty-angles` is the second-worst case after the charter**, because the
method it describes was ruled BINDING on every desk, and a desk that can only read
files cannot read the doctrine it is bound by. `design/ANGLES.md` is on disk and
points upward to `CCDesk-logs/ANGLES.md`, so the checklists are reachable; the
reasoning behind them is not.

## STATE 4 — IN A CHAT AND NOWHERE ELSE

**The Design Desk Handoff v1.** Nine numbered sections with evidence labels, produced
across three messages on Sleven's instruction — *"return the handoff here"* — for
review by ChatGPT alongside a separate handoff from the project head, while he
considered assigning research and possibly design work to Perplexity and Comet.

**Chat was the correct destination at the time and it is the only copy.** It is not
in the project, not on disk, and not in any tray. **If that conversation is lost, it
is gone**, and it is the only document that describes this desk as a seat rather than
describing its output.

**Not reconstructed here**, because the scope it was written against has since moved —
the Looking Project left Citizen Compass, the self-stop was lifted, the two identity
rows were merged, and the stick thread was closed by two rulings. **A handoff rebuilt
today would be a different document, and pretending otherwise would date it wrongly.**
**It is named as an owner decision rather than quietly regenerated.**

---

## WHAT I WOULD DO, AND THE PART THAT IS NOT A ONE-OFF

**Finishing state 3 is an afternoon and it is this desk's own work**, so it needs
nobody's permission. It is not done in one sitting on purpose: each document has to be
read for withdrawn claims before it is copied, the way the five today were, or the
copy carries errors the project has already corrected somewhere else.

**The part that matters more: nothing decides which documents reach the disk.** It has
been a per-document judgement call for two weeks and it has been inconsistent for two
weeks. **A rule that lives in somebody's habit is not a rule** — this project's own
phrase for it is a rule keyed to a proxy rather than to the thing itself, and here the
proxy is "whoever wrote it remembered."

**The cheap version:** a document that any other desk must be able to act on goes to
the repo, and the claude.ai project holds the copy for reading. **The expensive
version is a control that reads the project's document list and reports what has no
file behind it.** The cheap version is a habit and will fail the same way. The
expensive one is the one that survives.

---

## CHECKED AND NOT CHECKED

**CHECKED.** `docs/` listed in full on the machine today and compared name by name
against this desk's documents. `design/` listed. The five in state 2 written and their
writes confirmed. `CURRENT-STATE.md`'s citation of the wall spec read in the file.

**NOT CHECKED.** Whether any of the state-3 documents exist on disk under a DIFFERENT
name — the comparison was by exact filename, so a renamed copy would read as missing.
Whether `docs/` is the right home for all of them rather than `claude/` on disk, which
is an ownership question and not this desk's. Whether other desks have the same gap;
this audit covers only documents this desk wrote.

*Design (C3), 2026-09-12.*
