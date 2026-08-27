# Update: item 2 done - the collector will not make its home on a Desktop

`install_location.go` + `install_location_selftest.go`.

## What it does

On start, **before the log is opened** - the log lives beside the exe, so opening
it first would put one more file on the Desktop while deciding whether to put
files on the Desktop - it compares the exe's folder against the known folders:
**Desktop, shared Desktop, Downloads, Documents, user folder**.

All resolved with `SHGetKnownFolderPath`, never built from `%USERPROFILE%`.
OneDrive redirects Desktop on a large share of consumer machines, and a
hardcoded compare would pass on exactly the machines that need this most.

If the exe is sitting **directly in** one of them it does not start. It shows a
message that **names the files by name**, says `captures/` grows by a few MB per
screenshot, and offers one click that moves the program and every `collector-*`
file and `captures/` into `<that folder>\Citizen Collector\`, repoints the
shortcut, and starts from the new location.

**Directly in, not underneath** - `Desktop\Citizen Collector\` is a good home and
is what the fix creates. Refusing that would refuse the solution along with the
problem, and produce a loop with a dialog in it.

## The move order is the safety property

A move of many files cannot be atomic. It can be **recoverable**, and the order
decides what an interrupt leaves:

- **exe first** -> new folder has a program and none of its data. Next run looks
  like a fresh install: consent answer gone, install id gone, person asked to
  agree to everything again while their data sits on the Desktop.
- **data first** -> exe still in the old place with its data gone. Its next
  launch lands on the same known folder, and finishes the move into the same
  destination.

So data first, exe last, destination deterministic - **the guard firing a second
time IS the recovery**. Nothing is ever deleted; a name that already exists at
the destination means it already moved, so the source is left and reported.

## Proven, both directions

    [ok] the real Desktop IS refused
    [ok] Downloads IS refused / the user folder IS refused
    [ok] a folder UNDER the Desktop is allowed
    [ok] NEGATIVE CONTROL - an ordinary folder is allowed
    [ok] NEGATIVE CONTROL - this collector's own folder is allowed
    [ok] trailing slash / capitalisation do not defeat the compare
    [ok] NEGATIVE CONTROL - an empty path matches nothing
    [ok] the file list finds every data file and the captures folder
    [ok] NEGATIVE CONTROL - unrelated files are not swept up
    [ok] the captures folder came with its contents
    [ok] NEGATIVE CONTROL - the unrelated file was left where it was
    [ok] resuming an interrupted move leaves ONE install
    [ok] resuming does not overwrite what already moved

**Reported honestly rather than claimed:** this machine's Desktop is **not**
OneDrive-redirected, so that case was **NOT exercised here**. The selftest says
so in those words rather than printing a pass for it. The guard resolves the
folder rather than building a path, so redirection is handled by construction -
but construction is not observation.

One of my own assertions was wrong and the run caught it: I asserted
`len(found) == 4` against a fixture with five items. Now asserted by membership,
because a count would also break every time a new `collector-*` file is added and
teach people to adjust the number instead of looking at what moved.

## Also, from the erratum's "do not lose these"

The hotkey warning said *"Another collector may still be running"* - true, and
nothing a person can act on. It now says a new install does **not** stop the old
copy, and to close the other window or end `collector.exe` in Task Manager. That
message was still showing on the friend's machine after a clean reinstall, which
is exactly the situation it failed to explain.

## §5 - how to tell whether a stale machine can update itself

**One line for a non-technical person:** open the collector and look at the
window - if there is a line saying which version it is, it can update itself;
if there is no version anywhere in the window, that copy is too old and the
exe has to be replaced by hand from the GitHub release.

`selftest PASS`. Not committed yet - the four items ship as one build.
