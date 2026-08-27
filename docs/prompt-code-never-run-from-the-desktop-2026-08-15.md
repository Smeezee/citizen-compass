# PROMPT FOR CODE — the collector is running FROM a Desktop, so its whole working folder is somebody's Desktop. Refuse to do that.

    from    C1, 2026-08-15
    for     Code
    status  GO-AHEAD, queued behind the feed publish and 0.3.1.
    basis   Photographs of Sleven's friend's Desktop, 2026-08-15. This is
              observed, not theorised.

---

## 0. What is on that Desktop

Sleven went to his friend's machine to check whether the update was even
reachable, and found this — read off the photos, item by item:

```
collector            <- the EXE ITSELF, green ring icon, sitting on the Desktop
collector-s...       <- collector-settings.txt        white page
collector-a...       <- collector-auto.log            white page
collector-i...       <- collector-install-id.txt      white page
collector-d...       <- white page
collector-C...       <- white page
captures             <- A FOLDER. Screenshots. On his Desktop.
```

His words:

> "every time I click it, it puts two files on there... it kicks open two to
> three folders that are all identical, but they're just white pages on the
> desk... Why the fuck is that on there?"

**Nothing is malfunctioning.** The program writes its files next to itself, which
is a deliberate and good property — `shortcut.go` argues for it in its own
header, "deleting the folder removes everything." **The exe is on the Desktop, so
next-to-itself IS the Desktop.** Every launch writes more, exactly as designed,
into the one folder a person looks at all day.

**And it is going to get much worse than untidy.** `captures/` is on there. That
folder grows by roughly 3 MB a frame during a session. His friend's Desktop is
the storage location for a screenshot archive.

## 1. How it got there, and why the design invited it

From `shortcut.go`'s own header, Sleven on 2026-08-08:

> "I did drag the application that launched it, citizen collector. It says
> collector on it"

**He dragged the exe out of the unzipped folder onto the Desktop, because there
was no shortcut and the folder was unfindable.** That was the correct instinct
and the program had given him no better option. The shortcut feature was built
in response — but it was built for a machine where the exe stayed in its folder,
and it does nothing about a machine where the exe has already been moved.

**So the fix that shipped solved the next person's problem and not this one's.**

## 2. What to build: the program refuses to run from a folder that is not its own

**On start, before writing anything at all**, compare the executable's directory
against the known folders — Desktop first, then Downloads, Documents, and the
user profile root. Resolve them with `SHGetKnownFolderPath`, the same call
`shortcut.go` already uses and for the same reason: OneDrive redirects Desktop on
a large share of consumer machines, and a hardcoded `%USERPROFILE%\Desktop`
compare would pass on exactly the machines that need this most.

**If the exe is sitting directly in one of those folders, do not start.** Say, in
a message box, in plain words:

- what it is about to spread across their Desktop, **naming the files**
- that it needs its own folder
- **and then offer to fix it in one click.**

**The one click is the requirement, not a nicety.** "Please move this file into a
new folder and run it again" is a hand-off to a person who did not build this,
and Sleven's friend is not going to do it. Create the folder, move the exe and
every `collector-*` file and `captures/` into it, refresh or recreate the
shortcut so it points at the new location, and start normally.

**A move that cannot be completed leaves everything exactly where it was and says
so.** A half-moved install is worse than an untidy Desktop: the settings go one
way, the log goes the other, and the next run looks like a fresh install with the
person's consent answer missing.

## 3. The shortcut has to survive this, and it is the reason the icon vanished

Sleven reports the icon he clicks no longer looks like the app. A `.lnk` pointing
at an exe that has been renamed or moved goes blank, and **the updater's own
Windows rename-the-running-exe trick moves the target every single time it
installs a version.** On this machine that rename happens on the Desktop.

- **After any move or self-update, rewrite the shortcut** so its target is still
  the exe that exists.
- **Verify the shortcut resolves** rather than assuming the write worked. This
  project has logged the silent-success shape six times by `shortcut.go`'s own
  count.

## 4. Do not solve this by moving the data somewhere invisible

The obvious alternative is `%LOCALAPPDATA%`. **Do not.** The program's promise is
that everything it holds sits in one folder you can open, inspect and delete, and
that promise is load-bearing for a tool that reads a game log and takes
screenshots. **Hiding the data would trade a visible mess for an invisible one,
and the invisible one is worse for consent.**

The problem is not where the files go. It is that the exe was allowed to sit
somewhere that made the answer "your Desktop."

## 5. His friend's copy is an old build, and I cannot tell which

Nothing here reveals the version on that machine, and **do not guess it from the
file list.** Whatever it is, it predates the shortcut work, and it may predate
`update.go` entirely — in which case it cannot self-update and needs the exe
replaced by hand. **Report what a person should check on a stale machine to find
out which of those two situations they are in**, in one line a non-technical
person can follow.

## 6. Rule 12 — the checks that matter

- **Point the check at a directory that IS a known folder and confirm it
  refuses.** A guard that has only ever been observed allowing things is not a
  guard.
- **A redirected Desktop** — the OneDrive case — must be detected too. If that
  cannot be exercised, say so plainly rather than reporting a pass that only
  covers the easy machine.
- **The move is atomic in effect:** kill it midway and the install must still be
  exactly one place, not two.
- **The negative control:** a normal install in its own folder starts silently,
  with no dialog and no move. Without that check, "refuses to run on the Desktop"
  would also pass on a build that refuses to run anywhere.

## 7. What NOT to do

- **Do not delete anything from anybody's Desktop.** Move only, into the new
  folder. Rule 5 — and this is somebody else's computer, which makes it worse
  than a repo mistake.
- **Do not silently relocate on a machine that is working.** Sleven's own install
  is in its proper folder and must see none of this.
- **Do not `git add -A`.**

## 8. Acceptance

1. An exe placed directly on a Desktop refuses to start and explains why.
2. One click moves it into its own folder, brings every `collector-*` file and
   `captures/` with it, and starts.
3. An interrupted move leaves one install, not two.
4. The shortcut points at the exe that exists, after a move and after a
   self-update.
5. A normal install in its own folder is untouched and shows no dialog.
6. The message names the files by name. A person who did not build this can read
   it and know what happened.
