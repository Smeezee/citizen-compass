# WORK ORDER — WO-UI-01 — the collector as a program

    id        WO-UI-01  (CONSOLIDATED, rev 2)
    from      C1, 2026-08-07
    for       Claude Code
    replaces  every earlier launcher spec sent in chat, and Addenda 1 and 2.
              Those are SUPERSEDED. Build to this file and nothing else.
    ruled by  Sleven, 2026-08-07

**Code was right to stop. The earlier spec and its addenda contradicted each
other on three points because the base document was never revised after Sleven
changed the shape. That is C1's error — two writers on one fact. This file is
the single writer. If anything conflicts with it, this wins.**

---

## THE TEST THIS HAS TO PASS

**A person who has never opened a terminal downloads a zip, unzips it,
double-clicks one thing, plays Star Citizen, and presses one button.**

Sleven cannot be in the room with these people. **The program has to explain
itself.**

---

## 1. RESOLVED CONFLICTS — the three points, settled

| | SUPERSEDED | **BUILD THIS** |
|---|---|---|
| Version | radio buttons, choose before starting | **auto-detect LIVE/PTU/EPTU. Manual override in settings only, as a fallback.** |
| Controls | START / STOP buttons | **no start/stop. It follows the game.** Pause lives in settings. |
| Toolkit | raw Win32, single binary, no deps | **bundled WebView UI. Size is not a constraint.** |

**Drop the two acceptance tests written against START and the version selector.
They test things that no longer exist.** Replacements are in §10.

---

## 2. THE INTERFACE — the whole of it

```
        Citizen Collector

    ●  Waiting for Star Citizen…

        [  Send my data back  ]

    Nothing leaves your computer until
    you press that button.

    what this collects  ·  settings
```

While the game runs:

```
    ●  Collecting  —  Star Citizen 4.10 PTU
       47 pictures saved
```

Three states, one button, one reassurance line. **That reassurance line is not
decoration** — people are right to be careful about running something a friend
sent them.

`what this collects` — plain English: screenshots of your own game window, plus
the version and location the game itself writes to its own log. Nothing outside
the game. Nothing sent anywhere.

`settings` — install override, pause, capture folder. **Nobody needs to open it.**

---

## 3. HOW IT IS BUILT

**A WebView-hosted UI driven by the existing Go engine.**

**Bundle whatever the UI needs.** Size is explicitly not a constraint — the
audience downloaded 100 GB to play the game. **If bundling the WebView2 runtime
removes the runtime-missing failure mode, bundle it.** Optimise for working on a
stranger's machine, not for file size.

**KEEP THE GO CAPTURE ENGINE.** Not for size — because it is the most thoroughly
tested component in the project, 34 checks and 13 mutations, and it is now proven
against a live game. **The UI drives it. The UI never reimplements it.**

**One executable, `collector-master.exe`.** Not a separate launcher. A second exe
would drift from the engine exactly as the device panel drifted into three copies.

---

## 4. THE TERMINAL RULE — non-negotiable

**NOBODY EVER TYPES A COMMAND TO USE THIS. Not a crew member, not Sleven.**

**4.1 NO ARGUMENTS = THE WINDOW OPENS.** Double-clicking the exe with no
arguments opens the UI. Not hotkey mode, not usage text, not a console.

Do not rely on the desktop shortcut carrying a flag. Shortcuts get deleted,
moved and copied. **The default behaviour of the program is the program.**

Flags remain for automation. They are never required and never documented as the
way to do anything.

**4.2 NEVER A CONSOLE WINDOW.** Not on launch, not on error, not for an instant.

**4.3 EVERY SETTING IS CHANGEABLE IN THE WINDOW.** A settings file may exist as
storage. If a setting can only be changed by editing it or passing a flag, the
job is not done.

**4.4 GENERATING A CREW COPY IS A BUTTON.** Not a command.

---

## 5. THE `--selftest` OUTPUT PROBLEM — Code raised it, here is the ruling

**Code is right: `-H=windowsgui` means no stdout, so `--selftest` would print to
nowhere — including the packager's own verification step.**

**Do all three:**

1. **Attach to the parent console when one exists.** `AttachConsole(ATTACH_PARENT_PROCESS)`.
   Run from a shell, output appears in that shell. Double-clicked, no console is
   created.
2. **Always write results to a file** next to the exe, regardless. That file is
   what automated checks read and what the UI displays.
3. **Always return a meaningful exit code.** The packager asserts on the code,
   not on parsed text.

**The packager's verification reads the exit code and the results file.** Never
stdout — stdout is a convenience for humans, never a contract.

---

## 6. IT FINDS THE GAME ITSELF

`FindGameLog` already derives the install from the running window's process image
path and falls back to scanning `LIVE`, `PTU`, `EPTU`, `TECH-PREVIEW`. **That
logic is correct and stays.** What changes:

- detection runs **continuously**, not once at startup
- the detected install is **named in the status line**, so a person can see it
  found the right one
- a **manual override** lives in settings as a fallback, never as a first step

Two installs running at once is not worth designing for. Pick the one running;
if somehow both, pick the focused window **and say which you picked**.

---

## 7. IT STARTS AND STOPS WITH THE GAME

Game opens, it collects. Game closes, it stops. **Nothing to remember.**

A **pause** control lives in settings. Sleven's position is it is not needed; it
is included because it costs nothing, and a recording tool that cannot be paused
is one people are right to distrust.

---

## 8. ONE BUTTON, AND THE PACKAGER

**`Send my data back`** bundles the captures into one file, names it so the
sender and patch are identifiable, and **opens the folder with it selected.**
It must say what it made and where, in plain words.

**`Make a copy to send someone`** — master build only. Produces one zip
containing the crew build and a five-line readme.

- **the crew copy must NOT contain the packager.** One master, many leaves. A
  crew copy that can make further copies makes every package untraceable.
- **stamp the package id into the crew build.** The sidecar already carries a
  `collector` block with name/version/variant — extend it.
- **VERIFY BY USING IT:** generate a package, unzip to a temp folder, run the
  extracted exe's selftest, assert exit code 0 and read its results file.
- **NEGATIVE CONTROL: assert the extracted crew copy REFUSES to package.** If it
  accepts, the master/crew split is broken and the model is void.

The readme is five lines: unzip, double-click, play, press Send my data back,
send me the file. Plus one line: Windows will warn about the publisher, that is
expected, the program is not signed yet.

---

## 9. THE RULE THAT OUTRANKS EVERYTHING ELSE

**THE STATUS MUST BE DERIVED FROM REALITY, NEVER FROM WHAT THE UI THINKS IT DID.**

Read the actual process state. Read the actual log path. Count the actual files
on disk. **Never track it in a variable and trust the variable.**

This project has been bitten four times by components that looked healthy
because they were saying nothing:

    a backup reporting exit 0 having copied nothing
    an auto log that only writes when it captures
    a hotkey that was never registered
    a watcher whose fetches were served from cache

**A window that says COLLECTING while nothing collects would be the fifth, and
the worst — the person reading it cannot check and has nobody to ask.**

### And when something is wrong, say it in words

    "I can't find Star Citizen. Is it installed somewhere unusual?"
    "The captures folder is full — 2 GB left on this drive."
    "I found Star Citizen but it isn't writing a log I can read."

**No error codes, no paths, no stack traces in the window.** Those go in the log.

---

## 10. TESTS. Each must be able to fail.

Replacing the two dropped tests:

- **Auto-detect:** point at a PTU install, assert the displayed name AND the
  watched path both contain PTU. Repeat for LIVE. **A detector that does not
  change the path is decoration.**
- **Follows the game:** start the program with the game closed, launch the game,
  assert it transitions to collecting **without anyone touching anything.**
  Close the game, assert it stops.

Retained:

- Kill the process externally while the window says COLLECTING — must say
  stopped within seconds. **NEGATIVE CONTROL:** alive means collecting.
- Capture count comes from counting files on disk. **Delete one behind the UI's
  back and assert the number goes down.**
- `Send my data back` produces one archive containing exactly the files on disk.
  **NEGATIVE CONTROL:** an empty folder gives "nothing to send yet", not an
  empty zip.
- Launch with no arguments and assert the window opens and **no console is
  created.** NEGATIVE CONTROL: `--selftest` from a shell still prints.

**If any test passes on the first run without having been seen to fail, break it
deliberately, confirm it fails, and put it back.**

---

## 11. DESKTOP SHORTCUT

Created as part of this job. Named **Citizen Collector**, pointing at the exe,
working directory set to the collector folder, with an icon. **Launch it once and
confirm the window appears before reporting done.**

---

## 12. NOT IN THIS JOB

No OCR. No database routing. **Signing is deferred** — Sleven distributes to
people he knows first and they will click through the Windows warning. Do not
build for signing and do not wait on it.

**Ship the thing a person can use.**
