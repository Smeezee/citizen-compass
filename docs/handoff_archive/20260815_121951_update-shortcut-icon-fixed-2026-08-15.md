# Update: item 1 done - the shortcut icon, and the check that would have caught it

## The one line

`shortcut.go`: `icon := exe + ",0"` -> `icon := exe`.

`path,index` is what the Windows Properties **dialog** accepts as one typed
string. `SetIconLocation` takes them as two arguments and the index `0` was
already being passed correctly, so the shell was asked for an icon inside a file
literally named `collector.exe,0`. It fell back to the generic document glyph.

## The other three, which matter more

- **The discarded HRESULT is checked**, like every sibling setter. It would NOT
  have caught this - `SetIconLocation` stores the string without resolving it and
  returns S_OK for a path pointing at nothing - but a result nobody reads cannot
  report anything, and the asymmetry was the smell.
- **The icon is read back off the SAVED .lnk** (`ReadShortcutIconLocation` via
  `IPersistFile::Load` + `IShellLinkW::GetIconLocation`) and
  `VerifyShortcutIcon` confirms it names a file on disk. `CreateShortcut` now
  fails if it does not. **This is the only check that would have caught it.**
- **Existing installs are repaired silently.** Every install in the world has a
  blank page on its Desktop. Those people already said yes; asking again would
  make our mistake their decision. `RepairShortcuts` runs when the recorded
  answer is `yes`, checks each shortcut, rewrites only broken ones, and is silent
  when there is nothing to do.

## Proven, both directions

    [ok] the icon location can be read back off the saved .lnk
    [ok] the saved icon is the exe itself, with no index glued on
    [ok] the icon index is passed as an index, not inside the path
    [ok] the saved icon location exists on disk
    [ok] NEGATIVE CONTROL - an icon path with ,0 glued on IS rejected
    [ok] and the rejection names the real cause
    [ok] NEGATIVE CONTROL - an icon file that does not exist IS rejected
    [ok] NEGATIVE CONTROL - a correct shortcut is still accepted
    [ok] an answer of no is not treated as a request to repair
    [ok] an answer of yes is recognised, so repairs can happen silently

The rejection message names the actual cause rather than "file not found", which
would have sent the next person hunting for a missing icon file instead of at the
string that was written.

Two of those controls are load-bearing in opposite directions: the verifier must
reject the broken shortcut, **and** must still accept a correct one - a checker
that failed everything would satisfy the first and break every shortcut made.

**The selftest was reproducing the defect**: it passed `exe+",0"` itself, so it
had been asserting success on the very thing it should have caught.

To do that, writing a shortcut and verifying it are now separate
(`createShortcutNoVerify` + `VerifyShortcutIcon`), because a writer that refuses
to write a bad shortcut leaves the verifier untestable.

`selftest PASS`. Not committed yet - the four items ship as one build.

## Bucket, checked before starting (dry run, nothing emptied)

2 objects, 19.7 MB, both from install `b99c1e3b-...` at **16:40:50 and 16:42:01
UTC today**, both stamped version **0.3.1**. **Sleven's friend's send landed.**
The second is 14.6 KB, which is what a second SEND press looks like after
`clear_after_send` emptied the first.

## Working tree question, answered

Only `publish-destination.ps1` was actually dirty - `README.md` is clean and
`wrangler.toml` was committed in `6285f67`. Committed as `f4a3f08`.
