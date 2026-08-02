# UPDATE — token stored; the auth question answered; worker-name mismatch caught

Filed per rule 13. Deploy is running as this is written; results follow in a
separate update.

## CREDENTIAL — written, never echoed

`CLOUDFLARE_API_TOKEN` is in `.env`. Before writing, `.env` was re-confirmed
**untracked and absent from HEAD *at write time*** — not relying on the check
from earlier in the session. Appended, not overwritten, and the script refuses
to clobber an existing key.

Verified afterwards **by key name and length only**: `DATABASE_URL` 78,
`UEX_API_TOKEN` 40, `CLOUDFLARE_API_TOKEN` 53. The value has never been printed
by me, and `.env` remains gitignored and unstaged.

**ROTATION NOTE, as requested:** an earlier value of this token was exposed in a
chat transcript and was **rolled before first use**. No Cloudflare credential was
ever written to `.env` or used before this one — the two earlier attempts both
arrived as the literal placeholder `<TOKEN>` and were correctly refused rather
than written. So **the exposed value was never live here**, and nobody should
mistake it for the working credential.

**Said once and then dropped:** this replacement also arrived over chat, so it
now sits in a transcript too. Rotate it whenever convenient; nothing in the
tooling depends on the specific value.

## THE AUTH QUESTION — answered by evidence, and the answer is "no"

You suspected `wrangler login` had stored an OAuth credential outside `.env`.
**It had not.** Established before the token was written:

- **No credential store.** The real config dir is
  `AppData\Roaming\xdg.config\.wrangler`, and it contained **no
  `config/default.toml`** — where an OAuth login would live. `~/.wrangler` and
  the other candidate paths did not exist at all.
- **No `CLOUDFLARE_*` or `CF_*` environment variables.**
- **Only three wrangler invocations ever logged on this machine**, all from this
  session, two of them `whoami`. No `login`, no `deploy`, no upload.

So the site already serving at
`citizencompasstesting.citizencompass-contact.workers.dev` **was not deployed
from this machine.** It came from elsewhere — the dashboard, or another machine.
The token genuinely was needed; it was not being demanded unnecessarily.

`deploy_testing.ps1` now accepts both routes anyway, as asked: it asks wrangler
itself whether it is authenticated and only falls back to the `.env` token if
not. Checked **by behaviour** rather than by looking for a credential file,
because that file's location has moved between wrangler versions and an absent
file is not proof of an absent credential.

**A defect in my own diagnostic, found by running it.** On the real deploy the
script printed *"wrangler is already authenticated … no .env token needed"* —
which is **wrong**. Wrangler v4 loads `.env` from the project directory itself,
so the token I had just written is exactly what authenticated it. The dual-path
logic works; the message misattributes why. Left alone mid-deploy rather than
edited under a running upload; being corrected immediately after.

It is worth being clear this does not undermine the finding above: the
`whoami` that reported *not* authenticated ran **before** any token existed in
`.env`, which is precisely what rules out a stored OAuth credential.

## A WORKER-NAME MISMATCH THAT WOULD HAVE PUBLISHED A THIRD URL

The live worker is **`citizencompasstesting`** — the Worker name *is* the
subdomain. My `wrangler.toml` said **`citizen-compass-testing`** (hyphenated).

Deploying that would have created a **second Worker** at
`citizen-compass-testing.citizencompass-contact.workers.dev`, left the live
testing site untouched, **and reported complete success.** A third address in
circulation, self-inflicted, in the middle of an order whose whole Correction 2
is about two URLs being one too many. Corrected to match before deploying.

This is the same shape as the models-folder case: the command succeeds, the
output looks right, and the thing you cared about did not happen.

## YOUR THREE FILES — verified, and one orphan of mine removed

All three SHA-256 hashes **MATCH**, checked twice and again immediately before
upload. Markers confirm your account exactly: `id="cc-kb"` 1, `cc-ship::after`
2, `keybinds.html` 0, `cc-rel` 9.

**Rule 8 check on the git restore** — disclaimer text is intact and identical to
the preserved known-good: `trademark` 11, `Roberts Space Industries` 38,
`Cloud Imperium` 10, `not affiliated` 3, `unofficial` 4. Nothing was lost in the
restore.

I removed a stale `keybinds.html` that **my own** earlier rebuild had left in
`_deploy/`. Your page references it zero times, so it would have shipped as an
unreachable 25 KB orphan. Moved aside, not deleted; `index.html` hash unchanged
afterwards. Payload: **477 files, 347.2 MB, 235 `.glb`**.

**I did not run `build_deploy.py` before deploying** — it would have overwritten
the exact bytes you checksummed. Deploying your verified artifact, not a rebuild
of it.

## On the stale-transfer incident

No apology needed. A transfer that reports the correct byte count **and** a fresh
timestamp while serving stale bytes defeats the mtime check I was told to run —
the check reports a property it is not actually measuring, which is the same
failure class as everything else caught today. Your checksums are what caught
it, and that is why I re-verified them rather than trusting my earlier read.
