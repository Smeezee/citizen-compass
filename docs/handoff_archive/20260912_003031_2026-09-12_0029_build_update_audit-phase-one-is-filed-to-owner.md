# Build update - audit phase one is finished and filed to Owner; phase two waits for him

**Code (Build), 2026-09-12 00:29 CDT, read from the machine clock.**

**Done:** Owner's audit, phase one. It is read-only, and nothing was corrected along the way.

- Report: `claude/AUDIT_images-models-dimensions-phase-one-2026-09-12.md`
- Five CSVs beside it: `claude/AUDIT-2026-09-12-*.csv`
- Memo to Owner: `2026-09-12_memo_owner_phase-one-of-the-image-model-and-dimension-audit-is-in.md`

**Measured on the way, and worth knowing before anyone uses a model box:**

- Raw accessor bounds are wrong by up to 100x on the 31 files that carry node transforms.
- I recomputed the boxes in world space: `_needs_review/audit/world_bbox.py`, which reads the JSON chunk only.

**Not started:** phase two, the external dimension research. Owner's order is that it starts only after phase one. The six cards with no dimension from any source are its list.

**Still in flight:** the solo sweep, which started at 00:22 CDT. The T-008 and Q58 +3 deploy goes only if it comes back green.
