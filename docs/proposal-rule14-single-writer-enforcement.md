# PROPOSAL — making rule 14 true, not just written down

Written 2026-08-02 by Claude Code. **Proposal only — nothing here is
implemented.**

Rule 14 says one writer per artifact, enforced by construction. This is the
part that makes it enforced. Rule 14 without this is a convention with a rule
number.

---

## The constraint I will not paper over

The two previous fixes worked because each had a **choke point**:

- the inbox watcher had a *registration* step (`schtasks`), so a guard could
  refuse to register a second one;
- the auditor schedule had the same.

Both now match on **what a task executes**, not what it is called, and both are
proven to refuse. Neither actually prevents you creating a task by hand — they
prevent a *second registration*, which is where the failure came from.

**File writes have no such choke point here.** All three sessions run as the
same OS user on one machine. Any of them can open `_layer.src.html` and write
it. **I cannot make that impossible, and saying "enforced" would be exactly the
kind of enforcement-that-isn't this project keeps finding.**

So the honest target is the one rule 14 already states: **make an unacknowledged
write loud and immediate, and refuse to ship un-provenanced content.** That is
the same bar the task guards actually meet.

## What actually goes wrong — from four real incidents in one evening

| # | what happened | how it was caught |
|---|---|---|
| 1 | a session deleted the keybinds overlay and compliance strip | a marker count, minutes before deploy |
| 2 | a session rewrote the layer mid-verification, landing an in-progress feature into an unrelated commit | reading `git status` afterwards |
| 3 | the committed `newline=''` fix was silently dropped by an edit made against an older copy | a reproducibility test that failed |
| 4 | the LOADOUT tab returned after being removed on instruction | Sleven noticing it in the built page |

**Not one was malice, and not one was a stale-`mtime` mistake.** Every one was a
session editing a copy it believed was current. Incident 3 is the clearest: the
edit was a genuine improvement (generalising the page copy into `PAGES`) that
happened to carry an old version of one line.

**Conclusion that shapes the design:** the enemy is not concurrent *writing*,
it is concurrent writing **without knowing the file moved**. The guard should
make "the file moved under you" impossible to miss, not try to stop the write.

---

## Proposal: compare-and-swap on the artifact

### 1. A lock file records the last owner-acknowledged state

`testing/_src/LAYER.lock` — tracked in git:

```json
{
  "path": "testing/_src/_layer.src.html",
  "sha256": "889e4ff1...",
  "written_by": "claude-code",
  "written_at": "2026-08-02T00:41:00-07:00",
  "note": "removed cc-lo-tab (second removal)"
}
```

### 2. The build refuses to run when disk disagrees with the lock

`build_deploy.py` hashes the layer before doing anything:

```
LAYER CHANGED OUTSIDE THE OWNER
  lock says : 889e4ff1...  (claude-code, 2026-08-02T00:41)
  on disk   : 83b331c6...
Someone other than the owner wrote this file. Nothing was built.
Reconcile, then re-run:  scripts/layer_write.py --accept
```

That single check converts all four incidents from *discovered later in a diff*
to *the build stops and names the file*.

### 3. Writes go through one helper that updates file and lock atomically

`scripts/layer_write.py` writes the content and the lock in one step. The lock
cannot drift from a legitimate edit, because a legitimate edit cannot update one
without the other.

`--accept` is the deliberate escape hatch: it re-reads disk, shows a diff, and
adopts the current bytes as the new baseline. **Deliberate, visible, logged** —
the opposite of a silent clobber. Escape hatches that do not exist get worked
around; this one is cheap and leaves a record.

### 4. The deploy re-checks immediately before upload

`deploy_testing.ps1` re-validates the lock at upload time, not at start. The
lesson from tonight: I staged files I had verified minutes earlier and they had
changed in between. **Only a check at the moment of use is a check.**

### 5. A daily checker reports drift even if nobody builds

A `single_writer` checker in the existing auditor layer compares each locked
artifact against its lock and reports a DEFECT naming the file. Catches a
clobber that would otherwise sit unnoticed until the next build.

### 6. Optional hardening — deny-write ACL

`icacls` deny-write on `_layer.src.html`, with `layer_write.py` granting itself
write for the duration.

Same OS user, so one `icacls` defeats it — **but all four incidents were
accidental**, and this converts an accidental clobber into an act someone had to
choose. Most of the value for very little machinery. Recommended, not required.

---

## What this does NOT do — stated plainly

- **It does not prevent the write.** A session can still overwrite the file. The
  guard makes that state undeployable, not impossible.
- **It does not recover clobbered content.** That comes from git, which is why
  the owner committing after every edit is part of the workflow, not optional.
  Incident 3's fix was recoverable only because it was committed.
- **It does not extend past artifacts that are locked.** Each artifact needs a
  lock entry. Start with `_layer.src.html`; `build_deploy.py` and
  `testing/_deploy/index.html` are the obvious next two.
- **It adds a step to every legitimate edit.** That cost is real. It is smaller
  than the four incidents already paid for.

## Rule 12 — how it would be proven before being trusted

A guard that has never refused is not a guard:

1. write via the helper, confirm build succeeds and lock matches;
2. modify the file behind the helper's back, confirm the build **exits non-zero
   and writes nothing**;
3. run `--accept`, confirm the build succeeds again;
4. confirm the deploy refuses on a lock mismatch even when the build output is
   already on disk from an earlier good run — the case where the artifact looks
   fine and its provenance is not.

Step 4 is the one worth the most: it is the case that looks like success.

## Scope of work

Roughly: lock format and helper (small), one guard call in `build_deploy.py`
(small), one in `deploy_testing.ps1` (small), one checker (medium, mostly
tests), ACL hardening (optional). The rule-12 proof is comparable in size to the
implementation, as it has been for every other guard here.
