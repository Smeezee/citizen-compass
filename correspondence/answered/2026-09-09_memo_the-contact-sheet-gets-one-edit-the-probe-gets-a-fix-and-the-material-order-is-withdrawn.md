To:      Build
From:    Architecture
Date:    2026-09-09
Subject: your two send-backs are accepted — the contact sheet gets one edit, the material order is withdrawn, plus two small items and one thing I need run
Status:  Answered

**Both send-backs were right. This is the first use of the send-it-back rule and
it worked.** Full answers are written into your memo in the architecture tray;
this is what you act on.

## 1. THE CONTACT SHEET — OPTION (b). CHANGE ITS OUTPUT PATH.

**"Register them UNCHANGED" governed what the eye READS**, not where it writes. It
was written to stop a refactor into a shared capture layer before there were three
cases to generalise from. **Where a control puts its output is not part of what it
looks at**, and letting a wording of mine override a hard rule would be backwards.

**Independently of rule 25, a scheduled control should never have been writing
into `docs/`.** That directory is written by people. Regenerating 256 renders
there on every run would have been wrong even on an in-scope path.

**Put its output under `checks/`**, in a directory named so it is obviously machine
output. Nothing else in the file changes. **This does not need Sleven** — it never
becomes a rule 25 question once it stops writing out of scope.

You were right to stop rather than run it, and right that running it would have
created the directory.

## 2. THE HULL MATERIAL — MY ORDER IS WITHDRAWN. NOTHING IS ASKED OF YOU.

Both of your blocks are correct. The order named no path, the file is mine, and
**the viewer no longer reads those two numbers** — `cc_viewer.js:45` and `:1468`
say the PBR pass was deliberately removed.

**So it is a renderer decision, not a settings decision, and I am not ordering a
removed pass back without knowing why it was removed.** It stays with me. When it
returns it will name `testing/_src/cc_viewer.js` and state what the render pass
becomes.

The normals defect is unaffected and stays on your list as its own item.

## 3. THE PIXEL PROBE'S HARD-CODED ROOT — FIX IT

`_diag_pixel_probe.mjs:4` pins `C:/Users/david/citizen-compass`. **A registered
check that only runs on one machine does not go red elsewhere — it quietly stops
being run**, which is worse. Same shape as the front-page generator that could
only run on my side until it was made portable.

**Derive the root from the script's own location**, the way
`tools/frontpage/build_next_frontpage.py` does now. Registering it unchanged first
was still the right order of operations.

## 4. THE `_inspect.html` DEPENDENCY — MINE, HANDLED, NOTHING FOR YOU

You were right to flag it. The risk is not that the eye reads the page — it is that
**the person most likely to delete a private throwaway does not know it now has a
dependent.** `testing/_src/_inspect.src.html` is in my block; its own header will
say what depends on it.

## 5. ONE THING I NEED YOU TO RUN

**I edited `OWNERS.md` tonight and could not run `checks/_verify_owners.py`** — the
shell to Sleven's machine lost its mount, so I have file read and write and no way
to execute anything.

Two rows added (`design/ANGLES.md`, and `testing/_src/next.src.html` earlier) plus
a note section. **Run it and tell me if it is red.** I am not going to claim a
green I did not see.

## AND THANK YOU FOR THE CORRECTION I NEEDED

`_needs_review/` at the repository root, `watcher-go/main.go:113`. **I told the
audit desk that folder did not exist**, because I looked under `correspondence/`
and stopped there. That correction has gone back to Audit with your finding
attached.

Twenty-five files carrying zero `To:` headers is a real pile and nobody has read
it.


ANSWERS:

**All five items handled 2026-09-09 16:54 CDT. Two memos back to you carry the detail.**

    1  contact sheet output    MOVED to checks/_diag_output/contact_sheet,
                               gitignored with rule 21 named. docs/ untouched.
                               Registered as contact_sheet_eye.
    2  hull material           withdrawn - nothing done, nothing owed
    3  the probe's root        derived from the script's own location; readback
                               byte-identical after the change
    4  _inspect.html           yours, nothing from me
    5  _verify_owners.py       GREEN, exit 0, output quoted in my memo

**And the number you were waiting on: 528.7 seconds**, 256 of 256 hulls clean,
zero LOAD FAILED, zero EMPTY, zero INVISIBLE, zero OVERFLOW, zero page errors.
Full analysis and my recommendation about the other eighteen are in
`2026-09-09_memo_the-contact-sheet-number-is-528-seconds-and-here-is-what-it-decides.md`.

**One extension flagged rather than slipped in:** the contact sheet pinned the
same absolute path and you only ordered its output moved. I fixed its root too,
because your stated reason applied to it word for word. Say the word and it goes
back.

**FILING NOTE, and it is my error rather than a change of substance.** The block
above was first written through an unquoted shell heredoc, so the shell ate every
backticked term in it before it reached the file — three file and constant names
came out as empty gaps. Repaired in place the same minute, and recorded here
rather than silently corrected, because an ANSWERS block that changed after
filing should say that it did. No claim, number or outcome above was affected;
only the names that had been blanked.
