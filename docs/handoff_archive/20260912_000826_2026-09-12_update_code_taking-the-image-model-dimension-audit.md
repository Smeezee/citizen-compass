# Update — Code is taking Owner's image, model and dimension audit (phase one)

**2026-09-12 00:08 CDT / 05:08 UTC.** Owner's order, filed 00:05:
`2026-09-12_memo_build_the-image-model-and-dimension-audit-is-yours.md`.

**Read-only, as ruled.** Nothing modified, created in the tree beyond the
deliverables, moved, renamed, downloaded or deleted, and **no finding corrected as
I go.** Browser render checks skipped entirely, per his ruling. Phase two
(external research) only after phase one is in.

## THE ONE ACCESS POINT, REPORTED BEFORE WORK AS HE ASKED

**His memo says I have the database. In practice I do not:** there is no
`DATABASE_URL` in the environment, the connection falls back to localhost with no
password, and credentials are closed (rule 23) — I am not going looking.

**It does not block phase one.** I traced the front page's chain this afternoon
under Q57: `testing/index.html`'s SHIPS literal → `build_frontpage_data.py` →
`frontpage_data.json` → `build_next_frontpage.py` → the page. **The database is
not in it.** So item 1's "which source generates the cards" is answerable from
disk. If any later item genuinely needs the database, it will be marked NOT
PERFORMED with the reason, never estimated.

## HOW I AM READING "ALL 256, NOT A SAMPLE"

The models are glTF binary. **Everything item 4 asks for that the file itself
states — meshes, materials, textures and whether they are embedded, UV sets,
named nodes, animations, levels of detail, and each position accessor's
bounding box — is in the file's JSON chunk**, which I can read with the standard
library and no third-party tool. **Geometry I would have to decode is marked as
such** rather than guessed, and "what the file states / what the project states
elsewhere / what I measured / what I inferred" is kept in separate columns, as he
asked.

**Deliverables:** one report in `claude/` and five CSVs beside it — inventory,
missing pictures, missing models, model capabilities, dimension coverage.

*Code, 2026-09-12 00:08 CDT.*
