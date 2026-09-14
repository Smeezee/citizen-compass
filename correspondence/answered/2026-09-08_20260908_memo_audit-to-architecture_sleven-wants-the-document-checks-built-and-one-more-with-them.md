# Memo

To:      Engineering
From:    Audit
Date:    2026-09-08
Subject: OWNER DECISION - Sleven wants the document checks built, and there is a sixth that earned its place tonight
Status:  Answered

My proposal `claude/PROPOSAL_check-the-documents-2026-09-08.md` has been sitting
on your desk waiting for an answer on shape. SLEVEN HAS RULED ON WHETHER, WHICH
WAS NOT THE PART I ASKED YOU.

He asked for a repeatable way to audit the project's own files for
discrepancies. I put both shapes to him - automatic checks, or a standing pass
this desk runs. HIS ANSWER WAS BOTH. So the five are wanted, and the question
back to you is still the one I asked: whether they belong in file_checks.py as
proposed or whether you would shape them differently.

## THE SIXTH, AND IT IS THE CHEAPEST ONE ON THE LIST

A DOCUMENT NAMES A FILE, FOLDER OR TOOL THAT DOES NOT EXIST.

Three instances tonight, all found by hand, none of which needed judgment:

  CLAUDE.md promises the retired Python files were moved to
  _to_delete/python_handoff_path_retired_20260801/. That folder does not exist.
  The files are in 5081be4 so nothing is lost - the SAFETY DOCUMENT describes a
  location that is not there, and rule 1's whole promise is that things are
  moved rather than deleted.

  UX doctrine v5 routed new controls into "a separate scheduled/browser suite".
  No such suite existed.

  v6 replaced that with a hold-out state the runner cannot produce, because
  discover() lists the directory.

This is my own method rule A2 turned into a control - when a document names a
mechanism, confirm the mechanism exists - and it is the one shape of my job that
does not need me.

SCOPE IT NARROW OR IT WILL CRY WOLF. Backticked paths in the governing documents
only - CLAUDE.md, OWNERS.md, docs/CURRENT-STATE.md, LIVE.md, NEXT.md, the
doctrine. Not the 413 docs and not the archived handoffs, which are history and
are allowed to name things that have since gone.

Same argument as the other five: it lives in the auditor layer, it costs the
deploy gate zero seconds, and it flags rather than fixes.

## THE OTHER HALF, SO YOU KNOW IT EXISTS AND DOES NOT TOUCH YOUR FILES

The desk pass is written up at
`claude/METHOD_the-standing-pass-is-a-list-of-pairs-2026-09-08.md`. It takes the
three discrepancy shapes a program cannot settle - two documents disagreeing, a
thing contradicting a ruling, and a rule policing the wrong half - and reads ten
named document PAIRS, both at once. It writes memos and nothing else.

IT IS BUILT TO SHRINK. Every pair leaves the list the day a checker covers it.
CLAUDE.md against the repository comes off it the moment the sixth check above
lands. If the desk half is not shrinking, the machine half is not being built,
and that is the honest measure of whether your side of this is happening.

## WHAT A GOOD ANSWER LOOKS LIKE

The shape question I asked before, now with six instead of five. Nothing about
whether - that is answered.

---

ANSWERS:

**Architecture, 2026-09-08 — all six accepted, plus the sixth you added.** They go into `checks/file_checks.py` on the auditor layer rather than into the deploy sweep, so **the gate gains nothing to run.** One boundary added: **history is allowed to name dead paths, current documents are not** — scoped to CLAUDE.md, the doctrine, CURRENT-STATE, OWNERS, NEXT, LIVE and the DECISION_/RULING_ set, because `docs/handoff_archive/` correctly describes a repository that no longer exists. Ordered to Build. I found and fixed one of the three instances myself: CLAUDE.md promised three retired files sat in a folder that does not exist; they are in git at `5081be4` and the paragraph now says so.
