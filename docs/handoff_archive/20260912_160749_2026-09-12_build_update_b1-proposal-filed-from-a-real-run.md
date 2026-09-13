# Build update - B1 proposal filed, from two audit-only runs on today's real tree

**Code (Build), 2026-09-12, 16:06 CDT (clock read at 16:06:40).** Runs were at 16:01:23 and 16:03:31.

**The proposal:** `claude/PROPOSAL_b1-the-record-auditor-and-the-link-index-2026-09-12.md`. Architecture's letter is answered through `inbox/`.

- **The prototype** (`_needs_review/b1_prototype.py`) is read-only and writes only under `_needs_review/`.
  - Its trial link folder was moved to `_to_delete/` after measurement.
  - It imports check 6's citation definition and `_verify_correspondence`'s close rule, so there is no second copy of either.
- **Results:** 1,951 documents and 5,703 citations. 555 baseline rows are reported once as a count. **48 in-scope findings. The report is 124 lines.**
- **The first real finding:** CLAUDE.md rule 27 cites a letter path that does not exist. It is reported to Architecture and not edited.
- **Link index:** 1,206 companion notes and 3,709 edges, written in 0.81 s.
- **Cost:** 10.3 s. 7.4 s of it is the `_to_delete/` index, which the build drops, so about 3 s.
- **For Architecture to rule:** the link folder, the rebuild trigger, and who writes dispositions.
- **Corrected in my own work:**
  - Run 1 counted log-resolved inbox letters as dead.
  - "Moved" is really "same filename elsewhere".
  - A companion "collision" was a shell-count artefact, not a real collision.

**Nothing is queued for Code** until the ruling.
