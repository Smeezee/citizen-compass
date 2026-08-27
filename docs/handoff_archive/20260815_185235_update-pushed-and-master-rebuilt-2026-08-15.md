# Update: both commits pushed, master binary rebuilt. No release.

## 1. Pushed - and the feed did not move

`5a2690b..8ffe727`. `origin/main` is now `8ffe727`, nothing unpushed.

**Checked before pushing, not after:** neither commit touches `releases/`. The
17 files are collector source, the download page, the build script and
ARCHITECTURE_DECISIONS.md.

Confirmed after, over the network:

    published feed version: 0.3.2
    release tags: collector-v0.3.0, v0.3.1, v0.3.2   (no new tag)

**Nothing reaches Sleven's wife or his friend.** They stay on 0.3.2, which is the
build before tonight's four fixes.

## 2. The master build - the report was right, and worse than described

`collector-master.exe` on disk **was the crew binary**: version 0.3.2, and **no
`-allow-any-window`**, which is the master-only flag. Confirmed by asking the
binary rather than by trusting the filename.

**`collector-master.exe.old` is not a recoverable master build either.** It is a
**crew 0.3.0** - so the updater overwrote his master build at least twice, and no
master binary survived on disk under either name. Nothing was lost that mattered,
because it rebuilds from source, but it is worth knowing the `.old` is not a
backup of what he had.

Rebuilt with `-tags master`. Verified in both directions:

    collector-master.exe   0.3.2   MASTER  (allow-any-window present)
    collector.exe          0.3.2   crew    (allow-any-window absent)

That second line is the negative control - if the tag had leaked into the crew
build, the master-only bypass would be sitting in the binary that goes to other
people.

Both binaries: `-selftest` **PASS**.

Crew rebuilt afterwards too, so the pair comes from the same source state and the
crew is not older than the master - which is what `make-release`'s staleness
guard checks, and it would have refused a release with the crew binary older.

## What Sleven is testing tonight

`collector.exe`, version 0.3.2, built from `8ffe727` at 18:52. It carries the
four fixes:

- the window scraps itself and switches to the browser if the page never answers
- the tray's window is message-only, so the empty black box is gone
- `-send` flag **and** a tray menu item, both through the same consent path
- the collector's own icon in the tray and on the window

**The published 0.3.2 he could download is NOT this binary.** The fixes exist
only in the local build until a release is cut, which has not been done.
