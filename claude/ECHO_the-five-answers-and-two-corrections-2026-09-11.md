# ECHO — the five answers and two corrections

**Received 2026-09-11, in reply to `claude/ECHO_full-update-for-a-cold-read-2026-09-11.md`.
Echo is an outside reviewer with no repository access and no mailbox. Her text as
Sleven carried it in, verbatim, with her sources.**

**Sleven ruled on all five the same hour.** His words:

> "Make the committed Git repository the official record and treat the cloud as a
> copy. Freeze automation because it is safely off and disconnected. Before Q54
> deploys, replace the false footer with honest wording; unfinished features are
> acceptable on the test site, false claims are not. Reduce duplicate reports,
> unnecessary desk reviews and routine owner approvals. For the Perplexity export,
> remove any document as soon as its approved version changes, then return it only
> after reapproval."

Routed as `memo_build_hold-the-q54-upload-until-the-footer-is-honest.md` and
`memo_architecture_git-is-the-record-automation-is-frozen-and-three-more-rulings.md`.

**Not yet checked against the source:** her Graphify correction. The install is parked;
check it before anyone installs.

---

## HER REPLY, VERBATIM

Sir, two corrections before the five answers:

* The path allowance is not unproven. It selected the one write that proceeded automatically; no-prompt mode denied the unmatched writes. The combined containment passed.
* Graphify's local MCP is not necessarily network-free. Its server includes GitHub PR tools that can call authenticated `gh`. Code-only graph construction is local; the complete MCP toolset is broader.

Short answers

1. Git repository as record, cloud as generated mirror: Yes.
2. Freeze automation at containment: Yes.
3. Deploy Q54 with the false footer: No. Correct the sentence first.
4. First process to cut: Duplicate reporting, unnecessary desk hops and owner approvals for reversible work.
5. Export behavior: Drop a document when its approved content changes.

### 1. Two stores, one record

ESTABLISHED: The authoritative record should be the committed Git repository, not merely whatever happens to be in the local folder. Git describes itself as a "content-addressable filesystem," meaning recorded content has a specific identity. [Git documentation](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects)

RECOMMENDATION: Make the flow one-way:

Work is completed on disk → committed to Git → copied into the cloud project as a mirror.

The cloud copy must never become independently editable authority. Every mirror update should record its source commit or content hash.

The proposed missing-path check is worthwhile but insufficient. It should establish that a referenced document:

* Exists.
* Is tracked by Git.
* Belongs to the authoritative document set.
* Matches the recorded revision when one was specified.

FORECAST: If both cloud and disk remain writable records, they will drift again.

### 2. Freezing automation

ESTABLISHED: Freezing is safe because the switch is absent and the watcher is not connected to the launcher. The unfinished system cannot begin waking desks by itself.

RECOMMENDATION: Freeze it. Record the exact current version, switch state, completed steps and required restart checks. Then stop extending it.

The primary risk is future staleness—not present execution. When automation resumes, Code must recheck the specifications, dependencies and containment before continuing.

FORECAST: Finishing the brakes now would consume product time protecting a capability that remains deliberately disconnected.

### 3. Q54 and the false footer

ESTABLISHED: The testing site may legitimately contain incomplete features. It should not contain a knowingly false claim about data verification.

RECOMMENDATION: Block Q54 deployment only long enough to replace the footer with accurate wording. Do not require Q55 to restore all missing confidence information first.

Something equivalent to this would be truthful:

Verification coverage is incomplete and is being restored.

The rest of Q54 can proceed on the password-gated testing site.

FORECAST: Leaving the false statement will corrupt testing because reviewers may assume missing verification details exist somewhere they cannot see.

### 4. Keeping process proportional

ESTABLISHED: There is no universal correct number of rules or desks. The measurable warning signs are already present:

* Owner letters outnumber product decisions.
* Several desks review reversible implementation details.
* Routing and status records consume more time than the underlying change.
* Multiple hops occur without introducing new evidence.
* The owner remains involved in routine internal choices.

Google defines toil partly as work that is "manual, repetitive, automatable, tactical" and lacking enduring value. [Google SRE](https://sre.google/sre-book/eliminating-toil/)

RECOMMENDATION: Cut in this order:

1. Duplicate status reports and day-page restatements.
2. Mandatory second opinions for reversible changes.
3. Desks with overlapping responsibilities.
4. Owner approval for ordinary local implementation decisions.

Keep the controls around database destruction, spending, external publication, deployment, security boundaries and final independent verification.

The relevant principle is: "Working software is the primary measure of progress." [Agile principles](https://agilemanifesto.org/principles.html)

### 5. Export behavior

ESTABLISHED: If approval attaches to a document's hash, changing the document creates new, unapproved content.

RECOMMENDATION: Remove it from the export immediately when its hash changes. Notify that reapproval is required. Do not keep an automatically updated copy available to the outside reviewer.

SLSA defines provenance as verifiable information describing "where, when, and how something was produced." [SLSA provenance specification](https://slsa.dev/spec/v1.2/provenance)

FORECAST: "Stay current and report afterward" will eventually expose an unreviewed path, project name or security detail before anyone reads the change report.
