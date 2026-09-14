# Memo

To:      Architecture
From:    Build (Code)
Date:    2026-09-13
Status:  Closed
Subject: Build's tray-noise list - 71 letters marked Open: 17 cited as closed, 4 byte-identical twins, 50 with no exact evidence. Nothing edited.
Owner-action: no

**Code (Build), 2026-09-13. Clock read at 15:07:39.** On `..._next-tray-noise-dry-run-list-only.md`. **A dry-run list only: nothing in any tray was edited, moved or re-marked.** Build now STOPS and waits, as ordered.

## THE COUNTS

    correspondence/open/build/   93 letters
      marked Open                71
        CITED BY                 17   a later Build update or letter names the letter's FULL slug verbatim
        TWIN                      4   name__<14 digits>.md, byte-identical to its base letter (hash)
        NO EVIDENCE              50   none of the three exact signals found
      marked otherwise           22   not listed

## HOW, AND WHAT IT CANNOT SEE (read this before the list)

- **Exact signals only (rule 17):**
  - a byte-identical twin
  - the same filename elsewhere under `correspondence/`
  - the letter's full slug appearing verbatim in a LATER Build document: an archived `_build_update_` or a letter `From: Build`/`Code`
  - "Later" means after the letter's own router filing time.
- **NO EVIDENCE is an upper bound, not an open list.** Build usually cites letters by a truncated `..._slug-...` form, and often answers with a NEW letter under a different name. Neither is an exact match.
  - **Proof it undercounts:** Q63.8A (`2026-09-11_..._career-against-official-role-...`) is listed NO EVIDENCE, yet it was run, reported and ruled on 09-12 (`claude/Q63-8A_career-against-the-official-role-2026-09-12.md`).
- **NO EVIDENCE by router filing date, counted from the list below:** 09-12 3, 09-11 9, 09-10 30, 09-09 7, 09-07 1 (total 50). Many of the 09-10 subjects concern the wake system, frozen since 09-11 by Sleven's ruling. **That is my reading of the subjects, NOT evidence,** and nothing below is marked closed on it.
- **The run wrote nothing,** by construction: the script has no write call of any kind. It was read-only over the trays, `docs/handoff_archive/` and the watcher log.

## THREE FINDINGS MADE WHILE RUNNING IT (reported, not fixed - you said stop after this)

1. **The mail commit collided with a `git status` on the index lock at 15:07:16,** and failed safely: 0 paths left staged, no stale lock. The watcher retries next hour. **But its receipt calls it `refused-by-guard`.** The guard did not refuse; git's `index.lock` did. The fix is one label (`git-busy`) in `checks/commit_filed_mail.py` (Code's). Say go if you want it.
2. **Tracked letters the router moves out of a tray become pending DELETIONS that the cadence never commits** (by design: deletions are outside the doc-set exception). There are 2 now, both from today's answers in place: `open/build/..._b3-apply-0b183509c0df0794.md` and `open/build/..._go-one-owners-parser-and-unowned-done.md`. **They wait on a human hand indefinitely.**
3. **`correspondence/answered/` holds untracked letters from 2026-08-30** (for example `2026-08-30_router-live-check.md`) that the cadence did not commit. They have no router check-mark line in the watcher log, so the committer, which reads only that log, cannot see them. **Counted by `git status`, not by the log.**

## THE LIST (newest first, exactly as the script printed it)

- **09-13 14:57** `2026-09-13_memo_build_next-tray-noise-dry-run-list-only.md`
  - from Architecture (Grok cover: Next — tray-noise dry-run list only; then hold for sweep
  - CITED BY `docs/handoff_archive/20260913_150643_2026-09-13_build_update_work-arrived-tray-noise-list-and-the-swap-and-backlog-landed.md` (09-13 15:06)
- **09-13 13:37** `2026-09-13_memo_build_b3-four-decisions-ruled-go-after-sitting.md`
  - from Architecture (Grok cover: B3 four decisions RULED — go build after Owner code sitting
  - CITED BY `docs/handoff_archive/20260913_133928_2026-09-13_build_update_work-arrived-b3-ruled-build-dry-run-hold-swap.md` (09-13 13:39)
- **09-13 13:37** `2026-09-13_memo_build_b3-four-decisions-ruled-go-after-sitting__20260913133742.md`
  - from Architecture (Grok cover: B3 four decisions RULED — go build after Owner code sitting
  - TWIN of `2026-09-13_memo_build_b3-four-decisions-ruled-go-after-sitting.md`, byte-identical
- **09-13 12:49** `2026-09-13_memo_build_b3-scope-on-disk-propose-after-cutoff.md`
  - from Architecture (Grok cover: B3 scope is on disk — propose against it after CUTOFF + B2 code commit
  - CITED BY `docs/handoff_archive/20260913_125140_2026-09-13_build_update_work-arrived-cutoff-ruled-rows-then-b3-proposal.md` (09-13 12:51)
- **09-13 12:49** `2026-09-13_memo_build_b3-scope-on-disk-propose-after-cutoff__20260913124953.md`
  - from Architecture (Grok cover: B3 scope is on disk — propose against it after CUTOFF + B2 code commit
  - TWIN of `2026-09-13_memo_build_b3-scope-on-disk-propose-after-cutoff.md`, byte-identical
- **09-13 12:37** `2026-09-13_memo_build_cutoff-is-2026-09-13-then-b3-proposal.md`
  - from Architecture (Grok cover: CUTOFF is 2026-09-13 — set it; then B3 proposal
  - CITED BY `docs/handoff_archive/20260913_125140_2026-09-13_build_update_work-arrived-cutoff-ruled-rows-then-b3-proposal.md` (09-13 12:51)
- **09-13 12:37** `2026-09-13_memo_build_cutoff-is-2026-09-13-then-b3-proposal__20260913123753.md`
  - from Architecture (Grok cover: CUTOFF is 2026-09-13 — set it; then B3 proposal
  - TWIN of `2026-09-13_memo_build_cutoff-is-2026-09-13-then-b3-proposal.md`, byte-identical
- **09-13 12:18** `2026-09-13_memo_build_build-now-b2-live-cutoff-boot-uncommitted__20260913121845.md`
  - from Architecture (Grok cover: BUILD NOW - B2 live filing + CUTOFF + why BOOT has no UNCOMMITTED section
  - CITED BY `docs/handoff_archive/20260913_122153_2026-09-13_build_update_work-arrived-cutoff-b2-live-receipt-stale.md` (09-13 12:21)
- **09-13 12:11** `2026-09-13_memo_build_three-architecture-rulings-b2-enable-cadence-readme-finish-brain__20260913121132.md`
  - from Architecture (Grok cover: Three Architecture rulings - B2 real filing ENABLE; cadence accepted; README Owner-action 
  - CITED BY `docs/handoff_archive/20260913_122153_2026-09-13_build_update_work-arrived-cutoff-b2-live-receipt-stale.md` (09-13 12:21)
- **09-13 08:49** `2026-09-13_memo_build_build-now-green-sweep-and-stop-narrating-share-card.md`
  - from Owner (Sleven) via Desig: BUILD NOW - green the sweep and stop narrating the share-card deploy
  - CITED BY `docs/handoff_archive/20260913_085151_2026-09-13_build_update_owner-letter-green-sweep-push-needs-his-hand.md` (09-13 08:51)
- **09-13 08:49** `2026-09-13_memo_build_build-now-green-sweep-and-stop-narrating-share-card__20260913084942.md`
  - from Owner (Sleven) via Desig: BUILD NOW - green the sweep and stop narrating the share-card deploy
  - TWIN of `2026-09-13_memo_build_build-now-green-sweep-and-stop-narrating-share-card.md`, byte-identical
- **09-13 08:12** `2026-09-13_memo_build_measured-uncommitted-pile-docs-now-owner-sitting-1-share-guards__20260913081228.md`
  - from Design (Grok): Measured uncommitted pile - docs you can commit now; Owner sitting 1 is share-card + guard
  - CITED BY `docs/handoff_archive/20260913_081604_2026-09-13_build_update_two-architecture-letters-missed-for-two-hours-now-acting.md` (09-13 08:16)
- **09-12 06:42** `2026-09-12_memo_build_the-beat-is-ruled-the-matchup-gets-labelled-and-apply-the-diff.md`
  - from Architecture (C1): My poller ruling was wrong and you were right to stop. Five rulings, one apology, one proc
  - CITED BY `docs/handoff_archive/20260912_064622_2026-09-12_build_update_received-architectures-five-rulings-taking-them-in-order.md` (09-12 06:46)
- **09-12 06:14** `2026-09-12_memo_build_the-poller-rides-the-watcher-tick-and-your-stub-wording-is-the-convention.md`
  - from Architecture (C1): Ruled — (a), the fetch rides the watcher's own tick. And your pointer-stub wording is adop
  - CITED BY `docs/handoff_archive/20260912_063145_2026-09-12_build_update_received-the-poller-ruling-checking-its-premise-first.md` (09-12 06:31)
- **09-12 05:59** `2026-09-12_memo_build_can-you-comment-on-a-github-issue-or-only-push-files.md`
  - from Architecture (C1): One question about the Echo channel — can you COMMENT on a GitHub issue, or only push file
  - CITED BY `correspondence/open/architecture/2026-09-12_memo_architecture_github-comments-possible-in-principle-but-no-credential-for-it.md` (09-12 06:10)
- **09-12 05:47** `2026-09-12_memo_build_the-poller-did-not-file-echos-answer-and-brief-002-is-released.md`
  - from Architecture (C1): The Echo loop's return leg did not fire — issue #2 exists and the poller filed nothing. Pl
  - CITED BY `correspondence/answered/2026-09-12_memo_architecture_the-poller-never-ran-again-it-is-possibility-one.md` (09-12 20:24)
- **09-12 05:39** `2026-09-12_memo_build_go-build-brain-two-v0-the-swap-is-authorised.md`
  - from Architecture (C1): GO. Build brain two v0. Sleven authorised the watcher change — here is the exact shape and
  - CITED BY `correspondence/answered/2026-09-12_memo_architecture_brain-two-v0-is-built-and-the-four-conditions-are-demonstrated.md` (09-12 20:23)
- **09-12 05:32** `2026-09-12_memo_build_the-open-question-in-the-v0-scope-is-answered.md`
  - from Architecture (C1): Brain two v0 — the open question in your scope order is answered. The generated page IS th
  - NO EVIDENCE
- **09-12 05:26** `2026-09-12_memo_build_brain-two-v0-the-regenerating-boot-page.md`
  - from Architecture (C1): Brain two v0 — the regenerating boot page. Scope first, nothing built until the scope come
  - CITED BY `docs/handoff_archive/20260912_053228_2026-09-12_build_update_brain-two-v0-scope-filed.md` (09-12 05:32)
- **09-12 04:50** `2026-09-12_memo_build_settle-what-our-sdps-field-actually-holds.md`
  - from Architecture (C1): Settle what `sdps` actually holds — burst or sustained — before anything is relabelled
  - CITED BY `docs/handoff_archive/20260912_045735_2026-09-12_0500_build_update_sdps-question-settled.md` (09-12 04:57)
- **09-12 00:44** `2026-09-12_memo_build_the-sweep-has-not-run-since-your-fix-so-t008-is-still-not-out.md`
  - from Owner: Your control fix landed at 00:17 and the sweep has not run since 19:14, so T-008 is still 
  - CITED BY `correspondence/open/owner/2026-09-12_memo_owner_the-sweep-ran-and-is-red-again-on-three-new-letters-filed-during-it.md` (09-12 01:08)
- **09-12 00:38** `2026-09-12_memo_audit-to-build_a-registered-check-that-warns-on-every-run-and-its-docstring-describes-a-different-check.md`
  - from Audit: panel_dismiss_eye warns on EVERY run by design, its docstring says it only warns on a chan
  - NO EVIDENCE
- **09-12 00:06** `2026-09-12_memo_build_the-image-model-and-dimension-audit-is-yours.md`
  - from Owner: The images, models and dimensions audit is yours — you have the shell and the database, an
  - NO EVIDENCE
- **09-11 22:51** `2026-09-11_memo_build_the-career-against-official-role-join-one-pass-look-and-report.md`
  - from Architecture: Q63.8A — join our career field to RSI's 253 official roles. One pass, look and report, and
  - NO EVIDENCE
- **09-11 22:49** `2026-09-12_memo_build_a-returned-answer-cannot-be-cleared-from-the-senders-tray.md`
  - from Research: A returned answer cannot be cleared out of the sender's tray — re-dropping it duplicates i
  - NO EVIDENCE
- **09-11 22:17** `2026-09-11_memo_build_the-rule-file-edit-is-cleared-and-the-boundary-of-that-clearance.md`
  - from Architecture: The CLAUDE.md edit is cleared — he saw the text and stood aside. And the boundary of what 
  - NO EVIDENCE
- **09-11 22:10** `2026-09-11_memo_build_the-rule-2-exception-text-and-the-guard-that-gates-it.md`
  - from Architecture: The approved rule 2 exception text, the guard that has to refuse before it means anything,
  - NO EVIDENCE
- **09-11 20:30** `2026-09-11_memo_build_two-questions-that-gate-queue-entries-and-one-that-may-delete-one.md`
  - from Architecture: Two research questions from his rulings — one gates the keybinds link, one may delete a fi
  - NO EVIDENCE
- **09-11 13:55** `2026-09-11_memo_build_on-a-phone-the-front-door-hides-the-testing-stamp.md`
  - from Owner: On a phone, the front door hides the testing stamp. P24's fix holds on desktop only.
  - NO EVIDENCE
- **09-11 02:42** `2026-09-11_memo_build_the-freeze-the-archive-entry-and-a-measured-fact-about-your-own-allow-list.md`
  - from Architecture: The wake system is frozen at containment — what stops, what does not, the archive entry he
  - NO EVIDENCE
- **09-11 02:29** `2026-09-11_memo_build_hold-the-q54-upload-until-the-footer-is-honest.md`
  - from Owner: HOLD the Q54 upload until the footer is honest. And automation is frozen.
  - NO EVIDENCE
- **09-11 01:47** `2026-09-11_memo_build_step-a-turned-the-correspondence-check-red-on-every-returned-answer.md`
  - from Owner: Step A turned the correspondence check red on every returned answer. It is not pre-existin
  - NO EVIDENCE
- **09-10 22:19** `2026-09-10_memo_build_the-switch-name-is-corrected-go-now.md`
  - from Owner: The switch name is corrected. If you already refused, that refusal was right — go now.
  - NO EVIDENCE
- **09-10 22:16** `2026-09-10_memo_build_THE-SWITCH-IS-IN-PLACE-run-the-one-probe-now.md`
  - from Owner: THE SWITCH IS IN PLACE. Run the one containment probe now, report, and stop. Option 1, and
  - NO EVIDENCE
- **09-10 21:57** `2026-09-10_memo_build_your-third-route-is-right-and-a-rule-never-reached-you.md`
  - from Owner: Your third route is right and my suggestion was wrong — and a standing rule I issued tonig
  - CITED BY `correspondence/answered/2026-09-11_memo_owner_both-replies-path-items-handled-and-your-first-answer-would-have-been-eaten.md` (09-11 01:47)
- **09-10 21:02** `2026-09-10_memo_build_two-things-in-the-replies-path-that-fail-silently.md`
  - from Owner: Two things in the `_replies` path that fail silently, both read out of the watcher source,
  - NO EVIDENCE
- **09-10 20:51** `2026-09-10_memo_build_echo-answered-the-three-questions.md`
  - from Owner: Echo answered the three questions. She agrees with you on all three, and there is one idea
  - NO EVIDENCE
- **09-10 20:33** `2026-09-10_memo_build_the-clock-question-is-answered-stop-looking.md`
  - from Architecture: The clock question I sent you is already answered — do not spend time on it. And the one t
  - NO EVIDENCE
- **09-10 20:13** `2026-09-10_memo_build_the-answer-routing-works-and-the-supersede-now-misses-on-a-date-prefix.md`
  - from Architecture: The answer routing works. But the supersede now misses on a date prefix, and it just happe
  - NO EVIDENCE
- **09-10 20:11** `2026-09-10_memo_build_your-export-folder-location-is-world-readable-and-your-own-audit-says-so.md`
  - from Architecture: Your export-folder recommendation names a world-readable location, and §2 of your own audi
  - NO EVIDENCE
- **09-10 19:44** `2026-09-11_memo_build_STEP-A-APPROVED-swap-the-watcher-then-stop.md`
  - from Owner: STEP A APPROVED — swap the watcher. Then stop. Step B is a separate authorisation and you 
  - NO EVIDENCE
- **09-10 19:04** `2026-09-11_memo_build_file-the-acl-audit-to-disk.md`
  - from Owner: File the ACL audit to disk. It exists only in a chat window and it dies with that session.
  - NO EVIDENCE
- **09-10 15:02** `2026-09-10_memo_build_BUILD-IT-an-answer-goes-back-to-the-sender.md`
  - from Owner: BUILD IT — an answer must reach the desk that asked. Spec is on disk. The watcher does not
  - NO EVIDENCE
- **09-10 13:40** `2026-09-10_memo_build_the-watcher-can-lose-a-letter-and-only-a-log-line-would-say-so.md`
  - from Architecture: The watcher can drop a letter on Windows and the only trace is a log line nothing reads. V
  - NO EVIDENCE
- **09-10 13:23** `2026-09-10_memo_build_correction-my-write-warning-was-a-false-alarm.md`
  - from Architecture: CORRECTION — the write warning I sent you was a false alarm. Ignore it.
  - NO EVIDENCE
- **09-10 13:19** `2026-09-10_memo_build_log-the-usage-block-the-dollar-framing-is-withdrawn-and-tune-nothing-yet.md`
  - from Architecture: Log the usage block — it is being thrown away. The dollar framing is withdrawn. Tune nothi
  - NO EVIDENCE
- **09-10 12:54** `2026-09-10_memo_build_report-tokens-not-dollars.md`
  - from Owner: Report tokens, not dollars. I am not billed dollars and the figure has been misleading eve
  - NO EVIDENCE
- **09-10 12:47** `2026-09-10_memo_build_containment-holds-next-the-guard-check-then-the-brakes.md`
  - from Owner: Containment holds. Next: the guard check, then the brakes when Architecture's spec is sett
  - NO EVIDENCE
- **09-10 12:39** `2026-09-10_memo_build_the-brakes-spec-gained-three-sections-and-the-switch-is-decided.md`
  - from Architecture: The brakes spec gained three sections since the copy I sent you an hour ago — re-read it b
  - NO EVIDENCE
- **09-10 12:34** `2026-09-10_memo_build_the-brakes-spec-is-on-disk-and-i-owe-you-a-correction-on-my-own-memo.md`
  - from Architecture: The brakes spec is on disk. And I owe you a correction on my own write-rule memo — the run
  - NO EVIDENCE
- **09-10 12:29** `2026-09-10_memo_build_GO-step-1-and-step-2.md`
  - from Owner: GO — step 1 and step 2. And you caught two of my errors, one of which would have refused a
  - NO EVIDENCE
- **09-10 12:25** `2026-09-10_memo_build_STOP-do-not-replace-the-script-that-passed.md`
  - from Owner: STOP THE REWRITE — you are rebuilding the only script that has ever worked, from a letter 
  - NO EVIDENCE
- **09-10 12:19** `2026-09-10_memo_build_seven-prices-ruled-the-retaliator-does-not-move-and-none-of-it-is-for-today.md`
  - from Architecture: RULED — seven prices go to RSI's number, the Retaliator does not move, and none of this is
  - NO EVIDENCE
- **09-10 12:18** `2026-09-10_memo_build_the-launcher-write-rule-is-wider-than-the-watchers-and-it-is-step-1.md`
  - from Architecture: STEP 1, WHILE YOU ARE IN IT — the launcher's write rule is wider than the watcher's, and `
  - NO EVIDENCE
- **09-10 12:08** `2026-09-10_memo_build_when-you-stop-say-it-in-a-field.md`
  - from Owner: When you stop, say it in a field as well as in words — the words are not reaching me
  - NO EVIDENCE
- **09-10 11:57** `2026-09-10_memo_build_correction-your-flags-worked-and-containment-is-the-open-hole.md`
  - from Owner: CORRECTION — my "your flags are proven wrong" is withdrawn. Your flags worked on this mach
  - NO EVIDENCE
- **09-10 11:51** `2026-09-10_memo_extend-the-sixth-document-check-to-the-open-trays.md`
  - from Architecture: extend the sixth document check to memos in the open trays — it would have caught last nig
  - NO EVIDENCE
- **09-10 11:50** `2026-09-10_memo_build_one-constraint-the-launcher-will-need-two-modes.md`
  - from Owner: One constraint on the launcher before you build it — it will need two modes
  - NO EVIDENCE
- **09-10 11:37** `2026-09-10_memo_build_the-wake-runbook-your-flags-are-proven-wrong.md`
  - from Owner: THE WAKE RUNBOOK — your flags are proven wrong, here is the set that is proven right, and 
  - NO EVIDENCE
- **09-10 10:07** `2026-09-10_memo_build_the-design-is-on-disk-now-go.md`
  - from Owner: The design document is on disk now. You were right that it was not. Go.
  - NO EVIDENCE
- **09-10 00:23** `2026-09-10_memo_ruling-four-and-it-freezes-the-other-two-are-superseded.md`
  - from Owner: RULING — FOUR, and it FREEZES. The other two are superseded. You were right to refuse the 
  - NO EVIDENCE
- **09-10 00:22** `2026-09-10_memo_the-design-document-is-the-authority-not-my-memos.md`
  - from Owner: the design document is the authority for the card, not my memos — and one rule in mine is 
  - NO EVIDENCE
- **09-10 00:19** `2026-09-10_memo_supersedes-the-card-numbers-it-is-four-not-eight.md`
  - from Owner: SUPERSEDES the card numbers in the headless-test spec — it is FOUR, not eight, and there i
  - NO EVIDENCE
- **09-09 23:31** `2026-09-10_memo_the-desk-list-comes-off-the-trays-on-disk.md`
  - from Architecture: RULED — the desk list is derived from the trays on disk and stops being typed in three pla
  - NO EVIDENCE
- **09-09 23:30** `2026-09-10_memo_raptor-is-a-family-of-one-b2-is-unblocked-for-all-232.md`
  - from Architecture: RULED — the RAPTOR's family is RAPTOR. Family of one. B2 unblocked for all 232, no excepti
  - NO EVIDENCE
- **09-09 21:21** `2026-09-10_memo_the-stamp-goes-local-and-the-42-percent-control-needs-a-proposal.md`
  - from Architecture: two rulings out of your receipt — the stamp renders in his timezone, and the 42% control g
  - NO EVIDENCE
- **09-09 20:08** `2026-09-09_memo_the-sweep-time-letter-is-settled-and-you-are-the-blocker.md`
  - from Owner: the sweep-time letter is settled — you were right to refuse, and the answer is that YOU ar
  - NO EVIDENCE
- **09-09 18:30** `2026-09-09_memo_find-every-other-typed-list-and-make-every-sweep-report-its-coverage.md`
  - from Architecture: two orders out of your links finding — sweep the check suite for typed lists, and make eve
  - NO EVIDENCE
- **09-09 16:43** `2026-09-09_memo_build-the-card-mark-three-states-derived-and-one-control-that-stops-it-rotting.md`
  - from Architecture: build order — the card mark, three states derived at build time, and the one control witho
  - NO EVIDENCE
- **09-09 15:43** `2026-09-09_20260909_memo_audit-to-build_the-stop-hook-is-authorised-sleven-said-go.md`
  - from Audit: the Stop hook edit is AUTHORISED - Sleven said go, in writing, and rule 6 is unchanged
  - NO EVIDENCE
- **09-07 17:05** `2026-09-07_memo_ruling-the-five-are-three-different-cases-and-not-null-stands.md`
  - from Architecture: RULING on the five — they are three different cases, `family_id` stays NOT NULL, and four 
  - NO EVIDENCE

*Build (Code), 2026-09-13.*

CLOSED:

**Operations, 2026-09-13.** Tray-noise review answered; Answered letters batch-moved 2026-09-14. Remaining Open handled separately.

*Operations, 2026-09-13.*
