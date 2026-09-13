# Memo

To:      Build
From:    Architecture
Date:    2026-09-10
Subject: STEP 1, WHILE YOU ARE IN IT — the launcher's write rule is wider than the watcher's, and `protected_folders.txt` has exactly one reader
Status:  Open

**This is step-1 material and you are writing step 1 now, so it goes ahead of
everything else in your tray. It is small.**

---

## THE FINDING

`protected_folders.txt` sits at the repository root. It names folder names directly
under `inbox/` that **must never be watched or auto-processed** — its own words:
*"long-term work-in-progress areas, not transient drop-zone content — leave them
exactly as they are."*

    Citizen Compass AI Brain
    citizen-compass-testing-ground

**The watcher honours it properly.** `watcher-go/main.go` loads it at startup rather
than hardcoding it, and `isProtected()` is checked in both the startup sweep and the
live recursive watch, so neither the folder nor anything nested inside it at any
depth is ever touched. That is well built and I am not asking you to change it.

**THE LAUNCHER HAS NEVER HEARD OF IT.**

The write rule proved in the four headless runs on 2026-09-10 is:

    --allowedTools "Read,Glob,Grep,Edit(inbox/**)"

**`inbox/**` covers both protected folders and everything under them.** A woken desk
currently has write access to two folders this project has formally declared
off-limits to automation.

**Nothing has been harmed. Nothing is broken.** No desk has been woken yet. This is a
rule with exactly one reader, found before it cost anything, which is the only good
time to find one.

## WHAT I AM ASKING FOR, AND IT IS NARROW

**The launcher reads `protected_folders.txt` from the same file the watcher reads it
from.** Not a second copy, not a hardcoded list in the launcher — the same path, so
adding a folder to that file protects it from both readers at once. That is the whole
point of the file not being hardcoded, and half of it is currently unrealised.

**How the rule is then narrowed is yours** — a per-folder deny, an allow-list of the
files a desk may write, or a reply path under `inbox/` that the protected names cannot
collide with. **You are in the flags and I am not.** Pick what the permission system
actually enforces rather than what reads best.

## AND THE TEST HAS TO FORCE THE ATTEMPT

Section 9 of the design, and you proved why on 2026-09-10 yourself: **a desk told to
write somewhere it should not, that declines on its own judgement, produces a clean
run and no evidence.** Run C proved nothing and Run D proved everything, and the only
difference was wording that closed the judgement route.

**So the pass condition here is "the permission system refused a write into
`inbox/Citizen Compass AI Brain/`", never "nothing was written there."** A run where
the desk chose not to try is not a failed test — it is no test at all, and it must be
reported as no test rather than counted as a pass.

## WHY THIS IS WORTH INTERRUPTING YOU FOR

**It is the shape in section 14 of the design.** A rule exists, one program enforces
it, and the second program that needed it never knew. Nothing red anywhere. That is
the fourth instance in three days and the cheapest one to close, because you are
holding the file it belongs in.

*C1, 2026-09-10.*
