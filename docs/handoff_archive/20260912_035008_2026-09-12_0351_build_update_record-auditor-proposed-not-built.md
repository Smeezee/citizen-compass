# Build update - the record auditor is proposed, not built

**Code (Build), 2026-09-12. The measurement ran 03:47:46 to 03:47:53 CDT.**

**Proposed:** `claude/PROPOSAL_the-record-auditor-scope-first-2026-09-12.md`. The memo to Architecture asks for a ruling on whether to build, and where it lives.

## The measurement that sized it (read-only)

- **A naive check would flag 596 of 4,903 citations** across 1,830 documents: 455 absent, 111 moved, 30 set aside.
- **The scope is therefore limited** to documents dated 2026-09-12 or later, written under the citation convention.
- **There are two named green cases:** a project store named on the same line, and an `inbox/` address in transit.
- **Cost:** 7 s, about 0.3% of a sweep.

## One slip, recorded

The first measurement script globbed the whole repository once per flag. **It ran about six minutes beside the sweep before I stopped it**, from about 03:41 to 03:47. It was read-only. The bounded version replaced it.

**If the sweep that is running now reports a timeout, that overlap is the likely cause.** In that case I re-run the sweep alone rather than deploy on it.

## In flight

The solo sweep for the category change. It deploys only if green.
