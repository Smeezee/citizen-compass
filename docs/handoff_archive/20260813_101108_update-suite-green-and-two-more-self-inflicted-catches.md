# Update — `selftest PASS`, 437 ok, 0 FAIL. Both of the last two failures were mine, and one of them was the same escape sequence twice.

```
selftest PASS
EXITCODE=0
437 ok, 0 FAIL
```

## 1. My negative control was a contradiction

```
[FAIL] NEGATIVE CONTROL: the encoded fixture really is escaped (no literal <)
```

A copy step collapsed the six characters `<` into a literal `<`, so the
assertion read `!contains("<") && contains("<")` - never true, in any universe.

**That is the second time this exact escape sequence has bitten me in this
pass.** The first was the guard itself, which could not see a real sidecar. So
the spelling now comes FROM the encoder:

```go
var escapedLT = func() string { b, _ := json.Marshal("<"); return strings.Trim(string(b), `"`) }()
```

Typing it out is what broke twice. Asking `encoding/json` how it spells `<`
cannot disagree with what `encoding/json` writes.

It failed loudly rather than passing, which is the right direction - but a check
that can never be true is not a check, and it would have sat there green-adjacent
forever if the suite had not been run.

## 2. Four staleness checks - fixed, cause NOT proven

They went red in the full suite and passed in isolation, which is the signature
of timing contention rather than a logic fault. **I did not prove my burst
ticker caused them** and I am not going to claim it: it did not reproduce when
`runGameLogSelftest` ran alone, with or without the ticker.

What investigating it DID find is a real defect worth fixing on its own merits:

**The 250ms burst ticker ran for the entire life of the process.** Eight wakeups
per poll, forever, to `continue` - when a burst is a few seconds of a session.

It is now created when a burst starts and stopped when one ends. A nil channel
blocks forever in a `select`, so the case does not exist when idle, and one
place keeps the fast clock in step with the burst so the two cannot drift.

The staleness checks are green now. **That is consistent with contention and
still not proof.** If they go red again the cause is elsewhere and I will keep
looking rather than attributing it to something already changed.

## Everything now built for the collector order

```
§1  location_inventory_name    ANSWERED       pushed 7d12ace
§2  in-world gate + 120s       BUILT          pushed b75a94a
§3  hotkey burst               BUILT          pushed 6dde2bd
§4  miner timing               NOTHING BUILT  pushed b75a94a
§5a unify the location paths   BUILT          NOT COMMITTED
§5c 394 sidecars rewritten     DONE           (data, not code)
§6  export guard               BUILT          NOT COMMITTED
    renderer in the sidecar    BUILT          NOT COMMITTED
    consent v3                 BUILT          NOT COMMITTED
    governing rule recorded    DONE           NOT COMMITTED
    sent-rows isolation        FIXED          NOT COMMITTED
    burst ticker on-demand     FIXED          NOT COMMITTED
```

Nine files, uncommitted:

```
citizen-collector/auto.go               consent.go        consent_selftest.go
citizen-collector/export.go             gamelog.go        gamelog_mine.go
citizen-collector/main.go               sent_rows_selftest.go
citizen-collector/leak_selftest.go      (new)
scripts/scrub_sidecars.py               (new)
```

## Two decisions still open

1. **Commit §5/§6 and the rest.** Rule 2 - no go-ahead this session for these.
2. **`includeCaptures`.** Screenshots are still opt-in in code. Consent v3 says
   pictures are part of what is sent, which is true when they are included. If
   sending should always include them, that is a code change I have not made,
   because quietly widening what gets uploaded is exactly what the consent
   version bump exists to prevent.

## Still unverifiable here

Acceptance 1 wants a grep of a fresh captures folder **after a real session**.
Everything above is fixtures from the archive plus a rewrite of the existing
folder. It needs the game played.
