# PROMPT FOR CODE — `inject_engine.py` will ship syntactically invalid JavaScript into both hosts without noticing

    from    C1, 2026-08-12
    for     Code
    basis   your own words, mid-build today: "I broke device_engine.js — the
              \\n became real newlines inside a JS string literal, and the
              build shipped it because inject_engine.py doesn't syntax-check."
    scope   testing/_src/inject_engine.py. Small, and worth doing before the
              next injected-block edit rather than after.
    size    small — do it alongside whatever else is in flight, not as its
              own pass.

---

## 1. Why this is worth a guard rather than more care next time

`inject_engine.py` exists to be the **single writer** of the device panel, and
it does that job. But it copies `device_engine.js` into two host pages —
`keybinds.src.html` and `_layer.src.html` — with no check that what it's
copying is valid JavaScript.

**So a syntax error in `device_engine.js` becomes a syntax error on the keybind
page and the homepage simultaneously, in one silent step.** The blast radius is
both pages, and the failure mode is the whole inline block failing to execute —
which on the index means the site's own layer script, not just the device panel.

You caught it this time because you were looking. The guard makes that not
depend on anyone looking.

Note what the existing guards already do and don't cover: the script hard-fails
if `device_engine.js` no longer starts or ends with the boundary markers, and if
a host has the wrong marker count. So it already refuses to run on a
*structurally* wrong input — it just has no opinion on whether the payload is
valid code. That's the gap, and it's a small one to close.

## 2. The guard

**Before writing to any host**, syntax-check `device_engine.js` and **exit
non-zero without touching a single file** if it fails. Fail closed, and fail
before the first write — a half-injected pair of hosts is worse than a refused
build, and the script's own `HOST MISSING` check already takes that position
("refusing to half-inject").

`node --check <file>` is the obvious mechanism and node is already a build
dependency here — `roundtrip.js` and `mutate.js` both run under it.

**Handle node being absent deliberately, and say which you chose:** either fail
the build, or warn loudly and continue. Silently skipping the check is the one
option that isn't acceptable, because it recreates today's failure while
appearing to have a guard.

## 3. Worth considering, your call

Checking the **hosts after injection**, not just the source, would also catch a
bad splice — a marker landing mid-expression, say. That's a different failure
than a bad payload and the boundary-marker checks don't fully rule it out.

If you do this, note that both hosts carry `<script type="application/json">`
blocks holding build placeholders like `{"__BUILD_INJECTS__":"..."}`. **Those
are JSON, not JavaScript, and a naive check reports them as syntax errors.** I
know because I just did exactly that and nearly filed it as a bug. Filter on
the `type` attribute, or check only the injected region.

## 4. Acceptance

1. Deliberately break `device_engine.js` (an unterminated string is enough), run
   the injector, and confirm it exits non-zero and **neither host is modified** —
   check mtimes, not just the message.
2. Restore it, run again, confirm normal operation and unchanged output.
3. State what happens when node isn't on PATH.

## Commands

```
node --check testing/_src/device_engine.js
```

```
python testing/_src/inject_engine.py
```
