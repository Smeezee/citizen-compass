# Update — the update feed is worse than a missing file, the "two folders" are two shortcuts, and I overwrote Sleven's Desktop shortcut

Three findings. The last one is a mistake of mine and Sleven has to fix it,
because I am not permitted to.

---

## 1. I OVERWROTE THE DESKTOP AND START MENU SHORTCUTS. Sleven must repoint them.

Investigating §3 meant running the collector. I ran it from a scratch folder
specifically to avoid writing outside the repo — and **the program wrote outside
the repo by itself**, which is the whole point of §3:

```
[2026-08-09 20:27:51] shortcut: created C:\Users\david\Desktop\Citizen Collector.lnk
[2026-08-09 20:27:51] shortcut: created ...\Start Menu\Programs\Citizen Collector.lnk
```

Both **already existed** and were overwritten. They now point at
`...\Temp\claude\...\scratchpad\DesktopSim\collector.exe` instead of the real
collector.

I tried to repoint them at
`C:\Users\david\citizen-compass\citizen-collector\collector.exe` and **the write
was blocked** — correctly, by the same rule-6 guard I had just cited in my own
receipt. So I cannot fix it.

**Sleven: right-click each shortcut → Properties → set Target and Start-in back
to the real collector.** Or delete both and let the next real launch recreate
them.

**I have deliberately left the `DesktopSim` folder in place** so the shortcuts
still launch something rather than dangling. Say the word and I will remove it
once the shortcuts are repointed.

Two dialogs (consent, then shortcuts) also appeared on Sleven's screen during
that run and were answered — I do not know by whom, and I am not going to claim.

---

## 2. §3 ANSWERED: it is not two folders. It is two SHORTCUTS, and they are
   rewritten on every launch — including launches that immediately exit.

**No directory was created at all.** Not `captures`, not anything. What appeared
next to the exe were three *files* (`collector-auto.log`, `collector-consent.txt`,
`collector-shortcut.txt`) and, outside the folder, **exactly two `.lnk` files** —
one on the Desktop, one in the Start Menu.

**Two things. On clicking the icon. Every time.** That matches Sleven's
complaint precisely, except they are shortcuts rather than folders.

**The ordering is the bug.** In `main.go`'s double-click branch:

```
894  AskConsent(...)
906  OfferShortcuts(...)      <-- shortcuts created here
921  runUI(...)               <-- the single-instance check lives in here
```

So a launch **creates both shortcuts before it discovers another collector is
already running and exits.** My run proved it:

```
shortcut: created ...Desktop\Citizen Collector.lnk
shortcut: created ...Start Menu\...\Citizen Collector.lnk
another collector is already running, so this launch is exiting
```

Click the icon while it is running — which is exactly what somebody does when
the window is behind the game — and you get two shortcuts rewritten and nothing
else. **`captures/` never appeared because the process exited before `runUI`
got that far**, which also means C1's theory (a bare `captures` folder at
Desktop root) is *not* what Sleven is seeing.

**Recommendation, not built:** move `OfferShortcuts` to after the
single-instance check, so a launch that is going to exit does not touch the
Desktop at all. That is a small ordering change and it fixes the reported
symptom directly. Not doing it without a go-ahead, per §3 being
investigate-then-propose.

---

## 3. §2: the feed is missing AND the thing it would point at is missing too

C1 is right that `releases/collector-latest.json` has never existed on any
commit — verified against full history. But **creating it now would make things
worse, not better.**

`update.go` parses:

```go
Version string `json:"version"`
URL     string `json:"url"`      // direct download for collector.exe
SHA256  string `json:"sha256"`   // of the file at URL
Notes   string `json:"notes"`
MinFrom string `json:"min_from"`
```

and `update.go:187` **refuses any feed whose sha256 is not exactly 64
characters**, then hashes the download and compares.

`collector-latest.json.EXAMPLE` (already in the repo) points at
`releases/download/collector-v0.2.0/collector.exe`. **That asset does not
exist:**

```
collector.exe asset : HTTP 404
GitHub releases API : HTTP 200, body []   <- the repo has ZERO releases
```

So the sha256 field cannot be filled honestly, because there is no published
file to hash. Publishing a feed anyway would turn today's clean "no update
found" into "update available" followed by a failed download, on every install,
every six hours. **Right now the 404 is the safe state.**

`make-release.ps1` already encodes the correct order — *"asset first, always.
And the feed is not written at all until the asset"* has been downloaded back
from its public URL and re-hashed. It needs `gh`, which is not installed.

**So the real fix is one step, not two: publish 0.2.0.** Installing `gh` is
outside the repo and needs Sleven's say-so.

**Stated plainly, as asked: self-update is broken for every collector
everywhere, and will stay broken until a release is actually published. The
only way to get the friend onto a current build today is to hand him a fresh
package.**

---

## 4. §1 confirmed, nothing to do

`ui.go` does carry the picture-key row, with the comment quoting Sleven's
earlier complaint. The friend's window lacks it entirely, so he is on a build
from before it landed. C1's reading is right — and #3 is why he cannot catch up.
