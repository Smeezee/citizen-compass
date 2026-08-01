# UPDATE — Ollama disabled, wording corrected, source 1 re-gated (finding)

Four items. Nothing committed, nothing pushed.

## 1. Ollama / local-AI compression DISABLED

`generate_handoff.py` already shipped a kill switch — `USE_LOCAL_AI_COMPRESSION`
at line 59, committed — simply set to `True`. Now `False`, with the reason in a
comment.

| | before | after |
|---|---:|---:|
| regeneration time | ~120s | **0s** |
| LATEST_HANDOFF.md size | 86,090 chars | 86,009 chars |

The 120s was `OLLAMA_TIMEOUT_SECONDS` elapsing against a service that is not
running, then falling back to raw text regardless. It was contributing nothing.
Function and constants left in place (gated, not deleted) so it is reversible.

To be clear about how it got used at all: I did not choose it.
`build_notes_block()` calls it unconditionally, and running the generator to
verify the parser fix invoked it. Zero Ollama lines appear in my diff.

## 2. "deterministic" wording corrected in `api_star_citizen_wiki.py`

The fix comment claimed the `page[size]=200` failure was *deterministic*. That
overstated the evidence by one data point. Full record at 200:

| source | attempts | result |
|---|---:|---|
| run 1 (scripted) | 5 | all 500 |
| run 2 (scripted) | 5 | all 500 |
| run 1 manual curl | 3 | 2 failed, **1 succeeded** |
| 2026-07-31 probe | 1 | 500 |

**1 success in ~14 attempts — near-deterministic, not absolute.** The comment now
says so. This also dissolves the "unresolved contradiction" raised in the cowork
entry: the manifest's single recorded success and the probe's failure are both
true, and neither manifest needs amending.

## 3. Source 1 RE-GATED with the fixed `integrity_scan.py`

Snapshot `20260731T041451Z` — **28,993 files, 5.8 GB**. First time this snapshot
has been scanned by a gate that opens non-JSON files.

```
files_seen 28993 | files_scanned 28993 | files_unscanned 0
walk_errors NONE | coverage complete TRUE
content_indicator_hits: 0 files
unexpected_domains:     1 file
```

**Zero active-content indicators across all 28,993 files.**

### The finding: the snapshot contains a live `.git` directory

The old `*.json`-globbing gate never saw **any** of it. 33 files under `.git/`,
including:

- **4 ACTIVE git hooks** (no `.sample` suffix): `post-checkout`, `post-commit`,
  `post-merge`, `pre-push`
- git pack objects — the 4 files that needed replacement decoding are
  `index`, `pack-8c326a0b….idx/.pack/.rev`
- `.git/config` with a live remote:
  `https://github.com/StarCitizenWiki/scunpacked-data.git`

**Assessed, not assumed — the hooks are benign.** I read all four (reading is
fine under rule 7; executing is not). They are verbatim stock **Git LFS** hooks,
installed locally by `git lfs install` during the clone, each a 350-360 byte
`sh` script that shells out to `git lfs <verb>`. Nothing injected, nothing
third-party-authored.

The flagged domain is `facebook.github.io`, appearing once, in
`.git/hooks/fsmonitor-watchman.sample` — a stock file shipped with every git
installation, pointing at the Watchman docs. Also present: `github.com` x4 in
`.git/config` and `.git/logs/*`, already allowlisted.

### Gate verdict

**FAIL**, on the fail-closed criterion — `unexpected_domains` is non-empty. The
finding is benign, but "benign" is not "passed", and source 1 was already
finalized out of `.partial` back on 2026-07-31. **No status was changed and
nothing in that snapshot was touched.**

### Two things this raises, both Sleven's call

1. **`facebook.github.io`** is a stock git file. Either allowlist it, or accept
   that any snapshot cloned with git will fail gate 5 on it forever.
2. **A `.git` directory makes the snapshot non-inert.** It has a working remote,
   so a `git pull` inside that folder would mutate data we describe as an
   immutable snapshot, and the LFS hooks would fire on git operations. Worth
   deciding whether `.git` belongs in a data snapshot at all. If it should go,
   it gets **moved to `_to_delete/`**, never deleted — and it alters a finalized
   snapshot, so it is not something to do unilaterally.

## 4. Memories saved

Three, so they survive compaction: Ollama is off and should not be reached for;
work autonomously and only interrupt when genuinely stuck; the handoff-generator
traps (both now fixed).

## Uncommitted

`generate_handoff.py`, `ccpp.py`, `api_star_citizen_wiki.py`,
`_verify_generate_handoff.py`, and the re-gate report under
`data-layer/external-source-verification/20260731T041451Z-regate/`.
Commit `0ae0514` remains unpushed — `main` is 1 ahead of `origin/main`.
