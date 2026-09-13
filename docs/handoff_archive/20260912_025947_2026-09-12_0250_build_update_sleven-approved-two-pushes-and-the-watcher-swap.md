# Build update - Sleven approved both pushes and the watcher swap, in his own answers to this session

**Code (Build), 2026-09-12, about 02:49 CDT.** Rule 2 requires his word "in that message, for that change". So I asked him directly. A relayed go from Architecture was not treated as one. His answers, verbatim:

    Push one  (design/briefs/README.md + BRIEF-001, nothing else)   "Yes, push one"
    Push two  (the ACCESS-MAP corpus: 16 docs/ files, design/README.md,
               design/ANGLES.md, claude/ECHO_DESIGN_DESK_PACK.md)     "Yes, without keys.html"
    Watcher swap (inbox_watcher_pending_20260912b.exe, STEP A procedure,
               after tonight's zero-dimension deploy)                 "Yes, swap it"

## Scope, exactly as approved

- **`design/keybindings/keys.html` stays out.** He chose "without keys.html".
- **The stale `CLAUDE.md`, `NEXT.md` and `OWNERS.md` on `main` are not part of either push.** He was told they stay stale unless he says otherwise, and he did not say otherwise.
- **The swap waits for the zero-dimension deploy.** Its sweep is running now.

## Order of work

1. Push one.
2. `desk fetch`: the tool is written at `scripts/desk.py`, and its self-test comes first.
3. Push two.
4. The deploy.
5. The swap.
