# Update — three more memos closed: the two mailboxes and the sweep receipt

**2026-09-09 15:43 CDT** (`date`, read immediately before writing this).

## THE STOP HOOK IS BLOCKED — FILED SEPARATELY, NOT FORGOTTEN

Sleven authorised it twice and my own permission layer refuses both routes to
`.claude/settings.json`. Backup taken, every claim verified from disk, the exact
change written out. See the stall update filed at 15:37.

## THE AUDIT MAILBOX — ALREADY BUILT, NOW VERIFIED IN BOTH DIRECTIONS

`"audit"` is in `memoTrays`, the tray exists, README and checker agree.

**Rule 12 rather than assumption:** planted `"auditing": "audit"` into the
router's map and `TestAddingAuditDidNotWidenWhatIsAccepted` went red naming it —
*"a memo to \"auditing\" was ACCEPTED and filed to open\audit"*. `memo.go`
restored byte-for-byte, verified by SHA-256.

## THE DESIGN MAILBOX — THE ROUTER HAD IT, THE NEAR-MISS TEST DID NOT

`design` was already in `memoTrays`. **The condition Architecture set was not
met**: *"Designer and Designs must bounce"* — and no test covered design in
either direction.

Written: `watcher-go/memo_design_desk_test.go`, four tests covering delivery,
case-folding, and nine near-misses. Planted `"designer": "design"` and both new
tests went red. Restored and verified.

**A stale test found on the way.** `TestTheRefusalNamesEveryRealDesk` types five
desk names and has been passing green without ever mentioning design since the
day design landed. It would not notice a seventh desk either. My replacement
reads the list out of `memoTrays`. The old one is left alone — it is not wrong,
only blind.

**The class question answered, not built.** Architecture asked whether to derive
the desk list from the trays on disk. **No** — a typo'd directory would silently
become a desk nobody staffs, which is the exact failure the refusal path exists
to prevent, and empty tray directories do not survive a git clone. Counter-proposal
filed: one tracked `correspondence/desks.json`, embedded into the router with
`go:embed` so a missing list fails the BUILD rather than producing a router that
accepts nothing. Not built — it was a question, not an order.

## THE SWEEP RECEIPT — DONE-WHEN MET, WORKING FIGURE ADDED

`timings` was already in the receipt. Exercised it on the receipt on disk with
nothing re-run:

    1,741.8s total, 124 controls, ten most expensive = 1,366.2s (78.4%)
    _verify_broken_checker_end_to_end.py alone = 652.6s (37.5%)

**The sixty-minute working figure was never implemented.** `3600` appeared
nowhere in the sweep. `run_all_controls.py` now prints a report line after a full
sweep when it is crossed — naming both numbers and saying NOT GATED — via a pure
function that returns text and can never touch an exit code. Silent on `--only`
and `--self-test` at any duration.

Proven by `checks/_verify_sweep_runtime_line.py`: 8 cases, **0.24s**, both sides
of the boundary including 60:00.0 exactly, `--self-test` exits 1.

## TOTAL COST I HAVE ADDED TO THE DEPLOY SWEEP TODAY

    _verify_document_checks.py      0.6s
    _verify_eyes.py                 1.4s
    _verify_sweep_runtime_line.py   0.1s
                                    2.1s   =  0.12% of the current sweep

The six document checks and the two eyes add **nothing** — auditor layer. Only
their proofs are swept. `_verify_rule16_labels.py` green: 129 checks, 0
unlabelled.

**Build tray: eight memos closed, one sent back, one blocked. Eleven left.**
Nothing committed.
