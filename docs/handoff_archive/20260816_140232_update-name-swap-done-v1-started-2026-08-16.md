# Update: the name order is DONE and committed. V1 report follows.

`8245503`. `selftest PASS - 555 checks, 0 failing.` Not pushed, not released.

## Measured on his real dataset

    raw handle slots : 44 -> 0
    NPC rows kept    : 85 -> 85   (the old export destroyed 80 of them)
    distinct tags    : 15
    privacy note     : "...74 names were replaced with tags in this file."

Tags match the ones already in the bucket, so the data still joins to what was
already sent. Dataset backed up before I touched it.

## Three defects found underneath the reported one

1. **`safeActor` has never had a caller.** Four selftest checks certify it,
   including a negative control that passes. Unit-tested and unreachable.
2. **The export destroyed 80 of 85 ambient NPC names**, because its predicate
   did not know `PU_Human-...`. Safe, and it deleted the data §4 says to keep.
3. **`scrubIDs` ate its own tags.** `player:2860302f` -> `player:<id>f`, because
   a tag is eight hex characters and that one held a 7-digit run. Silent, and
   only for people whose tag happened to contain digits - so joins broke for
   some and not others. Caught by the idempotence check.

## VERSION ONE - answers to the three questions asked

### Installer technology: WiX v6 (MSI), and I would argue for it

**Chosen:** WiX Toolset v6, building a per-user MSI.

- **No admin.** A per-user MSI installs to `%LOCALAPPDATA%\Programs` and writes
  `HKCU\...\Uninstall`, giving a real Add/Remove Programs entry without
  elevation - which is a hard requirement here.
- **The uninstaller genuinely removes things.** MSI tracks what it installed, so
  the startup entry, the shortcut and the Start menu item come out with it.
  "Delete the folder" leaves a startup entry pointing at nothing, which is the
  defect §1 names.
- **Reproducible from this repo.** The WiX source is XML in the tree; the build
  is one command in `build.ps1`.
- **Signable later** without changing anything else, when Sleven wants to spend
  the few hundred a year.
- **Upgrade codes** are exactly the mechanism §1 needs for adopting an existing
  install: same UpgradeCode, higher version, and the migration runs as a custom
  action.

**Rejected:** Inno Setup and NSIS - both excellent and both produce an
installer EXE, which is the worst possible shape for the antivirus problem below.
Squirrel/ClickOnce - .NET runtime dependency, ruled out by "no runtime the user
must fetch". A self-extracting zip - no uninstall entry, so §1 fails at the first
requirement.

### Is an installer treated WORSE by antivirus than a bare exe?

**Yes, and materially - if it is an installer EXE. No, if it is an MSI.**

An unsigned installer EXE is the single most-flagged shape in consumer
antivirus: it is what droppers look like, NSIS and Inno stubs are what droppers
actually use, and SmartScreen has no reputation for a brand-new one. An MSI is
handled by Windows Installer itself, is not a self-extracting stub, and does not
carry the packer signature heuristics fire on.

**It does not make the problem go away.** Unsigned is unsigned, SmartScreen will
still warn, and `download.html` already states exactly what the person will see.
MSI is the least-bad unsigned shape, not a solution. **The actual solution is a
signing certificate**, and it is the one thing here that money fixes outright.

### How big is a kept diary, measured

Against **241 real sessions** in his own `logbackups`:

    total raw            206.7 MB
    mean per session      0.86 MB      median 0.50 MB
    largest session       8.66 MB
    gzip ratio            6.5%  (measured on the 12 largest, worst case)

    one session   0.86 MB raw  ->  0.06 MB gzipped
    241 sessions  206.7 MB     ->  13.5 MB gzipped
    a year at 3 sessions/week  ->  134 MB raw, 9 MB gzipped

**Keeping the whole diary is not expensive - it is rounding error.** 241 sessions
compressed is 13.5 MB against 1.8 GB of screenshots on the same machine: **0.7%**.
Logs compress to 6.5% because they are enormously repetitive. §3 is comfortably
affordable, and storing it compressed is the obvious choice.

## The one thing in the order I think is wrong

**§6 removes interval capture entirely; §9 lists "interval" as a setting that
must live in the window.** Those cannot both hold - a setting for a removed
feature is a control that does nothing, which is its own defect class and one
this project has been finding all week.

I will treat §6 as authoritative and drop the interval control. Say if that is
backwards.

## What is NOT built yet, stated plainly

Items 1, 2, 3, 5, 6, 7, 8 of V1 are **not started**. Done so far: item 4 (names),
which the order said to do first, plus the migration and the privacy statement.

The remaining work is a fortnight of building, not an afternoon - an MSI with
migration and a custom action, removing three capture paths, an activity list,
and update completion proven across two one-way jumps that have never been
tested. I would rather say that than deliver seven half-finished features.
