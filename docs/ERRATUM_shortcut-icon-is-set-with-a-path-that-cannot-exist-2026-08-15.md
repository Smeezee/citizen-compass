# ERRATUM — the shortcut icon is set to a filename that cannot exist, and the one call that could have said so is the one call whose result is thrown away

    from    C1, 2026-08-15
    for     Code
    status  DEFECT, located in source. Observed twice on Sleven's friend's
              machine, and NOT fixed by reinstalling from GitHub.
    file    citizen-collector/shortcut.go

---

## 0. The symptom, and what it is not

Sleven reinstalled 0.3.1 from the GitHub release onto his friend's machine. The
program runs, reports `Up to date - version 0.3.1`, and puts a shortcut on the
Desktop. **The shortcut has a blank white page icon.**

**The download is not the problem, and this was checked rather than assumed.**
The exe inside `citizen-collector-0.3.1.zip`:

```
sha256   f31890b1f70759f0...      <- byte-identical to the sha256 in the feed
size     12,730,368
.rsrc    present
collector.ico payload bytes found INSIDE the exe:  yes
```

**The icon is embedded in the shipped binary.** Explorer draws it correctly on
the exe itself — the previous install showed the green ring. **Only the shortcut
is blank.**

## 1. The defect

`shortcut.go:251`:

```go
icon := exe + ",0"
```

passed to `CreateShortcut`, which does:

```go
comCall(psl, slotShellSetIcon, uintptr(unsafe.Pointer(p)), 0)
```

That slot is `IShellLinkW::SetIconLocation`, whose signature is:

```
HRESULT SetIconLocation(LPCWSTR pszIconPath, int iIcon);
```

**Two separate parameters: a path, and an index integer.** The call already
passes `0` correctly as the index.

**But the path it passes is `C:\...\collector.exe,0`.**

`path,index` is the syntax the Windows Properties dialog accepts as a single
typed string. **It is not what the COM API takes.** So the shell is asked to load
an icon from a file literally named `collector.exe,0`, which does not exist and
never will. No icon is found, and the shell falls back to the generic document
glyph — the white page.

**The fix is one line:**

```go
icon := exe
```

The index is already being passed as its own argument.

## 2. Why nothing caught it, which is the more important half

**The icon setter is the only one whose HRESULT is discarded.** Every other
property goes through `set()`, which checks the result and returns an error:

```go
if err := set(slotShellSetPath, target); err != nil { return err }
if err := set(slotShellSetWorkDir, workDir); err != nil { return err }
if err := set(slotShellSetDesc, desc); err != nil { return err }

if icon != "" {
    if p, err := syscall.UTF16PtrFromString(icon); err == nil {
        comCall(psl, slotShellSetIcon, uintptr(unsafe.Pointer(p)), 0)   // <- result dropped
    }
}
```

**And a returned result would not have saved it anyway.** `SetIconLocation`
stores the string; it does not resolve it. It would have returned `S_OK` for a
path pointing at nothing. **The failure is invisible until a human looks at a
desktop** — which is exactly what happened, twice, before anybody noticed.

`CreateShortcut` ends with a real verification and a comment about six silent
successes on this project:

```go
// VERIFY IT IS ACTUALLY THERE.
if _, err := os.Stat(lnkPath); err != nil { ... }
```

**That check proves the .lnk exists. It says nothing about whether the .lnk
works.** The shortcut was verified into existence and never verified into
correctness, and `runShortcutSelftest` asserts the shortcut's NAME while the icon
sat broken behind it. **Rule 12: a check that cannot fail is not a check**, and
this is a check that passes on a shortcut nobody can recognise.

## 3. What to build

- **Fix the path.** One line.
- **Check the HRESULT**, like every sibling call. It would not have caught this
  one, and it should still be checked — the asymmetry is itself the smell.
- **Read the icon location back off the saved `.lnk`** and assert it names a file
  that exists on disk. **That is the check that would have caught this**, and it
  is the only one that would have.
- **Negative control, and it is the load-bearing one:** point the icon at a path
  that does not exist and confirm the check FAILS. A shortcut verifier that has
  never been observed rejecting anything is the thing it exists to catch.
- **Rewrite existing shortcuts.** Every install already out there has a broken
  `.lnk` on its Desktop and in its Start Menu. A machine that has already
  answered "yes" must have its shortcut corrected on next run — **without asking
  again**, since it already answered.

## 4. Related, observed on the same screen — do not lose these

1. **The install went into `C:\Users\Tardis\Downloads\citizen-collector-0.3.1\`.**
   Downloads is one of the folders `prompt-code-never-run-from-the-desktop-2026-08-15.md`
   names. That order stands and this is a second live instance of it.
2. **`alt+f3 - NOT registered. Another collector may still be running.`** still
   showing after a clean reinstall. An older process is almost certainly still
   alive from the Desktop install. **A reinstall into a new folder does not stop
   a running process**, and the program should say that in words a person can act
   on rather than "may still be running".

## 5. Acceptance

1. A fresh install's Desktop and Start Menu shortcuts both show the collector's
   own icon.
2. The verifier reads the icon location off the saved `.lnk` and confirms the
   file exists.
3. **The verifier is observed rejecting a deliberately bad icon path.**
4. An install that already answered "yes" gets its broken shortcut corrected on
   next run, silently, with no second prompt.
5. `-selftest` passes including 2 and 3.
