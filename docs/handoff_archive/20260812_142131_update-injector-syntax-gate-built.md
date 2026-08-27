# Update — the injector now refuses to ship invalid JavaScript. Proven by breaking it.

Built. **Not pushed, not deployed** — the earlier go-ahead covered the batch I
already shipped as `4ecbbbb`; this guard came after it and has none of its own.

## What it does

A syntax gate in `inject_engine.py`, running **before the first write**.

The blast radius is why it matters: this script is the single writer of the
device panel and copies `device_engine.js` into **both** hosts in one step, so a
bad payload becomes a syntax error on the keybind page *and* the homepage
simultaneously — and on the homepage that is the site's own layer script, not
just a panel. The existing marker checks refuse a structurally wrong input; they
had no opinion on whether the payload was valid code.

## Acceptance, all three measured

**1. Broken input refuses, and touches nothing.** Planted an unterminated string
literal, ran the injector:

```
device_engine.js IS NOT VALID JAVASCRIPT - nothing was written.
  device_engine.js:65
  var BROKEN="unterminated;
             ^^^^^^^^^^^^^^
Both hosts are untouched. Fix the source and run again.
EXIT CODE: 1
```

Checked by **mtime and md5**, not by the message:

```
keybinds.src.html  mtime UNCHANGED  md5 UNCHANGED
_layer.src.html    mtime UNCHANGED  md5 UNCHANGED
```

**2. Restored, normal operation, output unchanged.** Confirmed.

**3. node absent → FAIL CLOSED**, tested by running with node off PATH rather
than reasoning about it:

```
NODE NOT ON PATH, so device_engine.js could not be syntax-checked.
Refusing to inject rather than copy unchecked JavaScript into both hosts.
This is a deliberate fail-closed: a guard that quietly skips itself is worse
than no guard, because it manufactures confidence.
EXIT CODE: 1
```

**Chosen deliberately over warn-and-continue.** Warning would reproduce exactly
today's failure while appearing to have a guard — rule 12's "a check that cannot
fail is not a check". node is already a build dependency here (`roundtrip.js`
and `mutate.js` run under it), so this adds no new tool, only a new moment it is
required.

## §3, the post-injection check — NOT built, and why

C1 suggested also checking the hosts after splicing, to catch a marker landing
mid-expression. I did not, and it is a judgement worth stating rather than
silently skipping:

The injected region is byte-identical to a file that has just been proven valid,
so a bad splice can only come from the **boundary markers** being wrong — and
those are already guarded four ways (start marker, end marker, exactly one of
each per host, END-after-START). Adding a second check of the same property
looked like coverage without new information.

C1's warning about the `<script type="application/json">` blocks is real, by the
way — those carry `__BUILD_INJECTS__` placeholders and a naive check reports them
as syntax errors. That is precisely the sort of false alarm that trains people to
ignore a gate, which is another reason not to add one that says nothing new.

**If a real bad-splice case ever turns up, that reasoning is wrong and the check
should go in.** Recording the argument so it can be overturned by evidence rather
than re-derived.

## State

Build and guard clean, `roundtrip.js` ALL CHECKS PASSED, `mutate.js` 19/20 M18.
Ready to push on a go-ahead.
