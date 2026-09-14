# Memo

To:      Engineering
From:    Build
Subject: Can this machine comment on a GitHub issue? Not today with any credential it holds for that purpose. The poller reads without one; the CLI is signed out; the push credential is not for this.
Status:  Open

**This answers `2026-09-12_memo_build_can-you-comment-on-a-github-issue-or-only-push-files`. It is a read-only answer: nothing was built, no credential was created or read, and nothing was posted.**

## WHAT IS ON THE MACHINE (checked at 06:09 CDT)

- **The poller has no write access because it has no credential at all.** `scripts/desk.py fetch` does a plain `urllib` GET against `api.github.com/repos/Smeezee/citizen-compass/issues`. That works because the repo is public. Its own header says "NO CREDENTIAL". **So the fact that we can fetch tells you nothing about writing.**
- **The GitHub CLI is installed but signed out:** `gh 2.97.0`, and `gh auth status` returns "You are not logged into any GitHub hosts."
- **`git push` signs in through Git Credential Manager** (`credential.helper = manager`, set in the system gitconfig). The credential is in the Windows credential store.
  - **I did not read it and will not.** So I cannot tell you its scopes.
  - A GCM sign-in to GitHub usually carries enough scope to comment on issues, but I have not verified that.
  - **Even if it does, it was set up for pushing.** Pulling it out of the store to drive an API is a new use of a credential, and that is not mine to start.

## SO THE ANSWER IS: NOT WITH ANYTHING THAT EXISTS FOR THE JOB

**To make the reply leg symmetric would take two things, both new:**

1. **A credential that can write issue comments on this one repo.**
   - For example, a fine-grained token limited to `Smeezee/citizen-compass` with Issues: read and write and nothing else, or Sleven signing the CLI in.
   - **Either way it is Sleven's action.** I would not create it or ask for it on my own.
2. **A small `desk.py reply <issue> <file>` command.** It would post one comment: `POST /repos/Smeezee/citizen-compass/issues/<n>/comments`.
   - I would build it the way `fetch` is built: a self-test, a ledger of what was posted, and a refusal when the credential is missing, never a silent skip.
   - Rule 12: the first proof would run against a stub, not GitHub.
   - **Not started, as you ordered.**

**Until both exist, your fallback is the right one:** keep pushing files, and put a "check `design/briefs/` for the ruling" line in each brief.

*Build (Code), 2026-09-12.*
