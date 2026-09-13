# ACCESS MAP — the Design desk's files, and where Echo can actually reach them

    from    C1, architecture, 2026-09-12
    order   Sleven: Echo takes the Design desk and needs reliable access.
            GitHub for repo material, Dropbox for standalone references,
            no Windows-local paths alone.
    status  READ-ONLY. Nothing pushed, deployed, altered, deleted or
            overwritten. Nothing here is done; the push it names is
            NOT AUTHORISED and has not been attempted.

---

# THE ANSWER FIRST, AND IT IS NOT THE ONE THE ORDER ASSUMES

**1. The GitHub repository is PUBLIC, and it is five days stale.**
`github.com/Smeezee/citizen-compass`, branch `main`, newest commit **2026-09-07**
(`c8ab1d0`, *"The front-page tooling enters history"*). Before that, 2026-08-30.

**Public means Echo needs no account and no connector** — a raw URL is enough. That is
the one piece of good news and it makes GitHub the right channel.

**2. Most of what Echo asked for is NOT in the repository.** `design/` is not in the
repo at all. `claude/` is in the repo and contains **one file**. `docs/` is there with
335 entries, and the current UX Doctrine is not among them.

**3. PUSHING IS PUBLISHING, AND NOBODY ASKED THAT QUESTION.** The repo is public, so a
push does not "give Echo access" — it puts this project's internal design doctrine,
charter, findings and prototype in front of the world, permanently and in history.
**That is an owner decision under hard rule 8 and it is the real gate here, not the
mechanics.**

**4. I cannot use Dropbox at all.** No Dropbox tool exists in this session. I cannot
upload, cannot verify an upload, and cannot confirm what a connected Dropbox account
can see. **The Dropbox half of the order cannot be executed by this desk.**

---

# GITHUB — WHAT IS ALREADY THERE AND NEEDS NOTHING

    repository   Smeezee/citizen-compass
    branch       main
    visibility   PUBLIC — no account, no connector, no token needed
    last commit  2026-09-07, c8ab1d0
    read as      https://raw.githubusercontent.com/Smeezee/citizen-compass/main/<path>

**Design-desk material committed and reachable right now:**

    docs/DESIGN_ten-mining-page-concepts-2026-08-28.md
    docs/ERRATUM_the-mining-figures-2026-08-29.md
    docs/ORDER-C3-design-ten-mining-page-concepts-2026-08-28.md
    docs/PROPOSAL_make-the-ship-the-page-2026-08-30.md
    docs/SPEC_the-ship-page-becomes-an-instrument-2026-08-30.md
    docs/DESIGN_the-ship-is-the-instrument-2026-08-30.md
    docs/DESIGN_the-visual-language.md
    docs/DESIGN_what-else-the-collector-could-see-2026-08-30.md
    docs/REFERENCE_the-words-players-actually-use-2026-08-29.md
    docs/ARCHITECTURE_DECISIONS.md

**Context files, present but STALE against disk** — `CLAUDE.md` (the committed copy
states 15 hard rules; the working copy has 26), `docs/CURRENT-STATE.md`, `NEXT.md`,
`OWNERS.md`, `LIVE.md`, `ASK_OVERLAY_SETUP.md`. **Echo may read them for shape and
must not treat any number in them as current.**

**NOT in the repository and deliberately staying out:** `correspondence/` — the desks'
private mail. It is not committed, it is not being proposed for a push, and it is
excluded by the order.

---

# ON DISK, NOT ON GITHUB — THIS IS THE GAP

**Every file below exists on the machine and is absent from `main`. None of it is
reachable by Echo today.**

**THE ITEMS THE ORDER NAMED BY NAME:**

    the standing pack        claude/ECHO_DESIGN_DESK_PACK.md
    current UX Doctrine      docs/UX_DOCTRINE.md
    the desk's charter       docs/CHARTER-C3-design-and-imagination.md
    Keyboard First prototype design/keybindings/keys.html
    Angles material          design/ANGLES.md  (+ design/README.md)

    flight-stick, all three  docs/FINDING_nothing-in-the-browser-knows-where-a-
                               stick-button-is-2026-08-31.md
                             docs/DESIGN_dont-draw-the-stick-2026-08-31.md
                             docs/FINDING_the-stick-panel-is-the-hardpoint-
                               viewer-2026-08-31.md

    front-page concept       docs/DESIGN_the-front-page-and-the-url-defect-2026-08-30.md
                             docs/DECISION_the-main-page-is-the-drydock-2026-08-30.md
    fact engine              docs/PROPOSAL_the-fact-engine-2026-08-31.md
                             docs/DESIGN_the-fact-store-is-mostly-already-built-2026-09-06.md
                             docs/SCOPE_the-fact-engine-and-the-question-engine-
                               share-a-spine-2026-09-06.md
    keybinding line          docs/DESIGN_the-easiest-keybinding-setup-2026-09-06.md
                             docs/CIC_survey-keybind-tools-and-the-gap-2026-09-06.md
                             docs/FINDING_i-have-now-seen-the-games-own-keybinding-
                               screen-2026-09-07.md
                             docs/DESIGN_tap-lights-the-key-hold-opens-it-2026-09-07.md
    map correction           docs/RESPONSE-CIC-our-map-is-the-thing-that-is-wrong-2026-08-31.md
    this desk's own audit    docs/AUDIT_which-of-this-desks-documents-are-actually-
                               on-disk-2026-09-12.md

**THE PROTOTYPE NEEDS NOTHING ELSE.** `design/keybindings/keys.html` is 132,850 bytes
and self-contained — bindings embedded, two inline `<script>` blocks, two inline
`<style>` blocks, **no local images, stylesheets, scripts or data files.** Its only
external reference is a Google Fonts stylesheet, which loads from the internet. Its
own README says so and the file confirms it. **Copy that one file and it opens.**

---

# CLAUDE.AI PROJECT ONLY — NOT ON DISK AND NOT ON GITHUB

**These exist in the claude.ai project and nowhere a file tool can reach. Echo cannot
be given them by any of the three channels in the order.**

    DESIGN_ten-eyes-2026-09-08                          the Ten Eyes design
    VERIFIED_the-ten-eyes-arithmetic-holds-2026-09-08    its verification (C5)
    AUDIT_the-design-desk-four-documents-2026-09-08      C5 on the eyes and the angles
    DOCTRINE_sixty-angles-2026-09-08                     the Angles REASONING
    FINDING_a-window-can-let-the-mouse-through-2026-09-07        overlay research
    FINDING_no-rule-says-yes-and-no-rule-says-no-about-overlays-2026-09-08
    FINDING_cig-names-the-overlays-that-break-and-ours-is-not-one-of-them-2026-09-08
    SPEC_the-front-page-becomes-the-wall-2026-08-31
    FINDING_this-project-keeps-reinventing-the-same-idea-2026-09-08
    ASSESSMENT_ux-doctrine-v6.1-adoption-2026-09-08
    RULINGS_the-design-tray-worked-to-empty-2026-09-12
    GATHER_the-design-desks-citizen-compass-work-2026-09-12

**Two of those are the worst gaps in the list.** The Ten Eyes design and the Sixty
Angles doctrine are both named in the order, **the angles method was ruled BINDING on
every desk on 2026-09-08**, and a desk that can only read files cannot read the
doctrine it is bound by. `design/ANGLES.md` holds the checklists; the reasoning behind
them is project-only.

**And one is cited with a path that does not exist.** `docs/CURRENT-STATE.md` names
`docs/SPEC_the-front-page-becomes-the-wall-2026-08-31.md`. There is no file of that
name. **Reported by the Design desk this morning; `CURRENT-STATE.md` is C1's and the
citation is being corrected there, not here.**

---

# PERMANENTLY LOST UNLESS ONE CHAT SURVIVES

**The Design Desk Handoff v1** — nine numbered sections, produced across three
messages in a chat on Sleven's instruction. **Not in the project, not on disk, not in
any tray.** If that conversation is gone, it is gone.

**It is not being reconstructed.** The scope it was written against has moved — the
Looking Project left, the self-stop was lifted, two identity rows merged, the stick
thread closed by two rulings. **A rebuild today would be a different document wearing
the old one's date.** Named as an owner decision rather than quietly regenerated.

---

# WHAT WOULD MAKE THE GAP REACHABLE, AND WHAT IT COSTS

**OPTION A — one push of the named documentation to `main`. NOT AUTHORISED.**

    scope        16 files under docs/, design/README.md, design/ANGLES.md,
                 design/keybindings/keys.html, claude/ECHO_DESIGN_DESK_PACK.md
    who runs it  Code. This desk runs no git command that touches the index.
    result       every file above readable by Echo at a raw URL, no account

**Three things Sleven has to weigh before that, and the first is the real one:**

**1. IT IS PUBLICATION, NOT ACCESS.** A public repo means this is not "sharing with
Echo" — it is publishing the charter, the doctrine, the findings and the prototype to
anyone, permanently, in history where a later delete does not remove them. **Hard
rule 8. His alone.**

**2. THE COMMIT GUARD MAY REFUSE PART OF IT, CORRECTLY.** The rule 2 exception covers
named documentation files. **`design/keybindings/keys.html` is a prototype, not a
document**, and the guard is built to refuse exactly that kind of drift. If it refuses,
that is the guard working and it needs his separate word, not a workaround.

**3. THE STALE FILES ARE A SECOND DECISION.** `CLAUDE.md`, `CURRENT-STATE.md`,
`NEXT.md` and `OWNERS.md` on `main` are weeks behind. Pushing documentation without
them leaves Echo reading a 15-rule `CLAUDE.md` next to a current doctrine. **Either
both go or Echo is told in writing which files on `main` are not current.**

**OPTION B — Dropbox. THIS DESK CANNOT DO IT.** No Dropbox tool in this session. It
would need either a Dropbox connector added to a Claude session, or Sleven copying the
files himself — which is the pattern his own standing rule exists to remove, so it is
named as a cost rather than recommended.

**OPTION C — attach the files to Echo directly.** Works today, needs no push and no
publication, and **does not survive**: Echo gets one copy with no path to re-read it,
which is the "it exists only in a chat" failure this whole map is about.

**MY RECOMMENDATION, AND THE REASONING RATHER THAN THE VERDICT.** The publication
question is genuinely his and I am not going to pre-answer it. **If he is willing to
publish, Option A is clearly right** — public repo, raw URLs, no account, survives,
and the files are our own work with no CIG assets in them. **If he is not, there is no
good channel**, and the honest answer is that Echo cannot hold this seat properly
until one exists.

---

# ACCESS MAP — THE SUMMARY HE ASKED FOR

    IN GITHUB, READABLE NOW        10 design documents + ARCHITECTURE_DECISIONS,
                                   under docs/ on main. Plus 6 context files
                                   that are present and STALE.

    ON DISK ONLY, NEEDS A PUSH     16 docs/ files including the current UX
                                   Doctrine and the charter; all three
                                   flight-stick documents; the whole design/
                                   folder including the Keyboard First
                                   prototype and the Angles lists; and the
                                   standing pack in claude/.

    CLAUDE.AI PROJECT ONLY         12 documents including the Ten Eyes design
                                   and verification, the Sixty Angles doctrine,
                                   all three overlay findings, and the wall
                                   spec that CURRENT-STATE cites by a path
                                   that does not exist.

    PERMANENTLY LOST               the Design Desk Handoff v1, unless its chat
                                   still exists.

    NOT OFFERED, BY THE ORDER      correspondence/, credentials, anything from
                                   the Looking Project. None of it is in the
                                   repo and none is proposed for one.

---

# METHOD, AND WHERE I AM NOT CERTAIN

**CHECKED.** The repository read directly in a browser: root tree, `docs/` tree,
`claude/` tree, commit history. Individual files tested by raw URL. The machine's
`docs/`, `design/` and `claude/` folders listed directly. `keys.html` opened and every
`src`, `href`, `fetch` and CSS `url()` in it extracted. The project-only list taken
from the claude.ai project and cross-read against the Design desk's own audit of the
same question this morning.

**CONFIDENT.** That the repo is public, that `main`'s newest commit is 2026-09-07,
that `design/` is absent from the repo, that `claude/` holds one file, that
`docs/UX_DOCTRINE.md` is not on `main`, and that `keys.html` needs no companion files.

**LESS CONFIDENT — stated rather than smoothed over.** The `docs/` membership test read
the rendered file list from GitHub's page rather than from the API, which was rate-
limited. **If that page truncated its listing, a file I report as absent could be
present.** Every "absent" item worth acting on should be re-tested by its raw URL
before anybody relies on it — one fetch each, and two of them already were.

**NOT CHECKED.** Whether any project-only document exists on disk under a different
name; the comparison is by exact filename. Whether the connected Dropbox account or
Echo's GitHub connector can reach anything — no tool here can see either.

*C1, 2026-09-12. Nothing pushed. Nothing changed.*
