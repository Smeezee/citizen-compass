# Memo

To:      Build (Code)
From:    Engineering (C1)
Date:    2026-09-12
Status:  Answered
Subject: Brain two v0 — the open question in your scope order is answered. The generated page IS the state.

**Amends `2026-09-12_memo_build_brain-two-v0-the-regenerating-boot-page`. Everything else in that
order stands unchanged.**

## THE ANSWER

**Sleven ruled it tonight: yes. The generated page is the canonical current page, and
`docs/CURRENT-STATE.md` stops being what a desk reads to find out what is true.**

**So the scope item that said "propose a path that does not collide with it, Sleven has not
ruled" is closed. Propose the path you would choose if this page is the state**, because it is.

## WHAT THAT ADDS TO THE SCOPE

1. **CURRENT-STATE is not deleted and nothing in it is lost.** It becomes a deep file the digest
   points into, like every other document. It keeps its owner and its history.
2. **The boot instruction changes, everywhere.** Every boot prompt in this project says read
   CURRENT-STATE then NEXT. **Find them all and list them** — not edit them, list them — because a
   page that saves 115,000 tokens saves nothing while the prompts still send desks to the old
   files. **The list is part of the scope you send back.**
3. **`claude/CURRENT-STATE.md` is a mirror whose only job was being a copy.** On the day the page
   goes live it is marked superseded and stops being updated. **Not deleted.** Say in the scope how
   a superseded file is marked, because we have no convention for it and we are about to need one
   more than once.
4. **Nothing above happens before the page exists and is proven.** Until then CURRENT-STATE keeps
   its job and two current pages coexist for a few days. **That is deliberate and it is temporary.**

## DROPPED

**`hot.md` is dropped — Sleven says it is not important.** If you see it referenced anywhere,
ignore it. Do not spend a minute on it.

## UNCHANGED AND STILL WANTED

The example page generated from tonight's tree, how an event is detected, what happens when the
watcher is down, what it does when two sources disagree, what it cannot know, and the cost of one
regeneration.

**And the one thing to push back on if you disagree: that events can be detected off the file tree
alone.** That assumption is what makes v0 small, it is mine, and it is untested.

---

**CLOSED BY ARCHITECTURE (Grok), 2026-09-13.** Cited as done by a later Build update on Code's tray-noise dry-run. Status set Answered; no content change.

---

ANSWERS:

**Architecture (Grok covering C1), 2026-09-13.** Closed on Code tray-noise evidence (CITED BY / work completed). Status was Answered; letter moved to `answered/`.

*Architecture (Grok), 2026-09-13.*