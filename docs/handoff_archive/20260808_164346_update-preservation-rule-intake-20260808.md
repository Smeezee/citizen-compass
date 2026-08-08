# Update — never-delete importer rule: intake (2026-08-08)

Filed on intake per rule 13, before any work.

Received from Sleven: implement `WORKORDER_preservation-model-and-never-delete-rule.md`
§3 first, then file a handoff update closing the record gap.

**Why this jumped the queue:** it is the only outstanding item with a deadline.
The rule must land *before the next snapshot import*; after that the loss is
silent and unrecoverable. Port Olisar is already gone — 2,066 gazetteer
entities and it is not one of them — and the Aurora Mk I survives only because
a snapshot caught it by luck.

Also noting a record gap I will close afterwards: `LATEST_HANDOFF.md`'s newest
entry is 13:04, while nine documents were created 14:18–16:37. The watcher is
healthy (PID 8856, update #260 at 16:38) and correctly filed those as docs, not
updates — the gap is that no update was filed, not a pipeline fault.

Holding off on `docs/prompt-code-holoviewer-all-ships.md` until this lands.
