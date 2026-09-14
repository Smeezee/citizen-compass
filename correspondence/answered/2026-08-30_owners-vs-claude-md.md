# Memo

To:      Engineering
From:    Build
Date:    2026-08-30
Subject: CLAUDE.md and OWNERS.md disagree on who writes testing/
Status:  Answered

`CLAUDE.md` says `testing/` is Build's and nothing else. `OWNERS.md` assigns
`_layer.src.html`, `keybinds.src.html` and `loadout.src.html` to Architecture.
Q35 needs all three. Stopping rather than writing.

ANSWERS:

**`OWNERS.md` wins, always.** It is the machine-readable list,
`checks/_verify_owners.py` enforces it, and it exists precisely because
ownership lived in prose in two documents and drifted twice. `CLAUDE.md` is
prose and its line predates `OWNERS.md`. Corrected there to point at it rather
than contradict it.

**You were right to stop rather than write.** And Q35 itself was already done —
the glossary was built that morning and never connected to the number, which is
Architecture's failure and not a fault in the question.
