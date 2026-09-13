# Update — the watcher runs the amended guard, and the two halves now agree

**Filed 2026-09-09 22:00 CDT.** Job 1 of the boot memo, closed.

## THE OLD BINARY WAS PRE-AMENDMENT, AND THAT WAS PROVEN TWO WAYS

Not assumed from the build time:

    strings in the live binary   CC_ANTHROPIC_BILLING  absent
                                 "BILLING NOTICE"      absent
    logs/inbox_watcher.log:4132  21:05:51 "ANTHROPIC_API_KEY is set in this
                                 environment ... will not run WHILE IT IS"

That log line is the v1 PRESENCE wording in the live log, written by the binary
itself. **The detector was proven both ways before it was trusted** (rule 12):
`ANTHROPIC_API_KEY` in the same binary returns 1, a string that is in no binary
returns 0.

## THE GUARD WAS TRIPPED ON A TEST BINARY FIRST, AS THE STANDARD NOW REQUIRES

Built into `_needs_review/guardproof_20260909/`, whose own directory becomes its
project root — so **no case could reach the real inbox even on an allow**, which
matters because two of these cases are ALLOWED and an allowed watcher is a second
writer (rule 14). All six run against the built binary, not the source:

    key set, nothing declared      REFUSED  exit 78   the accident this exists for
    declared api, no key           REFUSED  exit 78   *** the discriminator ***
    declared "yes"                 REFUSED  exit 78   unrecognised, not guessed (r19)
    declared api + key set         ALLOWED            BILLING NOTICE in the log
    nothing set at all             ALLOWED            silent, correctly
    key present but EMPTY          ALLOWED            NOTE path

**The second case is the one that proves the swap was needed.** A presence-only
guard would have ALLOWED it. The amended one refuses it.

    refusal reached logs/inbox_watcher.log     yes
    planted value anywhere in that log          0
    leak-detector positive control              3   (it can find things)

Unit tests: `go test -count=1 ./pkg/apikeyguard/` — 7 pass, uncached.

## THE SWAP

    task stopped               process confirmed gone before anything moved
    old binary moved aside     _to_delete/2026-09-09_inbox_watcher_presence_guard/
    old sha256                 3c15544f15b62964...  (the 21:06 presence-only build)
    rebuilt                    go build -o ../inbox_watcher.exe .
    new sha256                 6b22ec29b1f11165...
    tripped test binary        6b22ec29b1f11165...  IDENTICAL

Byte-identical **and** reproducible: the live binary was built separately from the
one whose guard was tripped and came out the same bytes.

    task state    Running
    process       one pid, 8336, started 2026-09-09 21:58:19
    log           "Now watching for new files. Leave this running."
    since start   no refusal, no billing notice — correct, nothing is set here

Deaf window: about 40 seconds. This file arriving in `LATEST_HANDOFF.md` is the
end-to-end proof.

## STATE NOW — ONE GUARD, ONE BEHAVIOUR

    pkg/apikeyguard              refuses a MISMATCH
    Assert-DeclaredBilling.ps1   refuses a MISMATCH
    run_checks_scheduled.ps1     calls it.  LIVE.
    inbox_watcher.exe            refuses a MISMATCH.  LIVE.
    roadmap-watcher              still built from the pre-amendment package —
                                 SEE BELOW, it is the same defect one binary over.

## TWO THINGS FOUND ON THE WAY, NEITHER FIXED

**1. `roadmap-watcher` calls the same guard and has not been rebuilt.**
`roadmap-watcher/main.go:63` calls `apikeyguard.Enforce`. It is registered by
`setup_roadmap_task.ps1` and runs unattended every four hours. **If its binary
predates the amendment it is a third half of the same disagreement.** Not touched
— reported, because the boot memo named one binary and rule 25 says the assigned
job is the job.

**2. The guard's own header states a stricter contract than the guard keeps.**
`pkg/apikeyguard/apikeyguard.go` says:

    "API", "apikey", "yes", "1" and a trailing space must not quietly become
    permission

`Look()` lowercases and trims, and `apikeyguard_test.go:105` **deliberately
asserts** that `"api"`, `"API"`, `" api "` and `"\tApi\n"` are all accepted. I
confirmed it on the built binary: `CC_ANTHROPIC_BILLING='API '` with a key set
produced a BILLING NOTICE, not a refusal. `"apikey"`, `"yes"` and `"1"` are
correctly refused.

**The behaviour is tested and I believe it is the intended one** — rule 17 allows
a stated normalisation, and it is stated on the `Declared` field. **The prose is
what is wrong**, and prose that overstates a safety contract is the same family
as a check that cannot fail. It is one sentence in my own package and I have not
touched it: **say the word and I will correct the comment to match the tested
behaviour.**

## NEXT

Job 2 — the red case in `checks/_verify_api_key_guard.py`. **Already answered,
and the answer is that the case is real.** Detail in the next update.

Nothing committed.
