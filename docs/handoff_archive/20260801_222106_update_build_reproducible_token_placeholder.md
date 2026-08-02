# UPDATE — build made reproducible and verified; deploy still blocked, token not received

`4d07f6b` pushed. Filed per rule 13.

## THE TOKEN — I did not write anything to `.env`, and why

**The value that reached me is the literal string `<TOKEN>`** — a placeholder,
not a credential. Cloudflare API tokens are ~40 characters of
alphanumerics/underscores; this is 7 characters of angle-bracketed placeholder.
Either the transcript redacted it or the paste did not carry.

**I have not written it to `.env`.** Putting a placeholder into a secrets file is
worse than leaving the key absent: it fails later as a confusing auth error, and
it sits in the one file on this machine that is supposed to contain only real
credentials, where a future reader may mistake it for one.

`.env` still holds `DATABASE_URL` and `UEX_API_TOKEN` only, and was confirmed
**ignored, untracked, and absent from the HEAD tree** — three separate checks —
before any write was contemplated.

**Recorded as instructed:** Sleven reports the earlier value of this token was
exposed in a chat transcript and **has been rolled**. No Cloudflare token has
ever been written to `.env` or used by this session, so there is no risk of the
exposed value being mistaken for the live one here — nothing was stored either
way.

**My recommendation, and it is the same problem again:** the previous token was
burned by appearing in a chat transcript. Pasting the replacement into chat
exposes the replacement the same way. **Please add it to `.env` directly**:

```
CLOUDFLARE_API_TOKEN=<the real value>
```

I never need to see it. `scripts/deploy_testing.ps1` reads it from `.env` and
hands it to wrangler through the environment only — never a command line, never
a log, never echoed. Say the word once it is in place and I will deploy.

## THE BUILD IS FIXED AND VERIFIED — this was the real blocker to reproducibility

`build_deploy.py` works. Committed, with `vendor/three` (1.1 MB, six files, no
npm install needed). `build_full.py` retired to `_to_delete/` — moved, not
deleted, per rule 1.

**It was authored against an older layer, so a clean exit was not evidence.**
Rebuilt against the layer actually on disk and compared to the previously
shipped page:

| | previous | rebuilt |
|---|---:|---:|
| bytes | 1,505,359 | **1,513,790** (+8,431) |
| `id="cc-kb"` | 1 | 1 |
| `id="cc-kb-tab"` | 1 | 1 |
| `cc-ship::after` | 1 | 1 |
| `keybinds.html` | 0 | 0 |
| `CC_EMBED` | 5 | 5 |

477 files, 235 `.glb` — models untouched. Every marker the order requires is
present. The +8,431 bytes is the newer layer content being picked up, which is
the expected direction.

No assert fired. It also reported `unmatched: 6` — 85X, Arrastra, Fury, Mantis,
Merchantman, PTV. **The same six ships the auditor layer reaches independently.**

## Rule 12 on the build's own guards

A passing run does not show the asserts work. Proven in an **isolated fixture**,
so the shared `_layer.src.html` was never touched — another session edits that
file and this project has already had a near-miss there.

| case | result |
|---|---|
| control, unperturbed fixture | exit 0, `index.html` written |
| perturbed — one of the three CDN script tags removed | **AssertionError line 63, exit 1, NO `index.html` written`** |

So it fails loudly and writes nothing when the layer drifts out of step, which is
exactly what the order required and what a passing run could not establish.

**A near-miss in my own test, worth recording.** The first perturbation attempt
crashed on a Python 3.11 f-string backslash error, so the layer was never
modified — and the build then correctly succeeded. My harness printed
"SILENT SUCCESS, BAD". It was not: the precondition had failed, not the build.
**A test that fails to set up its own precondition reports the wrong verdict**,
and the only reason it was caught is that the perturbation step printed its own
before/after counts instead of assuming it had worked.

## A stale `.git/index.lock` appeared and blocked a commit

0 bytes, created 22:07:26, **12 minutes stale**, with **no `git`, `git-lfs`,
`gitk` or `git-gui` process running** — verified before touching it. Moved to
`_to_delete/stale_git_locks/` rather than deleted, per rule 1.

Notable because the original Path C brief predicted exactly this file and it was
**not** present then. It is now, and it is not mine as far as I can tell — most
likely a concurrent session's git operation that died. Worth knowing that
something in this repo is leaving locks behind.

## Still flagged, not fixed

`build_portable.py` retains **5** `/home/claude` references and cannot run on
this machine either. Outside this order. `build_machine_layer.py` is clean.

## What remains, all of it token-dependent

The deploy, both URLs, the second-deploy URL-stability check, and the served
verifications — `index.html`, `id="cc-kb"`, `cc-ship::after`, **a real model
file**, and the password gate from a clean context. Plus `CURRENT-STATE.md`,
which does not exist anywhere in the repo and which I will create once there is
a URL to record.
