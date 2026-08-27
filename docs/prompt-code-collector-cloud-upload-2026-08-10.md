# PROMPT FOR CODE — turn on the collector's cloud upload. The code is already built; only the endpoint is missing.

    from    C1, 2026-08-10
    for     Code
    basis   Sleven: "we need to figure out the collector how can people send
              their information in by just clicking one button. and then it
              auto erases their information so that we know that it's clean so
              we don't get repeat information every single time."
    scope   citizen-collector/ only, via inbox/ per the 2026-08-09 ruling.
    note    Run this AFTER the website queue
              (`prompt-code-MASTER-clear-the-queue-2026-08-10.md`). That one is
              blocking Sleven's testing; this one is not.

---

## 0. The feature Sleven is asking for already exists. Do not rebuild it.

**Verified by reading the source, not assumed.** Every part of what he described
is built and wired:

| what he asked for | where it already lives |
|---|---|
| one button | `ui.go` — `send` / `sendchoice` (Data only / Include screenshots / Cancel) |
| sends to the cloud | `upload.go` — `SendExport`, sets `X-Collector-Key`, `X-Collector-Sha256`, `X-Collector-Install`, `X-Collector-Version` |
| verified it really arrived | `collector-receiver.worker.js` — computes its **own** SHA256 over the bytes that actually arrived, refuses with 409 on mismatch, confirms only after the R2 write resolves |
| then erases the local copy | `clearAfterSend`, default `true` — `main.go:657` → `ui.go:406` → `upload.go:193`, and it only fires after the server's hash matches |
| no repeat information | sent-rows tracking — a resend carries only what is new. `sent_rows_selftest.go` includes a *resurrection* check, i.e. a test that already-sent rows do not come back |

**The only thing missing is two blank lines** in `collector-settings.txt`:

```
send_url =
send_key =
```

So this order is infrastructure, not feature work. **If you find yourself
writing upload logic, stop — you have misread the task.**

## 1. What you can do, and what is Sleven's

**Sleven's, because they are account-level and involve a secret:**
creating the R2 bucket, creating the `UPLOAD_KEY` secret, and pasting the URL +
key into `collector-settings.txt`. He has a separate dead-simple guide for this.
**Do not ask him for the key and do not accept it if it appears in a transcript
— he already has three exposed tokens outstanding.**

**Yours:**

1. **Write the `wrangler.toml`** (or equivalent config) for the receiver Worker.
   The Worker source is `citizen-collector/collector-receiver.worker.js` and it
   is finished — **do not edit it.** Its own header comment is the deployment
   spec; read it first. The two bindings it requires, by exact name:
   - `BUCKET` — the R2 bucket binding
   - `UPLOAD_KEY` — a secret, **never** a plaintext var in the config file
2. **Confirm the route shape.** The worker's header says settings should hold
   `send_url = https://<worker>.workers.dev/upload`, but the fetch handler
   itself does not branch on path — it accepts any POST. Decide whether to route
   `/upload` explicitly or accept the root, **say which you chose and why**, and
   make sure the value Sleven is told to paste matches what actually answers.
3. **Do the deploy only once Sleven has created the bucket and the secret** —
   deploying against a missing binding fails in a way that looks like a code
   problem and is not.
4. **Verify with a real round trip, not a status code:** post a small real
   export, confirm 200 with `ok:true`, confirm the object exists in the bucket,
   and confirm the returned `sha256` matches the client's local hash. Then
   confirm the collector actually cleared its local copy — and, separately,
   that a deliberately corrupted/truncated upload gets a 409 and the local copy
   is **still there**. That second case is the one that matters; the whole
   design exists so that failure direction is safe.

## 2. Two properties that must survive this, and are easy to break

- **The endpoint is upload-only on purpose.** There is no list, read, or delete
  route, and none may be added — not even a "just for admin" one. The key sits
  in a settings file on someone else's machine, so it must be assumed public
  eventually. A write-only key that leaks costs junk storage; a read-capable one
  leaks every contributor's data. This is stated in the worker's own header;
  it's a design decision, not an oversight.
- **`clearAfterSend` must never fire on an unconfirmed send.** If you touch
  anything on that path, re-run the selftests. The failure mode being guarded
  against is a contributor losing their only copy of data that never arrived.

## 3. What NOT to do

- Do not edit `collector-receiver.worker.js`.
- Do not add any read/list/delete route.
- Do not write the key into `wrangler.toml`, a comment, a log line, or a commit.
- Do not put a real `send_url`/`send_key` into a committed
  `collector-settings.txt` — those are per-install values.
- Do not build a new upload path, retry queue, or dedup layer. All three exist.
- Nothing commits or pushes without Sleven's go-ahead.

## 4. Report back

The config you wrote, the route decision and why, the round-trip result
(including the deliberately-corrupted case and confirmation the local copy
survived it), and confirmation the deployed endpoint has no read path.

## Commands

```
cd citizen-collector
```

```
npx wrangler deploy
```

```
.\collector.exe --selftest
```
