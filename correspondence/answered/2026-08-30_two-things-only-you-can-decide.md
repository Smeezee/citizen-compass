# Memo

To:      Owner
From:    Architecture
Date:    2026-08-30
Subject: two small things that are yours by rule, neither urgent, both costing nothing today
Status:  Answered

**Neither of these is blocking anything. They are here because they are yours by
rule and they were sitting in a handoff nobody was required to read.**

## 1. The consent text is 238 characters over the limit its own test asserts

    the approved wording        2,838 characters
    consent_selftest.go:225     asserts  len(text) <= 2600
    consentVersion              4

**Two ways and they are both one line:** trim the wording, or move the limit.

**Nobody but you may touch consent wording**, which is why it has sat. If you say
"move the limit" that is Code's to do in a minute. If you say "trim it" you would
need to say what comes out, or approve a trim someone drafts for you.

**Cost of leaving it: nothing today.** It is a test asserting a bound the real
text exceeds — worth closing so the assertion means something again.

## 2. Twelve files will show as modified the next time they are edited

Code measured this and I confirmed the measurement. **My own note about it was
wrong on both its premises and has been corrected in NEXT.md.**

Twelve tracked files were committed before line-ending normalisation. They cost
nothing until one of them is next edited, and then that one shows as changed when
it is not.

**The fix is one command over twelve named paths, and it needs a commit — which
makes it yours, not mine and not Code's.** Say go and Code runs it.

**I have already turned down the bigger version of this** — normalising all 2,053
tracked files — because it is a huge diff bought for no present gain. Recorded so
nobody offers it to you as the tidier option.

## Nothing else needs you

Everything else open today is between Code and me and is moving. **Do not read
this as a queue.** Two lines, whenever you feel like it.

**What I checked:** `git config core.autocrlf` is true and `.gitattributes` has
existed since 2026-08-20 — I verified both myself rather than taking them from
Code's memo. **What I did not:** the twelve paths individually, or whether the
2,838-character consent text is still the wording you approved.

---
ANSWERS: C1, 2026-09-06.

**Item 1, the consent text: ruled.** Sleven removed the question rather than
choosing between trim and raise — there is no consent on the collector for now,
and it is redesigned fresh before the program reaches anybody but him.

**Item 2, the twelve CRLF files: already done before it was asked about.** Commit
`87b8ae9`, exactly twelve files, 1,102 insertions against 1,102 deletions.
Verified from the repository's own history.

**The failure this memo records is the mail, not Sleven.** It sat a week because
nothing required anyone to open it, and half of it was a request to approve
finished work. Rule 24 exists for this class of failure.
