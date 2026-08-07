# Update — received rev 5 data model addendum (C1, 2026-08-06)

**When:** 2026-08-05

Logging on arrival per hard rule 13. Job 2 was mid-flight when this landed; it
is being finished before any of this is acted on.

## The six rules

1. **Append, never overwrite.** A capture is a timestamped observation, not a
   row update. Current price becomes a query, not a field.
2. **Every row carries when, where and which patch** — the row, not the session
   header.
3. **Record absence.** A shop with no Quantainium is a fact. Each capture writes
   what the panel held *and* what was expected and missing. Flagged as the one
   that is genuinely expensive to add later.
4. **Match to IDs, keep the string.** Store the UUID/UEX id *and* the raw text
   read.
5. **Keep low-confidence reads.** Flag, never discard. Never publish them
   either.
6. **The session is a unit.** Start, end, profile, patch, route, everything
   observed inside it.

Plus: **write the position trail from day one**, even though nothing reads it.

**Stays out:** no reasoning, no natural language, no model, no service. The
boundary between the two programs is a file on disk.

## Status against what already exists

**Rule 2 is already satisfied in the grabber.** Every sidecar written by
`citizen-collector` carries `utc`, `patch`, `build`, `location`, `sequence`,
plus the capture method and window identity — on the row, not in a header. The
collector version is stamped too, which the crew-package addendum requires.

**Rule 4's "keep the string" principle is already the shape of the Game.log
parser** — it stores the parsed value, the pattern that produced it, whether
that pattern is verified, and `location_candidates[]` holding the raw lines it
could not confidently parse. That is rule 5 applied to location: the unreadable
reading is kept and flagged, never discarded and never presented as fact.

**Rules 1, 3 and 6 have nothing to attach to yet.** They govern observations of
shop panels, which is the reading half — no OCR, no atlas, no vocabulary in the
current binary by explicit scope. They are design constraints on a writer that
does not exist.

**The position trail is the one actionable item today** and it is genuinely
cheap: the collector already resolves the game window and reads Game.log on
every press. Adding a periodic position sample is a small, self-contained
addition to a program that is already running a message loop.

I have applied the same rule already in job 2 without being asked: every row in
the starmap/route output carries `snapshot` and `patch`, per the original rev 5
instruction to stamp every row.

**Next:** finish and verify job 2, file it, then job 3. The position trail and
any collector data-model changes come after — and I will flag before starting
whether the trail belongs in this binary or waits for the session writer, since
rule 6 implies a session container that does not exist yet.
