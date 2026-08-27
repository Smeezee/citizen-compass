# PROMPT FOR CODE — the update feed 404s (so old builds can never self-update), and a Desktop-clutter complaint to investigate

    from    C1, 2026-08-10
    for     Code
    basis   Sleven, looking at his friend's actual running collector window
              (photo of the app) and his own: "my friend's copy does not look
              like that, it doesn't have the stuff there at the top" — plus,
              separately, "when I click the collector icon it launches and
              then creates two [...] folders on the desktop. I'm not happy
              with that."
    scope   citizen-collector/ only. Per the 2026-08-09 ruling, this goes
              through inbox/ — no direct writes from C1.

---

## 1. The friend's window isn't missing a feature — it's an old build, and it can never catch up on its own

Read the friend's screenshot against the actual source before assuming
anything's broken: `ui.go` already has the "Picture key" line Sleven asked
for, and the comment above it is literally quoting this exact complaint from
before —

```go
// THE KEY, ON SCREEN. The panel told a person the log path, the capture
// count and the folder - everything except the one thing they have to DO.
// Sleven, watching it run on a friend's machine: "there need to be a place
// for users to look at what the hotkey [is]".
```

That fix is in the source. The friend's window shows no such row at all — it
goes straight from the update-check line to the buttons. **That means the
friend is running a build from before this line was added**, not a different
feature set. Nothing to fix in `ui.go` for this specific complaint — it's
already fixed. The real problem is #2.

## 2. The real bug: `releases/collector-latest.json` doesn't exist, so the update feed 404s for everyone, always

`update.go` checks:

```go
const updateFeed = "https://raw.githubusercontent.com/Smeezee/citizen-compass/main/releases/collector-latest.json"
```

**Confirmed: this file has never existed in the repo, on any commit, ever.**
`releases/` only holds the citizen-compass HTML snapshots. Every collector,
everywhere — Sleven's own master build included, per his friend's screenshot
showing the same 404 — has been checking a URL that can never resolve. This
is why the fix in §1 (and presumably every other fix since whenever this
feed was supposed to start working) never reaches anyone who isn't handed a
fresh copy directly.

**The fix:** create `releases/collector-latest.json`, publish it (commit +
push, with Sleven's go-ahead same as always), and keep it updated whenever a
new collector build is cut. Check `update.go`'s parsing of the response to
get the exact shape right — version string, download URL, and whatever
fingerprint/hash field it checks the download against (README-FOR-TESTERS.txt
says "it checks the download against a fingerprint published alongside it and
throws it away if they do not match" — find that check and make sure the
published JSON satisfies it, don't guess the shape).

This is a real, live bug affecting every install, not just the friend's —
worth flagging clearly in the report back rather than treating as a minor
housekeeping item.

**Until this is fixed, the only way to get the friend (or any other tester)
onto a current build is to hand them a fresh package directly** — Sleven's
own "Make a copy to give somebody" button on his master build. Say this
plainly in the writeup so it doesn't get lost: self-update is broken for
everyone right now, full stop, regardless of this fix, until a version
actually gets published to that feed.

## 3. Investigate: two folders appear on the Desktop when the collector launches

Sleven doesn't like this and wants it fixed, but I could only confirm ONE
folder-creation path from reading the source, not two:

```go
outDir = flag.String("out", filepath.Join(exeDir, "captures"), "directory for captures")
```

Captures AND exports both land in this same `captures` folder
(`ui_actions.go`'s `BuildExport(c.ExeDir, c.OutDir, c.OutDir, ...)` passes the
same dir twice) — so that's one folder, not two. Everything else I found
(`collector-install-id.txt`, `collector-consent.txt`, settings, the log) is a
file, not a folder. **I don't know what the second folder is** — could be
something I haven't read yet, could be an artifact of how the zip was
unpacked rather than something the program creates.

**Since `exeDir` is wherever the exe happens to be sitting, if someone
unzips straight onto their Desktop instead of into a subfolder, `captures`
appears directly on the Desktop** — which reads as clutter even though it's
working as designed. That's very likely what both Sleven and his friend are
looking at.

**Don't guess — actually run it and look.** Run a fresh `collector.exe`
from a folder placed directly on a Desktop-equivalent location, same as a
casual user would, and see exactly what appears and where. Report back what
you actually saw, not a theory. If it really is just `captures` appearing
because the exe itself sits at Desktop root, say so plainly — that's a
packaging/instructions problem, not a code bug, and the fix is different
(e.g., always create one dedicated subfolder like `CitizenCollector_data/`
next to the exe instead of a bare `captures` folder, so even a Desktop-root
install produces one clearly-named thing instead of something that looks
like it could be anything). If there's a genuine second folder-creation path
I missed, find it and name it.

## What NOT to do

- Don't touch `ui.go`'s "Picture key" line — it's already correct.
- Don't invent the `collector-latest.json` schema — read `update.go`'s
  parsing code and match it exactly.
- Don't restructure the captures/output folder layout without reporting back
  what you actually found first — §3 is investigate-then-propose, not
  build-blind.
- Nothing commits or pushes without Sleven's explicit go-ahead, same as
  every other order.

## Report back

What `releases/collector-latest.json` needs to contain (matched against
`update.go`'s actual parsing, not assumed), confirmation the feed resolves
once published, and — separately — what you actually observed running the
collector fresh from a Desktop-root location: exactly which folder(s)
appeared, and your recommendation for §3.
