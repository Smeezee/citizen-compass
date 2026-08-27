# PROMPT FOR CODE — plan B: deploy the Worker, publish the version feed, and make the bucket emptiable.

    from    C1, 2026-08-15
    for     Code
    status  GO-AHEAD. Sleven picked B and created the bucket himself.
    order   1 of 2. The other is the on-machine reader (plan D), filed
              alongside this as prompt-code-onmachine-reader-2026-08-15.md.
              Do B first — D depends on nothing here, but B is what makes the
              collector useful to a second person this week.

---

## 0. Where this stands

**Sleven has created the R2 bucket.** Confirmed by him in session:

```
account   Citizencompass.co...  (ad974500ce73c9694e94213c4d762f3e)
bucket    collector-uploads     Standard, Automatic location, Eastern North America
```

Everything else in the upload path was written on 2026-08-10 and has never run:
`upload.go` (`SendExport`), `collector-receiver.worker.js`, `deploy-receiver.ps1`.
`send_url` and `send_key` in `collector-settings.txt` are still blank, so nothing
has ever been sent anywhere.

**The plan, in Sleven's words:** pictures upload, he reads the prices off them,
then they get deleted. Free tier holds. Full reasoning in
`docs/DECISION_screenshots-are-internal-only-2026-08-13.md`.

## 1. Deploy the Worker

Use the existing `collector-receiver.worker.js` and `deploy-receiver.ps1`. Bind
the Worker to `collector-uploads`.

- **Dry run first**, then deploy, then verify the deployment by fetching it back
  rather than by trusting exit 0. That mistake has silently published to a second
  URL five times in this project's history.
- **Never `wrangler pages deploy`.** This is a Worker.
- **Report the Worker's URL back.** Sleven needs it for `send_url`, and he cannot
  finish his part without it.

## 2. UPLOAD_KEY — hand him the command, do not invent the value

The key is Sleven's to generate and it must never pass through a chat window or
a log. Give him the exact command to run and let the prompt take the value:

```
wrangler secret put UPLOAD_KEY
```

**Do not put a key in a file, a commit, or a report.** If the Worker needs a
placeholder to deploy, make it fail closed — refuse uploads when the secret is
unset rather than accepting them.

## 3. The key can ADD only. Verify that, do not assume it.

This is already the design and it is the part worth testing rather than trusting:
the key lives in a text file on other people's machines, so one will leak
eventually. A key that can only upload costs junk in a bucket. A key that could
also read hands every contributor's data to whoever found it.

**Prove it:** with a valid key, attempt a list, a read and a delete through the
Worker. All three must be refused. Report what you actually observed, not what
the code intends.

## 4. Publish the version feed — this is what unblocks the other two machines

`update.go` is complete: it checks a feed, tells the operator, installs on a
click, verifies SHA256 before running anything, and handles the Windows
can't-overwrite-a-running-exe problem by renaming. **It is pointed at a file
that does not exist:**

```
https://raw.githubusercontent.com/Smeezee/citizen-compass/main/releases/collector-latest.json
```

Create `releases/collector-latest.json` with the real values for the current
build — version, url, **the actual SHA256 of the exe you publish**, and notes.
`collector-latest.json.EXAMPLE` shows the shape.

**The checksum is not paperwork.** This is the one path in the whole program that
downloads a file and then runs it as the collector. A release with no checksum,
or a wrong one, must abort without touching anything.

**Sleven's friend's machine is stale and his wife's is one version behind.** This
file is what makes them announce an update instead of drifting. Report where you
host the exe itself, since the feed's `url` has to point somewhere real and
`gh`/releases are still not authorised.

## 5. Make the bucket emptiable — the part B actually depends on

B only works if the pictures come out again. Right now nothing removes them, and
10 GB is roughly 3,400 frames at ~3 MB each.

Build Sleven a way to **pull down what has arrived and then clear it**:

- Downloads everything in the bucket to a local folder
- **Verifies each file landed before removing the remote copy** — same discipline
  as `clear_after_send`, which already refuses to erase anything the server has
  not confirmed
- Reports counts and bytes both ways
- **Never deletes something it did not successfully fetch.** A half-finished pull
  leaves the bucket exactly as it was.

Deletion from the bucket is a real destructive step, so it is **opt-in with a dry
run first** (rule 5), the same shape as `scrub_sidecars.py --apply`.

## 6. What NOT to do

- **Do not build any OCR, reader, atlas or vocabulary here.** That is order 2.
- **Do not publish a GitHub release or install `gh`.** Still not authorised.
- **Do not make the bucket public.** It is private by default; leave it.
- **Do not put the key anywhere except Cloudflare and, by Sleven's own hand,
  `collector-settings.txt`.**
- **Do not `git add -A`.** Stage by explicit path.

## 7. Acceptance

1. Worker deployed, URL reported, verified by re-fetching.
2. With the secret unset, an upload is refused. With it set, an upload succeeds.
3. List, read and delete through the Worker are all refused with a valid key —
   observed, not inferred.
4. A real export from Sleven's machine lands in `collector-uploads`, and the
   local copy clears only after the server confirms it.
5. `releases/collector-latest.json` exists, carries a real SHA256, and the
   collector's own update check finds it and offers the update.
6. A deliberately wrong checksum aborts the install and leaves the existing exe
   untouched.
7. The pull-and-clear tool round-trips: files down, bucket empty, counts match,
   and a dry run changes nothing.

## 8. Report back

- The Worker URL, and the exact two lines Sleven must paste into
  `collector-settings.txt`.
- Where the exe is hosted for the feed's `url`.
- What you observed on the read/list/delete refusals.
- Anything in §5 you think is unsafe. That step deletes Sleven's only copy of
  data that has already left his machine, and it is the one place here where
  getting it wrong loses something.
