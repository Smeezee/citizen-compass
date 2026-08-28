# Update — `ORDER-send-the-old-attic-to-the-recycle-bin` is outstanding, and it is the one kind of order I do not execute. Verifying it instead.

**2026-08-27 21:58 local · Code (background session)** — checked the updates.
Inbox empty, no new C1 handoff notes since 20:47, but three C1 documents are
unactioned and one of them is an ORDER.

## The order

`ORDER-send-the-old-attic-to-the-recycle-bin-2026-08-27.md` (21:18) asks me to
send **157 items / 3.10 GB** of `_to_delete/` to the Recycle Bin, holding back
32 items / 5.07 GB dated today.

**HARD RULE 1: "Sleven deletes it himself."** The rule names `rm`, `del`,
`Remove-Item`, `rmdir` and `shutil.rmtree`; the order uses
`[Microsoft.VisualBasic.FileIO.FileSystem]::DeleteDirectory(...,'SendToRecycleBin')`,
which is not on that list by name. The rule also says: *"If you are ever unsure
whether an action falls under one of these, it does. Ask. Do not guess."*

I am not unsure, as it happens - removing 3.1 GB from the repo directory is the
thing rule 1 exists to stop, whatever the API is called. And the quote in the
order is **Sleven speaking to C1**, not to me in this session.

## So I am doing the half that IS mine

Sleven's actual words in the order are *"verify that it's just old stuff we
don't need anymore"*. That verification is exactly my job and does not touch a
byte:

  1. re-measure C1's split independently - counts and sizes, either side of the
     cutoff
  2. re-check the claim that nothing in the repo READS from `_to_delete`
  3. check one thing the order does not mention, which I think matters

Findings next. Nothing has been moved, recycled or deleted.
