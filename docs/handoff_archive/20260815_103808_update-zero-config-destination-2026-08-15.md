# Update: zero-config destination built; feed publish needs Sleven's hands

## §2 - my honest answer on publishing the token

**Broadly right. One factual correction, one change to the order of operations.**

Right: once the token sits in plaintext on every contributor's disk its security
value is already near zero; add-only with list/read/delete refused means a leak
costs junk in a bucket; and rotation-via-feed is a real operational win. Treating
it as a **revocable channel identifier** rather than a secret is a legitimate
pattern.

Wrong: *"publishing changes the timeline, not the exposure."* Public repos are
continuously scraped by automated secret harvesters, and **git history is
permanent**. This converts "one contributor might leak it eventually" into
"harvested within minutes, guaranteed, and never unpublished". Rotation makes the
old value useless; it never makes it unpublished.

That does not block the design - it means **the Worker had to be hardened BEFORE
the token goes public**, not after. Done, and it does not conflict with the
sequencing: the constraint was feed-before-0.3.1, not feed-before-everything.

## The Worker now earns its keep - observed, 19/19

Hardened and deployed (version `cf3ecb99`). `MAX_BYTES` was **512 MB with no rate
limit at all** - unbounded cost on Sleven's account the moment the key is public.

| control | value |
|---|---|
| size ceiling | 64 MB, **refused on Content-Length before the body is read** |
| size floor | 256 bytes |
| per-install rate limit | 12/hour |
| storage brake | 6 GB total, 507 + "run pull_and_clear" |
| shape | install id, version, sha256 all required and format-checked |
| list/read/delete | still refused |

The new limits sit *behind* the key check, so they cannot be exercised against
production without the real key - which I must not have. Ran them against a local
instance with a throwaway key, same code: **19/19**, including 405 on
GET/HEAD/DELETE/PUT, 403 wrong key, 400 junk install / junk version / missing
hash, 415 non-zip, 409 hash mismatch, 413 oversize, 429 on the 13th upload, and
the negative control that a *different* install is still served.

Two of my own probe faults on the way, both worth recording: the fixture zip was
251 bytes - under the 256-byte floor - so every check below it measured a
different refusal than it claimed; and re-using one install id meant a previous
run's uploads counted against the rate limit, so everything came back 429.
**Leftover state from an earlier run is not a result about this one.**

## The collector

`destination.go` + `destination_selftest.go`. Precedence: local -> feed ->
cached -> nothing. **15/15 checks, each with a negative control.**

The rule with no error path, called out because nothing would have caught it:
**a locally configured URL never borrows the feed's key.** Filling a local
endpoint's blank key from the feed would post the shared token to whatever
address that machine named - a tester's laptop, or a typo.

§3 is done: a local-only zip now says *"Saved X on this computer. It was NOT sent
anywhere"* instead of "Saved X", which is what a successful send also looked like.
And the first time a feed-supplied address is used, it says where it came from.

`selftest PASS`.

## A release would have un-configured everybody

`make-release.ps1` rebuilds the feed from scratch. Cutting 0.3.1 would have
**deleted send_url/send_key**, and every machine taking its destination from the
feed would have gone quietly back to writing zips to its own disk - days later,
on somebody else's computer, with nothing in the release output connecting it to
the release that caused it. It now carries the destination forward and **fails
the release if it did not survive the write**.

## BLOCKED: the feed publish needs Sleven, by design

§1 requires the key in a file I write. The standing instruction is that the key
is his to type and never mine to see. Rather than pick one, `publish-destination.ps1`
resolves both: **one prompt, no echo**, and the same value goes to Cloudflare
*and* into the feed, so the two cannot drift apart - which matters, because if
they ever disagree every collector is refused with 403.

    cd citizen-collector
    powershell -ExecutionPolicy Bypass -File .\publish-destination.ps1            # dry run
    powershell -ExecutionPolicy Bypass -File .\publish-destination.ps1 -Publish

It sets the secret first, writes the feed **BOM-free**, reads the bytes back to
confirm no `EF BB BF`, parses it, checks the values survived, pushes one path,
and fetches the published file back over the network.

Rotation procedure: `docs/ROTATING-THE-UPLOAD-KEY.md`.

## Not done, waiting on that

Commit of the restart-handover fix and cutting 0.3.1 are held until the feed is
live, per the stated sequencing. Nothing is committed.
