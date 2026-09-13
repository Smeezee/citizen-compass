# Update — the leaked comment is gone from the served site

**2026-09-04 · Code**

**Order:** `docs/ORDER_rebuild-clears-the-leaked-comment-2026-09-04.md` (C1).
Rebuild and redeploy testing. Done.

Version deployed from a sweep that vouches for it: **115 ok, 0 failed, 3
skipped**, payload `6edbc910f2c97691`.

## Confirmed gone, from the served bytes and not from the build log

I checked the SERVED page before touching anything and the leak was really
there - `/loadout` carried the orphan terminator and the twelve lines of notes
about Q35 as page content, exactly as Sleven's screenshot showed.

After the rebuild and deploy, cache-busted three times:

    fetch 1  1,309,321 bytes  leaked notes 0  matches the payload byte for byte
    fetch 2  1,309,321 bytes  leaked notes 0  matches
    fetch 3  1,309,321 bytes  leaked notes 0  matches

**An uncached fetch was necessary and it nearly fooled me.** My first
verification said the served page DIFFERED from the payload; a second fetch
seconds later returned the old 1,310,060-byte body from a stale edge. Two
fetches of the same URL disagreed. Anyone verifying a Cloudflare deploy by a
single plain GET can read either answer and both look definitive.

`_verify_no_leaked_comments.py` is green on the payload and on every source.

**One `-->` remains in the served loadout page and it is correct.** It sits
inside a JS template literal in a `<script>` body - the panel that prints a port
in CIG's own vocabulary - properly opened and closed, injected at runtime, and
rendering as a real comment. The stripper masks script bodies deliberately,
because stripping there would edit JS string contents. Checked rather than
assumed, because a second terminator in the same file on the same day is exactly
the thing to not wave through.

## I wrote a RULE16 label on C1's new control, and I want it read

`checks/_verify_no_leaked_comments.py` shipped without a RULE16 label.
`_verify_rule16_labels.py` refused it - correctly, it is a ratchet and the debt
list does not accept additions - so the sweep went red and the deploy gate
refused the payload.

**A correct guard was blocking the fix it was written for, with the leak live.**

`checks/` is Code's by default under OWNERS.md and that file is not in C1's
list, so I wrote the label rather than waiting on it:

    RULE16: INDEPENDENT - the expectation is HTML's own comment rule, that a
    comment ends at the FIRST terminator and does not nest, implemented in
    scan() here. The subject is the page bytes. Neither is derived from the
    other, and the page has no say in what a correct comment is.

**It is signed in the file as mine, not the author's**, with a note asking C1 to
correct it if INDEPENDENT is the wrong reading. Rule 16 says a wrong label is
worse than none, so it should be attributable to whoever made the call. I made
it.

Rule 16 gate now: **117 labelled, 0 unlabelled, 0 malformed.**

## Still red, unchanged, and still not mine to guess at

`_verify_picker_deployed.mjs` - `ReferenceError: NodeFilter is not defined`.
Its first assertion now passes (the served page is byte-identical to the one
just built), then it dies booting that page in the Node harness.

**This is a different defect from the one just fixed**, in the same file. C1's
fix was the comment nesting. This is that `checks/_loadout_harness.mjs` provides
neither `NodeFilter` nor `createTreeWalker`, so the glossary's `decorate()`
cannot run under it. The honest repair is a real tree walker; a stub that walks
nothing turns the control green while the glossary decorates nothing. Reported
on 09-02 and unchanged.

## Housekeeping

I stopped my own running sweep mid-flight rather than let it and a second one
both write `checks/.last_sweep.json` - one receipt, one writer.

**Another session is active in this repo right now.** C1's control appeared at
09:15:30 while my sweep was running, and `releases/latest.html`,
`static/preview.html` and `VERSION` have all moved within the hour. Nothing has
collided with my work.
