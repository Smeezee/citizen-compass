# Rotating the upload key

**The upload key is published on purpose. It is not a secret, and nothing should
ever treat it as one.**

It ships in `releases/collector-latest.json`, which is a public file in a public
repository, so that a contributor never has to open a text file and paste a
51-character password. That trade was made deliberately on 2026-08-15. This page
is the other half of it: **the procedure that makes publishing safe is being able
to revoke.**

---

## What the key actually is

A **revocable channel identifier**. It says "this upload came through the current
channel". It does not prove who sent it and it never did — the moment the key
lived in a settings file on somebody else's machine, it stopped being a secret in
any useful sense.

What genuinely bounds abuse lives in the Worker, not in the key:

| Control | Value | Why |
|---|---|---|
| Size ceiling | 64 MB, refused on `Content-Length` | The largest real export seen is 27 MB. Refused before the body is read, so nobody can make the Worker buffer half a gigabyte just by claiming it is coming. |
| Size floor | 256 bytes | Under this it is not a truncated export, it is somebody poking. |
| Per-install rate limit | 12 uploads/hour | People play; they do not send twelve exports an hour. |
| Storage brake | 6 GB total | R2's free tier is 10 GB and Sleven pays for the overage. Refuses with 507 and says to run `pull_and_clear`. |
| Shape checks | install id, version, sha256 all required and format-checked | A real collector always sends all three. Anything that does not is not one. |
| List / read / delete | **refused, always** | There is no route that returns data. Verified every deploy. |

**A leaked key costs junk in a bucket, bounded by the table above.** It cannot
read anybody's data, because no route exists that could.

---

## Rotating it

Three steps, and every collector in the world follows within one check cycle.
**No rebuild, no reinstall, and nobody has to be told anything.**

### 1. Pick a new value

Anything long and random. It is an identifier, not a password, but there is no
reason to make it guessable.

### 2. Set it on the Worker

```
cd citizen-collector
npx wrangler secret put UPLOAD_KEY
```

Paste at the prompt. Cloudflare stores it; nothing local keeps a copy.

**From this moment until step 3 completes, every collector in the field is
refused with 403.** Their data is not lost — a refused send leaves the zip on the
contributor's disk and `clear_after_send` never fires. Keep the gap short.

### 3. Publish the same value in the feed

```
cd citizen-collector
powershell -ExecutionPolicy Bypass -File .\publish-destination.ps1 -Publish
```

It prompts for the key, writes it into `releases/collector-latest.json`, verifies
the file parses, and pushes. **The value is never printed, never logged, and
never passed on a command line** — command lines are visible to other processes
and land in shell history.

Collectors pick it up on their next update check.

---

## Verifying a rotation actually took

Do not trust "it pushed". Ask the things that have to be true:

```
# the feed is live, parses, and carries the new destination
curl -s https://raw.githubusercontent.com/Smeezee/citizen-compass/main/releases/collector-latest.json

# the old key is now refused (expect 403)
# the new key is accepted - test with a real export, not a hand-made one
```

`publish-destination.ps1` does the first two itself and refuses to report success
if the published file does not parse with a JSON parser.

**The BOM trap.** This file is written by PowerShell, and
`Set-Content -Encoding UTF8` on Windows PowerShell 5.1 prepends `EF BB BF`. Go's
`encoding/json` — which is what `update.go` parses it with — rejects a leading
BOM outright, and the file looks perfectly fine in any editor. It has already
broken this exact file once, on 2026-08-14. The script now writes with
`UTF8Encoding($false)` and reads the bytes back to confirm.

---

## When to rotate

- Anyone reports uploads they did not make
- The storage brake starts firing without an explanation
- A contributor leaves on bad terms
- Anything that feels off. It costs one command and a check cycle.

**Rotating does not remove the old key from git history, and nothing can.**
Rotation makes the old value useless; it does not make it unpublished. That is
understood and accepted — it is the reason revocation has to be this cheap.

---

## What must never change

- **Do not make the R2 bucket public.**
- **Do not add a list, read or delete route to the Worker.** The whole safety
  argument for publishing the key rests on there not being one.
- **Do not remove `send_url` / `send_key` from `collector-settings.txt`.** Local
  values always win; that is the escape hatch for a machine pointed somewhere
  else on purpose.
- **A locally configured URL never borrows the published key.** The pair comes
  from one source or the other, never mixed — otherwise a typo'd local address
  would receive the shared token.
