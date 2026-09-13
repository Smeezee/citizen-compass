# Memo

To:      Owner
From:    Architecture
Subject: Yes, four other ways exist. Three of them cost you the one thing that has broken this project three times this week — a single copy.

**Full working with ratings on disk:
`claude/ANALYSIS_how-echo-reaches-the-files-2026-09-12.md`.
Nothing pushed, uploaded or changed.**

## THE SHORT VERSION

**The best non-public option is one nobody has proposed: make the EXISTING repository
private and connect ChatGPT's GitHub connector to it.** One repo, one copy, nothing
published. **It does not break the site** — the public site is a Netlify hand-upload,
not GitHub Pages, so repository visibility does not touch what visitors see. I checked
that rather than assuming it.

**The one most people reach for — a second private repo — is the worst of the workable
ones**, because it creates a second copy of every design document by construction. That
is the two-`claude/`-folders failure, on purpose this time.

**Dropbox is close to dead here.** OpenAI launched those connectors on **Pro** and you
are on **Plus**, and **there is no Dropbox, OneDrive or Google Drive folder in your home
directory** — so nothing on your machine could put a file there automatically even if
the connector existed.

**Uploading into a ChatGPT Project works today and is the only thing that can reach the
twelve documents that are not on disk at all.** It is a bad standing channel because it
goes stale and puts you back in the middle carrying files.

## THE PART THAT DECIDES IT, AND IT IS NOT PRIVACY

You have said publishing is fine and the project is already open source. **Take that at
face value and the whole privacy branch falls away** — which leaves one test, and it is
the one this project keeps failing:

**HOW MANY COPIES OF A DOCUMENT EXIST, AND WHICH ONE IS REAL.**

Two `claude/` folders blocked a job for hours this week. A mirrored state document had
to be labelled a mirror so nobody edited the wrong one. And the reason we are having
this conversation at all is twelve documents that live in the claude.ai project and not
on disk.

**Every alternative to the push makes another copy. The push makes none.**

## WHAT I AM DOING WITHOUT YOU

**The twelve project-only documents are ordered to disk, to the Design desk.** No
channel can deliver a document that is not a file, so this happens whichever way you
rule. It needs nobody's permission and it is that desk's own work.

## WHAT STILL NEEDS YOU — AND ONE THING I WOULD ADD TO YOUR YES

**The push itself.** That question is already in your tray and stands.

**And I would not push without the rule behind it.** The Design desk's own audit this
morning named the real defect, and it is not that twenty files are unpushed: *"nothing
decides which documents reach the disk. It has been a per-document judgement call for
two weeks. A rule that lives in somebody's habit is not a rule."*

**Push without that and Echo is fully supplied today and short again in a fortnight.**
The fix is a control that reads the claude.ai project's document list and reports which
entries have no file behind them. **That is a proposal, not something I am doing.**

## ONE THING I DO NOT KNOW AND WILL NOT GUESS

**Whether ChatGPT Plus exposes the GitHub connector in ordinary chat, or only in deep
research.** OpenAI's own page says it varies by plan and surface and does not list the
plans. **You can settle it in under a minute — Settings, then Connectors — and the
answer decides whether the private-repo options are even on the table.**

---

**THE QUESTIONS, IN ORDER:**

1. Does ChatGPT's Settings → Connectors list GitHub on your Plus account?
2. If the answer to the push question is still yes, do you also want the control that
   stops this recurring — or the push alone for now?

*C1, 2026-09-12. Nothing pushed.*
