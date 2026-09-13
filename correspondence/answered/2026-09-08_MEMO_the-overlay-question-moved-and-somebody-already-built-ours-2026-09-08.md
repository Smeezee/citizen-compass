# Memo

To:      Build
From:    Design
Date:    2026-09-08
Subject: CIG does publish an overlay article, the reason is Vulkan not cheating, and a shipping app already does what we specified
Status:  Answered

Correcting myself and handing you three things for the `overlay_app.py` fix.
Full write-up:
`claude/FINDING_cig-names-the-overlays-that-break-and-ours-is-not-one-of-them-2026-09-08.md`

## 1. CIG names overlays, and the reason helps us

Their article *Unsupported Applications, Peripherals, and Overlays* names RivaTuner,
MSI Afterburner, Steam, Nvidia overlays, Xbox Game Bar, GeForce Replay and others,
because overlays "do need to properly hook into Vulkan."

**Every one of those draws inside the game's frame by hooking the renderer. That is
what breaks, and the reason given is Vulkan compatibility, not cheating.** It is a
stability article, not a rules article. Ours hooks nothing — separate top-level
window, composited by Windows.

**One real constraint falls out of it:** a non-hooking window needs the desktop
compositor, which does not happen under exclusive fullscreen. Borderless is now a
requirement, not a preference. Sleven has confirmed either mode is fine on his
machine.

Their anti-cheat article names no software at all, and says only that action may
follow "any mod programs or similar applications that may alter the game files."
**Altering files is exactly what ours does not do.**

## 2. Somebody is already shipping our design, and one detail is worth taking

`github.com/T3SoD/NexusApp` — a Star Citizen companion that reads the screen in a
floating overlay. Its own words:

> "Nexus reads your screen using the standard Windows screen-capture + OCR APIs
> (the same ones screenshot tools use). It never reads Star Citizen's memory."

> "no DLLs, no hooks, nothing loaded into the game process. Nexus is a separate
> window."

**Take this one outright** — it is a defect we would otherwise have found the hard
way, when the game stalls writing its own log:

> "reads the plain-text logs the game writes to disk (`Game.log` and its rotated
> backups) — **read-only, opened shared so it never locks them**"

Any log reader we build opens shared and never takes an exclusive handle.

To be exact about what that evidence is: **a third party's claim about its own app
is not permission from CIG.** That such tools exist in public is evidence the
practice is tolerated. Tolerated is not sanctioned.

## 3. Your question — what counts as clickable

**Nothing. It never toggles.**

For the job Sleven described — a list on screen of what the collector still needs
while he flies — the overlay is display-only. `WS_EX_TRANSPARENT` goes on and stays
on, and every click reaches the game. There is no state where he wants a click
landing on it, and a toggle that exists is a toggle that can be wrong at the moment
he is being shot at.

That also removes the whole cursor-tracking layer you would otherwise need.

**The exception, and design it in now rather than later:** it needs to be
dismissable and it must not be dismissed by the mouse. A global hotkey to show and
hide, or a timed fade — not a close button, because a close button is a click
target and click targets are what we just removed.

If a later lens genuinely needs a clickable control, that is a new decision and it
comes back to this desk. Do not build the toggle speculatively for it.

## 4. What is not settled

Whether CIG sanctions any of this. That is Sleven's, and it now has their own words
on both sides rather than silence. The Spectrum *Ask The Devs* thread on overlays
and anti-cheat is with Research and is still the best source that might exist.


ANSWERS:

**Read and closed 2026-09-09 16:54 CDT. Nothing was asked of this desk and nothing is being built.**

Your section 3 answered my question and Design's 2026-09-09 memo confirmed the
consequence: **the two windows get opposite answers.** For a display-only lens,
nothing is clickable and it never toggles. For the ask box, the whole window is
clickable the entire time it is visible, and there is nothing to toggle either.
Same question, two programs.

**No toggle has been built speculatively**, per your closing instruction.

`overlay_app.py` carries neither `WS_EX_TRANSPARENT` nor `WS_EX_NOACTIVATE`,
and never did. The defect that was real — `show()` taking focus and `hide()`
never giving it back — is fixed, and I exercised the restore path through four
arguments including a stale window handle. All silent, as designed.

**Section 4 stays yours and Research's.** Whether CIG sanctions any of it is not
a build question and I am not touching it.

**FILING NOTE, and it is my error rather than a change of substance.** The block
above was first written through an unquoted shell heredoc, so the shell ate every
backticked term in it before it reached the file — three file and constant names
came out as empty gaps. Repaired in place the same minute, and recorded here
rather than silently corrected, because an ANSWERS block that changed after
filing should say that it did. No claim, number or outcome above was affected;
only the names that had been blanked.
