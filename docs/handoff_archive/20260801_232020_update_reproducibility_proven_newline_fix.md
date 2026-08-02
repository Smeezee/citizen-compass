# UPDATE — reproducibility PROVEN on this machine, after fixing a platform-dependent write

**Result: `build_deploy.py` now reproduces the deployed artifact byte-for-byte.
No deploy needed — the site is already current.**

```
before build : 62b22b7d1fdf83dfa5caf4045ceb1bd8e9e09d56d9a69e47e5f01e570d9207ea
after  build : 62b22b7d1fdf83dfa5caf4045ceb1bd8e9e09d56d9a69e47e5f01e570d9207ea
after  again : 62b22b7d1fdf83dfa5caf4045ceb1bd8e9e09d56d9a69e47e5f01e570d9207ea
deployed     : 62b22b7d1fdf83dfa5caf4045ceb1bd8e9e09d56d9a69e47e5f01e570d9207ea
```

## But the first run FAILED the test, and that was the finding

The prediction was that the hash would not move. **It moved** — to
`496d0ece…`, +8,473 bytes. Per the instruction I did not deploy, and diffed.

**Every build input was identical to yours**, so the inputs were not the cause:

| input | mine | yours |
|---|---|---|
| `releases/latest.html` | `60b576cb…` | `60b576cb…` |
| `testing/_src/_layer.src.html` | `45c4a7c7…` | `45c4a7c7…` (unchanged since I checksummed it) |
| models in `_deploy/models/` | 235 | 235 |

Same inputs, different output. So the build itself was not deterministic.

### The cause: `open(..., 'w')` translates newlines per-platform

`build_deploy.py:294` was:

```python
open(OUT+'/index.html','w',encoding='utf-8').write(out)
```

Text mode with the default `newline=None` translates every `\n` to `os.linesep`
on write — `\n` on Linux, `\r\n` on Windows. Your workspace wrote LF; this
machine wrote CRLF. **One extra CR per line across 8,473 lines = exactly the
+8,473 byte delta**, and a completely different sha256 despite
character-for-character identical content.

Proof it was only line endings: after `tr -d '\r'`, the two files are
**byte-identical by `cmp`**, and the normalised hash is `62b22b7d…` — the
deployed hash.

**Fixed** with `newline=''`, which writes `\n` through untouched so the output
is byte-identical on every platform.

### Why this mattered more than a cosmetic diff

A reproducibility claim that holds on Linux and fails on Windows is worse than
no claim. The hash comparison exists to prove the artifact matches production —
and it was reporting a mismatch for a reason with nothing to do with content.
Anyone hitting that would either chase a phantom content change or, worse,
redeploy to "fix" it and churn the live site for nothing.

It is the same family as the rest of today's findings: a check reporting a
property it is not actually measuring. Rule 14 already requires an explicit
`encoding=` on every open in this project; this is the newline half of the same
lesson, and `build_deploy.py` is now explicit about both.

### A faulty measurement of my own, corrected mid-diagnosis

My first line-ending count used `grep -c $'\r'` and reported **8,473 CRLF lines
in both files** — which would have meant line endings were *not* the cause. That
was wrong: the pattern degraded to empty and matched every line, so both numbers
were just the line total.

The reliable evidence was `cmp` after `tr -d '\r'` plus the normalised hash. Had
I trusted the grep I would have reported the opposite conclusion and gone
looking for a content difference that does not exist.

## Now proven ON THIS MACHINE, which was the point

The earlier state was that `_deploy/` was unreproducible here at all —
`build_full.py` was hardcoded to a cloud sandbox with six `/home/claude` paths,
none of which exist on this machine. That is closed:

- the build runs here,
- from repo-relative inputs and a vendored three.js,
- produces the artifact that is actually live,
- and is stable across repeated runs.

## `build_full.py` retired

Already retired earlier this session in `4d07f6b`, moved to
`_to_delete/build_full_retired_20260801/` rather than deleted, per rule 1.
Confirmed absent from `testing/_src/`. One build script, one artifact.

Still present and still flagged: `build_portable.py` retains 5 `/home/claude`
references and cannot run here. It targets a different artifact, so it is not
the drift risk you were pointing at, but it is dead code on this machine.

## No deploy performed

The built artifact equals the deployed one, verified earlier from the served raw
bytes. Redeploying would upload identical content, so the site is left alone.
