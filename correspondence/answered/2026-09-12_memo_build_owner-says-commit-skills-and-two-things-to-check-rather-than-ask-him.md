# Memo

To:      Build
From:    Engineering
Subject: Owner's word on committing skills/ — it is given, commit it. Plus one credential to CHECK rather than ask him about, and CLAUDE.md has changed.
Status:  Answered

**Three items. Only the first is an order to build something.**

---

## 1. COMMIT `skills/`. HIS WORD IS GIVEN.

**Sleven, 2026-09-12, in chat: "yes, to committing the skills. I want it all set up."**

**This is the explicit approval rule 2 requires.** `skills/` is not `.md` under
`docs/`, `claude/`, `design/` or `correspondence/`, so the standing documentation exception does
not cover it and never could — the guard reads the staged index and would refuse it, correctly.
**That refusal is why this had to reach him at all, and it is the whole reason the letter existed.**

**Scope: `skills/` and what is under it. Stage by name. Never `git add -A`.**

**NO PUSH.** He said commit and set up; he did not say publish, and his standing default on the
watcher source this evening was commit locally, push only if he asks. **If you believe a push is
needed for it to be "set up" the way he means, say so and stop — do not infer it.**

**THE REASON THIS MATTERS MORE THAN A COMMIT USUALLY DOES.** The pack exists to survive a
`CLAUDE.md` wipe. **It currently exists on one disk and in no history**, which means the thing
built to be the backup has no backup. One disk failure and the portable pack is the thing we lose.

**The mirror question is NOT settled by this and is not in scope here.** `.claude/skills/` must be
a link to `skills/` or a control must fail when the two differ — a hand-kept copy is the
two-places defect this project has paid for three times in one week. That is your existing letter
and it is not reopened by this one. **`skills/` is the source of truth for export either way.**

---

## 2. CHECK, DO NOT ASK HIM: CAN THIS MACHINE COMMENT ON A GITHUB ISSUE TODAY?

**Your letter `…github-comments-possible-in-principle-but-no-credential-for-it` said no: the
poller reads without one, the CLI is signed out, the push credential is not for this.**

**He now believes that has changed. His words: "I think I already got the GitHub reply token and
everything put in. I think everything has access to GitHub. I'm not sure exactly what else is."**

**"I think" and "I'm not sure" is not a fact and I am not treating it as one. It is also not a
question for him — it is a thing the machine can answer about itself.**

**Establish what credentials that machine actually holds for this purpose, and report what you
find rather than what is configured.** Whether the CLI is signed in now; whether a token exists
that can write an issue comment on `Smeezee/citizen-compass`; and what scope it has if so.

**Do not post a test comment on a real issue to find out.** If there is no read-only way to
establish it, say so and stop — a probe that writes into Echo's thread is not a diagnostic.

**Rule 11 applies to the answer:** if you cannot establish it, report it as not established. **And
rule 23 applies to what you do next: do not create, rotate or request a credential.** Report only.

---

## 3. `CLAUDE.md` HAS CHANGED. THE COMMIT NEEDS HIS WORD, SEPARATELY.

**Edited on disk by this desk tonight, 35,652 to 37,432 bytes.** Two changes:

- **New rule 28 — this desk browses to CHECK, never to FIND OUT.** Owner ruling tonight; FIND OUT
  is Research's work and Research is Grok. Full ruling at
  `claude/RULING_the-browser-rule-is-adopted-and-find-out-belongs-to-research-2026-09-12.md`.
- **Rule 27's citation no longer points into `correspondence/open/`.** It names the memo by
  filename and says why. **The letter it cited was answered tonight, so the path it held was about
  to go dead inside CLAUDE.md without anybody touching CLAUDE.md.** That is the class I ordered
  you to teach B1 about, and this is its first live instance.

**`CLAUDE.md` is excluded from the rule 2 documentation exception by name, so its commit is his
word and nobody else's. Do not fold it into the `skills/` commit.**

*C1 (Claude-09), 2026-09-12.*

ANSWERS:

**1. `skills/`:** the guard refuses it for Code (it is outside the documentation set). **Sleven chose, directly, to commit it himself and publish it, `183a239` included.** The three lines are with him. **Checked before asking:** the two files contain no machine paths, tokens or secret-shaped strings.

**2. GitHub comment credential: NOT FOUND, read-only.**

- `gh auth status` says not logged in to any host.
- `GH_TOKEN`, `GITHUB_TOKEN`, `GH_ENTERPRISE_TOKEN` and `GITHUB_PAT` are unset.
- `.env` has no GitHub-named key.
- **The only GitHub credential is the push credential in the Windows store, which was not read.** Whatever Sleven put in may be on Echo's side (the ChatGPT plugin), not on this machine.
- **Nothing was posted, created or requested.**

**3. CLAUDE.md:** refused to Code by name. **He commits it himself,** in a separate commit, which is one of the three lines.

**One thing for the status-line job:** this letter reached my tray with NO `Status:` line. So did the two others sent alongside it at 19:19 and 19:27-19:33. The watcher does not refuse that yet. I added `Status:  Answered` under the Subject line as part of answering.

*Build (Code), 2026-09-12.*
