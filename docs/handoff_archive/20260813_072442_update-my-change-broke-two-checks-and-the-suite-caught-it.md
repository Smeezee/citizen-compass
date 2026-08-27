# Update — my §2 change broke two existing checks. The suite caught it, I had claimed nothing, and both are now fixed.

Worth its own entry because the sequence is the point, not the fix.

## What happened

I reported §2 as built and said the full `-selftest` was still running and that
I would report its verdict **rather than assume it**. The verdict:

```
selftest FAIL (4 checks failed)
EXITCODE=1
409 ok, 4 FAIL
```

Two were the known, pre-existing `sent-rows` failures. **Two were mine:**

```
[FAIL] no interval setting -> the 60s default    sec=120 notes=[] err=<nil>
[FAIL] interval_seconds is honoured              sec=30 err=<nil>
```

Had I written "built, tests pass" on the strength of a clean `go build`, both
would have shipped.

## Why they broke, and why the first one was a badly-shaped check to begin with

**`no interval setting -> the 60s default`** asserted the literal `60`. That is
a test of a constant's value dressed as a test of the resolver — the name says
nothing about a specific number, but changing the default broke it. It now
asserts `sec == defaultIntervalSeconds`, which is what its name actually claims,
and a **separate** check pins the constant to 120 so changing the default is
still a visible, deliberate edit rather than a silent one.

Two questions, two checks. They were sharing one, and that is what made a
correct change look like a regression.

**`interval_seconds is honoured`** asserted `len(notes) == 0` — the absence of
the very note I added. It now asserts the note is present and says the right
thing, plus a negative control: a settings file that merely restates the default
must produce **no** note, or "this overrides the default" becomes a line that
appears whether or not it is true.

## The pre-existing pair, unchanged

```
[FAIL] sent-rows: first export carries the one pending row   rows=309
[FAIL] sent-rows: confirming marks exactly the exported row  marked=309
```

Still export-path, still held with §6, still only failing on a machine that has
Star Citizen installed. Not touched.

## The correction I owe my own earlier report

In the §2 update I wrote that I had not confirmed whether the suite exits
non-zero with failures present, and would not claim it either way. **Confirmed
now: it prints `selftest FAIL (4 checks failed)` and exits 1.** No silent
success there — the gate does what it says.

Re-running the full suite to confirm the two fixes land and nothing else moved.
I will report that verdict too rather than assume it.
