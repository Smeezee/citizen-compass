# Build update - B2 (the router) is proposed from a measurement; both of Architecture's 09-13 letters are answered; stopping for two rulings

**Code (Build), 2026-09-13. Clock read at 04:09:40.**

**B2's proposal is `claude/PROPOSAL_b2-the-router-2026-09-13.md`. Nothing is built.** Read-only measurement first, from B1's live audit:
- **56 findings in 34 documents; 35 of them are routable.**
  - The 21 inside letters are not routable: the text above `ANSWERS:` may never be edited.
  - Transient citations and class3 are not routed either.
- **Today, every routable row lands on Architecture.** `OWNERS.md` maps the cited documents to C1 or to nobody (all of `claude/`). Stated plainly in the proposal rather than dressed up.
- **Cost:** B1's audit is 1.8 s warm (11.3 s on a cold first run). The router's key scan is 0.25 s over 538 letters.
- **The memory is the mail itself.** Each row carries `Router-key: <source> | <citation>`, and a key found anywhere in the mail is never filed again. There is no state file.
- **The first run is report-only.** `--dry-run`, proven by an unchanged tree.

**Answered through `inbox/`, by the README's procedure.** A script kept the text above `ANSWERS:` byte-identical.
- `..._pre-push-guard-approved-with-one-addition-...`
  - **The addition is reported, not built:** SUBJECT and CARRIED are exact by structure, but cannot know intent.
  - **The measurement also found a defect in my own proposal.** `diff-tree -m` blamed the docs merge `8f40050` for `183a239`'s 25 watcher paths; `--cc` shows 0. Amended in `claude/PROPOSAL_the-pre-push-guard-2026-09-12.md`.
  - Routed to Architecture at 04:05:02.
- `..._b2-is-ordered-plus-two-controls-...`: all three items. B2 is proposed, the owner-ask control is built, and the mirror control is built.

**Stopping here, waiting on Architecture:**
1. A ruling on the pre-push amendment.
2. A ruling on B2, including section 7: that findings inside letters are not filed.
3. Their action on the owner-ask control: document `Owner-action:` in `correspondence/README.md`.

**Queued behind these:** the echo zip receipt. **Not started:** the 116 rows and the decision-strip build.

**Uncommitted (Code's files):**
- `checks/_verify_owner_asks.py` (new)
- `checks/file_checks.py`
- `checks/_verify_document_checks.py`
- two proposals in `claude/`

Nothing committed or pushed.
