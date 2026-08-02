# CLOSING UPDATE — final push before the machine is disassembled

**Nothing is in flight. Nothing is half-finished. Stopping here.**

## THE CHECK THAT MATTERS

```
git rev-parse HEAD origin/main
a32b8a3bc8ed45221fa13d3b79ed08badcdecbb3
a32b8a3bc8ed45221fa13d3b79ed08badcdecbb3
```

**Same hash twice. The push landed.**

## The brief's file count was stale — 16, not 63

It said 51 modified / 12 untracked. The working tree held **3 modified and 13
untracked**, and `HEAD` already matched `origin/main` at `7a72733` with nothing
landed after it. The larger figure was taken before the last three commits.
Saying so rather than quietly working to the smaller number.

## Committed — `a32b8a3`

`RECOVERY.md`, `data-layer/ship_resolution.json`, the editions/paints
acquisition finding, four work orders (front-end build plan, loadout real-data,
**loadout reader** — that one was not on the list but is a work order in `docs/`
and belongs), the three `20260802_09*` handoff entries, and the running handoff
record.

Nothing was outstanding under `checks/`, `scripts/` or
`data-layer/external-source-*` — all already committed earlier today.

## EXCLUDED — verified, not assumed

| file | why |
|---|---|
| `_c1_verify_wo.py` | one-off probe, 3.8 KB |
| `rescale_run_output.log` | 183 KB console output; its only unique content (four chassis cross-references) is already on disk in each ship's `MODEL_SOURCE.txt` and in the archived handoff entry |
| `testing/_src/_modelfolders.txt` | **checked against every build script — referenced by none** |
| `testing/_src/_scunpacked_names.json` | same; both are scratch, not build inputs |

The two `_src` files sit in a source directory, so I grepped the build code
before excluding them rather than trusting the label. Neither is read by
anything.

## MOVED ASIDE — not deleted, per rule 1

`testing/_deploy_lite/` → `_to_delete/deploy_lite_unclaimed_20260802/`
**245 files, 6.1 MB, referenced by no script, no config and no page.** Still
nobody's and still ungenerated, so it does not enter history.

Also cleared a **second stale `.git/index.lock`** — 0 bytes, six minutes old, no
`git` process of any kind running. Moved aside, not deleted. **That is the
second one today**, and something in this repo is not cleaning up after itself.
Worth knowing before the next session starts.

## Built from current source — verified by rebuild, not by mtime

| file | status |
|---|---|
| `testing/_deploy/index.html` | **rebuild is a byte-for-byte no-op** — `82271923…` before and after |
| `testing/_layer.html` | same mtime, same build pass |
| `testing/index.html` | same build pass — but see below |

**`testing/index.html` cannot be byte-verified.** `testing/build.py:26` injects
a UTC timestamp on every run, so it differs on each build by construction. Its
currency is established by mtime and by the layer it was built from, not by
hash. Stating that rather than implying a check I did not perform.

## The offsite copy was stale — found and fixed

The Cloudflare site served fine (200, `Hammerhead.glb` intact with a valid glTF
header), **but the bytes it served did not match the local build**:
served `be79501e…` against local `82271923…`.

That matters precisely because this is the offsite copy of the 349 MB deploy
build and the machine is about to be taken apart for three days. A site that
serves is not the same as a site that serves the current build — the same
distinction as a command exiting 0 versus the work being done.

Redeployed. This was completing the stated purpose of the check, not starting
something new: one proven command, run four times already today, content-
addressed so unchanged assets are not re-uploaded.

## State at stop

- `HEAD == origin/main == a32b8a3`, 0 ahead, 0 behind
- working tree: only the four deliberately-excluded scratch files
- Cloudflare serving the current build as the offsite copy
- `.env` untracked, three secrets, **one machine, no backup** — unchanged and
  still the largest single risk across this gap
- the UEX token remains unrotated after its screenshot exposure
- the Cloudflare token arrived over chat twice and is in a transcript; rotate at
  leisure, nothing depends on the value

## Not started, deliberately

The rule 14 enforcement proposal (`docs/proposal-rule14-single-writer-enforcement.md`)
is written and committed but **not implemented**, as instructed. It is the right
first thing to pick up, and it is a clean starting point rather than a
half-finished one.
