# Update — received: the update feed 404s, and a Desktop-clutter complaint to investigate

From C1, 2026-08-10, off Sleven looking at his friend's running collector.
Logging receipt per rule 13. First order to arrive for `citizen-collector/`
through `inbox/` under the 2026-08-09 ruling.

Three items:

1. **The friend's window** — C1's reading is that it is an old build, not a
   missing feature, because `ui.go` already carries the picture-key row.
   Verifying that myself before agreeing.
2. **`releases/collector-latest.json` has never existed** — so every collector
   everywhere has been checking a URL that 404s. Will read `update.go`'s
   parsing and match the shape exactly rather than invent it.
3. **Two folders on the Desktop** — C1 could only find one folder-creation
   path and says to run it and look rather than theorise. I will.

One thing I am deciding up front, and flagging: **I will not run the collector
from the real Desktop.** Rule 6 puts anything outside this repo off-limits
without asking, and the Desktop is outside it. I will reproduce the same
condition in a scratch directory — an exe sitting at the root of a folder, run
as a casual user would — which answers the same question without writing to
somewhere I have no permission to touch. If that turns out not to reproduce it,
I will say so and ask rather than reach for the real Desktop.

Nothing commits or pushes without a go-ahead.
