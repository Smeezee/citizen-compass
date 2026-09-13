#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
commit_filed_mail.py - the watcher commits the mail it filed, on a cadence.

RULE16: INDEPENDENT - WHAT is committed comes from the router's own log (the
check-mark lines the Go watcher writes as it files); WHETHER a path may be
committed is decided by checks/commit_guard.in_doc_set, IMPORTED, and then again
by the real pre-commit guard reading git's staged index - a different program
reading a different source.

Accepted by Architecture 2026-09-13 (`..._three-architecture-rulings-b2-enable-
cadence-readme-finish-brain.md`, section 2), built to
`claude/PROPOSAL_the-watcher-commits-filed-mail-2026-09-13.md`:

    cadence   hourly, and only when something new was filed (--beat keeps the hour)
    what      paths a check-mark line filed under correspondence/ or
              docs/handoff_archive/, whose LATEST filing is one beat (10 min) old,
              at the path where each sits NOW, and only if git sees it changed
    push      NEVER - there is no push, fetch or remote anywhere in this file
    refuse    a non-empty index (another writer is staging): nothing this run
              one path outside the documentation set: the WHOLE batch
              the pre-commit guard refuses: exactly our paths are unstaged
              more than BULK paths without --approve <batch id>: rule 5
    author    Citizen Compass Watcher <watcher@local>, as author AND committer

WHERE A FILED LETTER IS NOW. A check-mark line names where the router put it. If
it is not there any more (an answered letter moves from open/ to answered/), it
is found by its exact filename under correspondence/: one match is where it sits;
none is GONE; two or more is AMBIGUOUS, all named, and none committed (rule 19).

A SUPERSEDING FILING keeps the older copy under a `__<stamp>` name and says so on
the same line ("the older one is kept as X"). That copy is router output too, and
is committed with the new one.

THE FIRST RUN IS THE BACKLOG (about 850). Rule 5: the dry run prints exactly the
batch, its id and the `--until` it was cut at; a bulk batch is committed only by
`--commit --until <that> --approve <that id>`, after Sleven has seen the list.

Every run but the dry run writes logs/mail_commit.json: when, the state
(committed / nothing-new / index-busy / bulk / refused-outside / refused-by-guard
/ git-busy / git-failed), the count, the batch id, the hash or the reason.
index-busy is another writer's STAGED paths; git-busy is another git process
holding `.git/index.lock` - both leave the index as found and retry next hour. A run that could
not look says so; it is never written as zero.

Rule 15: every text open states encoding="utf-8"; git output is decoded as utf-8.

Usage:
    python checks/commit_filed_mail.py                   dry run: the batch and its id; writes nothing
    python checks/commit_filed_mail.py --commit          commit now
    python checks/commit_filed_mail.py --beat            what the beat runs: --commit, once per clock hour
    ... --until "YYYY-MM-DD HH:MM:SS" --approve ID       a bulk batch Sleven has seen (rule 5)
    python checks/commit_filed_mail.py --self-test
"""
import datetime
import hashlib
import io
import json
import os
import posixpath
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from commit_guard import in_doc_set  # noqa: E402  ONE DOC-SET RULE

LOG_REL = "logs/inbox_watcher.log"
OUT_REL = "logs/mail_commit.json"
PREFIXES = ("correspondence/", "docs/handoff_archive/")
SETTLE = datetime.timedelta(minutes=10)          # one beat
BULK = 100
AUTHOR_NAME, AUTHOR_EMAIL = "Citizen Compass Watcher", "watcher@local"
GIT_TIMEOUT = 120
STAMP = "%Y-%m-%d %H:%M:%S"

RE_FILED = re.compile(r"^\[(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)\] \u2713 .*? -> (.+?)(?: \((.*)\))?$")
RE_KEPT = re.compile(r"the older one is kept as (\S+?\.md)")


class GitError(Exception):
    pass


def git(root, args, data=None):
    try:
        r = subprocess.run(["git"] + args, cwd=root, input=data, capture_output=True,
                           timeout=GIT_TIMEOUT)
    except subprocess.TimeoutExpired:
        raise GitError("git %s timed out after %ds" % (args[0], GIT_TIMEOUT))
    except OSError as e:
        raise GitError("git could not run (%s)" % e)
    return r


def _text(b):
    return b.decode("utf-8", "replace").strip()


def _rel(root, dest):
    try:
        rel = os.path.relpath(dest, root).replace("\\", "/")
    except ValueError:                           # another drive
        return None
    return None if rel == ".." or rel.startswith("../") else rel


def filings(root):
    """-> [(when, rel)] for every path the router filed under PREFIXES, in log order."""
    out = []
    with io.open(os.path.join(root, *LOG_REL.split("/")), encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = RE_FILED.match(line.rstrip("\r\n"))
            if not m:
                continue
            when = datetime.datetime.strptime(m.group(1), STAMP)
            rel = _rel(root, m.group(2).strip())
            if not rel:
                continue
            rels = [rel]
            k = RE_KEPT.search(m.group(3) or "")
            if k:
                rels.append(posixpath.join(posixpath.dirname(rel), k.group(1)))
            out += [(when, r) for r in rels if r.startswith(PREFIXES)]
    return out


def names_under_correspondence(root):
    names = {}
    for dp, _dn, fn in os.walk(os.path.join(root, "correspondence")):
        for f in fn:
            names.setdefault(f, []).append(
                os.path.relpath(os.path.join(dp, f), root).replace("\\", "/"))
    return names


def where_now(root, rel, names):
    """-> (current path, None) or (None, GONE / AMBIGUOUS - ...). Never guessed."""
    if os.path.isfile(os.path.join(root, *rel.split("/"))):
        return rel, None
    if not rel.startswith("correspondence/"):
        return None, "GONE"
    hits = sorted(names.get(posixpath.basename(rel), []))
    if len(hits) == 1:
        return hits[0], None
    return None, ("GONE" if not hits else "AMBIGUOUS - %s" % ", ".join(hits))


def changed(root):
    """-> paths git sees as untracked or modified under the two prefixes."""
    r = git(root, ["status", "--porcelain", "-z", "--untracked-files=all", "--",
                   "correspondence", "docs/handoff_archive"])
    if r.returncode != 0:
        raise GitError("git status exit %d: %s" % (r.returncode, _text(r.stderr)[:160]))
    parts, out, i = r.stdout.decode("utf-8", "replace").split("\0"), set(), 0
    while i < len(parts):
        e = parts[i]
        i += 1
        if len(e) < 4:
            continue
        st, p = e[:2], e[3:]
        if "R" in st or "C" in st:
            i += 1                               # -z: the source path follows as its own field
            continue
        if "D" not in st:
            out.add(p)
    return out


def staged(root):
    r = git(root, ["diff", "--cached", "--name-only", "-z"])
    if r.returncode != 0:
        raise GitError("git diff --cached exit %d: %s" % (r.returncode, _text(r.stderr)[:160]))
    return [p for p in r.stdout.decode("utf-8", "replace").split("\0") if p]


def plan(root, now, until=None):
    """-> the batch. Read-only."""
    until = until or (now - SETTLE)
    latest = {}
    names = names_under_correspondence(root)
    skipped = {}
    for when, rel in filings(root):
        cur, why = where_now(root, rel, names)
        if cur is None:
            skipped[rel] = why
            continue
        latest[cur] = max(when, latest.get(cur, when))
    dirty = changed(root)
    batch = sorted(p for p, w in latest.items() if w <= until and p in dirty)
    waiting = sorted(p for p, w in latest.items() if w > until and p in dirty)
    outside = [(p, in_doc_set(p)[1]) for p in batch if not in_doc_set(p)[0]]
    return {"until": until.strftime(STAMP), "batch": batch, "waiting": waiting,
            "id": hashlib.sha256("\n".join(batch).encode("utf-8")).hexdigest()[:16],
            "outside": outside,
            "ambiguous": sorted((p, w) for p, w in skipped.items() if w.startswith("AMBIGUOUS")),
            "gone": sum(1 for w in skipped.values() if w == "GONE")}


def _paths(paths):
    return b"\0".join(p.encode("utf-8") for p in paths)


def _busy(r):
    """`git-busy` when git refused because another git process holds the index lock.

    Not a guard refusal and not a failure: git's own lock made the second writer
    stop, exactly as the proposal's rule 14 section says, and the beat retries next
    hour. Named for what it is (Architecture, 2026-09-13, after one was labelled
    refused-by-guard at 15:07:16). Matched on git's own message, exactly."""
    return "git-busy" if "index.lock" in _text(r.stderr) + _text(r.stdout) else None


def commit(root, p):
    """Stage exactly the batch, commit through the real hook. -> (state, hash_or_reason)."""
    paths = p["batch"]
    add = git(root, ["--literal-pathspecs", "add", "--pathspec-from-file=-", "--pathspec-file-nul"],
              _paths(paths))
    if add.returncode != 0:
        git(root, ["--literal-pathspecs", "reset", "-q", "--pathspec-from-file=-",
                   "--pathspec-file-nul"], _paths(paths))
        return (_busy(add) or "git-failed"), "git add exit %d: %s" % (add.returncode, _text(add.stderr)[:200])
    corr = sum(1 for x in paths if x.startswith("correspondence/"))
    msg = ("Watcher: commit %d filed letter(s) and archived update(s)\n\n"
           "correspondence/ %d, docs/handoff_archive/ %d. Batch %s, filed up to %s.\n"
           "Committed by checks/commit_filed_mail.py, which never pushes.\n"
           % (len(paths), corr, len(paths) - corr, p["id"], p["until"]))
    c = git(root, ["-c", "user.name=" + AUTHOR_NAME, "-c", "user.email=" + AUTHOR_EMAIL,
                   "commit", "-q", "--author=%s <%s>" % (AUTHOR_NAME, AUTHOR_EMAIL), "-m", msg])
    if c.returncode != 0:
        git(root, ["--literal-pathspecs", "reset", "-q", "--pathspec-from-file=-",
                   "--pathspec-file-nul"], _paths(paths))
        why = (_text(c.stderr) or _text(c.stdout)).splitlines()
        left = staged(root)
        return (_busy(c) or "refused-by-guard"), ("commit exit %d: %s; our paths unstaged, %d left staged"
                                                  % (c.returncode, " | ".join(why[-3:])[:300], len(left)))
    h = git(root, ["rev-parse", "HEAD"])
    return "committed", _text(h.stdout)


def write(root, rec):
    out = os.path.join(root, *OUT_REL.split("/"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    tmp = out + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(rec, fh, indent=1)
    os.replace(tmp, out)


def read_receipt(root):
    try:
        with io.open(os.path.join(root, *OUT_REL.split("/")), encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def run(root, now, mode, until=None, approve=None, bulk=BULK):
    """mode: dry | commit | beat. -> (exit code, receipt or None)."""
    if mode == "beat":
        last = read_receipt(root)
        if last and str(last.get("at", ""))[:13] == now.isoformat(timespec="seconds")[:13]:
            print("mail commit: not this hour (last run %s, %s)" % (last.get("at"), last.get("state")))
            return 0, None
    rec = {"at": now.isoformat(timespec="seconds")}
    try:
        p = plan(root, now, until)
        rec.update(until=p["until"], batch_id=p["id"], count=len(p["batch"]))
        busy = staged(root)
        if mode == "dry":
            for x in p["batch"]:
                print("  would commit  %s" % x)
            for x, why in p["ambiguous"]:
                print("  NOT COMMITTED %s  %s" % (x, why))
            print("mail commit DRY RUN: %d path(s), batch %s, filed up to %s; %d waiting to settle; "
                  "%d outside the documentation set; %d ambiguous; %d filed and gone; index %s. "
                  "Nothing was written." % (len(p["batch"]), p["id"], p["until"], len(p["waiting"]),
                                            len(p["outside"]), len(p["ambiguous"]), p["gone"],
                                            ("BUSY (%d staged)" % len(busy)) if busy else "empty"))
            return 0, None
        if not p["batch"]:
            rec.update(state="nothing-new")
        elif busy:
            rec.update(state="index-busy", reason="%d path(s) already staged by another writer: %s"
                       % (len(busy), ", ".join(busy[:10])))
        elif p["outside"]:
            rec.update(state="refused-outside", reason="; ".join(
                "%s (%s)" % (x, why) for x, why in p["outside"][:10]))
        elif len(p["batch"]) > bulk and approve != p["id"]:
            rec.update(state="bulk", reason="%d paths is more than %d; rule 5 - Sleven sees the dry "
                       "run, then --commit --until \"%s\" --approve %s" % (len(p["batch"]), bulk,
                                                                          p["until"], p["id"]))
        else:
            state, detail = commit(root, p)
            rec.update(state=state)
            rec["hash" if state == "committed" else "reason"] = detail
    except GitError as e:
        rec.update(state="git-failed", reason=str(e))
    except OSError as e:
        rec.update(state="git-failed", reason="could not read the router log (%s)" % e)
    write(root, rec)
    print("mail commit: %s - %d path(s)%s" % (rec["state"], rec.get("count", 0),
                                              (" at " + rec["hash"][:12]) if "hash" in rec
                                              else (" - " + rec["reason"]) if "reason" in rec else ""))
    return (1 if rec["state"] in ("refused-outside", "refused-by-guard", "git-failed") else 0), rec


# ------------------------------------------------------------------ self-test
def self_test():
    import shutil
    import stat
    import tempfile

    results = []

    def check(ok, what):
        results.append(bool(ok))
        print("  %-7s %s" % ("caught" if ok else "MISSED", what))

    tmp = tempfile.mkdtemp(prefix="cc-mailcommit-")
    try:
        repo = os.path.join(tmp, "repo")
        bare = os.path.join(tmp, "remote.git")
        os.makedirs(repo)

        def g(*a, cwd=repo):
            r = subprocess.run(["git"] + list(a), cwd=cwd, capture_output=True)
            if r.returncode != 0:
                raise RuntimeError("fixture git %s: %s" % (a[0], _text(r.stderr)))
            return _text(r.stdout)

        def put(rel, body="x\n"):
            p = os.path.join(repo, *rel.split("/"))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(body)

        log_lines = []

        def filed(stamp, rel, desc="memo for build from Architecture - x"):
            dest = os.path.join(repo, *rel.split("/"))
            log_lines.append("[2026-09-13 %s] \u2713 %s -> %s (%s)\n"
                             % (stamp, posixpath.basename(rel), dest, desc))
            with io.open(os.path.join(repo, "logs", "inbox_watcher.log"), "w",
                         encoding="utf-8", newline="\n") as fh:
                fh.writelines(log_lines)

        def head():
            return g("rev-parse", "HEAD")

        def files_in(h):
            return set(g("show", "--name-only", "--format=", h).splitlines())

        def state_hash():
            h = hashlib.sha256()
            for dp, dn, fn in sorted(os.walk(repo)):
                dn[:] = sorted(d for d in dn if d not in (".git", "logs"))
                for f in sorted(fn):
                    with open(os.path.join(dp, f), "rb") as fh:
                        h.update(f.encode("utf-8") + fh.read())
            h.update(g("diff", "--cached", "--name-only").encode("utf-8"))
            return h.hexdigest() + head()

        NOW = datetime.datetime(2026, 9, 13, 12, 0, 0)
        g("init", "-q", "-b", "main")
        g("config", "user.name", "plant")
        g("config", "user.email", "plant@example.invalid")
        g("config", "commit.gpgsign", "false")
        put(".gitignore", "logs/\n")
        put("correspondence/README.md", "mail\n")
        os.makedirs(os.path.join(repo, "logs"))
        g("add", ".gitignore", "correspondence/README.md")
        g("commit", "-q", "-m", "base")
        subprocess.run(["git", "init", "-q", "--bare", bare], capture_output=True, check=True)
        g("remote", "add", "origin", bare)
        g("push", "-q", "origin", "main")
        remote_ref = g("rev-parse", "main", cwd=bare)
        # THE REAL GUARD, IN PLACE: its repo is the directory above its own checks/.
        os.makedirs(os.path.join(repo, "checks"))
        shutil.copy2(os.path.join(HERE, "commit_guard.py"), os.path.join(repo, "checks", "commit_guard.py"))
        hook = os.path.join(repo, ".git", "hooks", "pre-commit")
        real_hook = '#!/bin/sh\nexec "%s" "%s"\n' % (sys.executable.replace("\\", "/"),
                                                     os.path.join(repo, "checks", "commit_guard.py").replace("\\", "/"))
        with io.open(hook, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(real_hook)
        with io.open(os.path.join(repo, ".git", "info", "exclude"), "a", encoding="utf-8") as fh:
            fh.write("checks/\n")

        # 1, 8, 11, 15: a settled letter and an archived update commit; a fresh one waits
        put("correspondence/open/build/a.md")
        put("correspondence/open/build/fresh.md")
        put("docs/handoff_archive/20260913_1_u.md")
        filed("11:00:00", "correspondence/open/build/a.md")
        filed("11:01:00", "docs/handoff_archive/20260913_1_u.md", "update doc - archived")
        filed("11:55:00", "correspondence/open/build/fresh.md")
        before = state_hash()
        rc, _ = run(repo, NOW, "dry")
        check(rc == 0 and state_hash() == before and read_receipt(repo) is None,
              "8  the dry run writes nothing: tree, index, HEAD and receipt unchanged")
        h0 = head()
        rc, rec = run(repo, NOW, "commit")
        h1 = head()
        got = files_in(h1) if h1 != h0 else set()
        check(rec["state"] == "committed" and "correspondence/open/build/a.md" in got,
              "1  a filed, settled letter is committed")
        check("correspondence/open/build/fresh.md" not in got,
              "1b a letter filed in the last beat is NOT committed yet")
        check("docs/handoff_archive/20260913_1_u.md" in got, "15 an archived update is committed")
        check(g("log", "-1", "--format=%an <%ae>|%cn <%ce>") ==
              "%s <%s>|%s <%s>" % (AUTHOR_NAME, AUTHOR_EMAIL, AUTHOR_NAME, AUTHOR_EMAIL),
              "11 author AND committer are the watcher, not the configured user")
        check(g("rev-parse", "main", cwd=bare) == remote_ref, "6  it never pushes: the remote's ref did not move")

        # 2: nothing new
        rc, rec = run(repo, NOW, "commit")
        check(rec["state"] == "nothing-new" and head() == h1, "2  nothing new -> no commit")

        # 10: the beat keeps the hour
        rc, rec = run(repo, NOW.replace(minute=30), "beat")
        check(rec is None and head() == h1, "10 a second run in the same clock hour does nothing")

        # 3: another writer is staging
        put("docs/other.md")
        g("add", "docs/other.md")
        put("correspondence/open/build/b.md")
        filed("11:10:00", "correspondence/open/build/b.md")
        rc, rec = run(repo, NOW, "commit")
        check(rec["state"] == "index-busy" and head() == h1 and staged(repo) == ["docs/other.md"],
              "3  a non-empty index -> nothing staged or committed, the other writer's path untouched")
        g("reset", "-q", "--", "docs/other.md")

        # 4: one path outside the documentation set stops the whole batch
        put("correspondence/open/build/zip.bin")
        filed("11:20:00", "correspondence/open/build/zip.bin", "zip archived")
        rc, rec = run(repo, NOW, "commit")
        check(rec["state"] == "refused-outside" and head() == h1 and not staged(repo) and rc == 1,
              "4  one path outside the documentation set refuses the WHOLE batch, index untouched")
        os.remove(os.path.join(repo, "correspondence", "open", "build", "zip.bin"))

        # 5: the guard refuses -> exactly our paths unstaged, no partial commit
        with io.open(hook, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("#!/bin/sh\necho planted refusal >&2\nexit 1\n")
        rc, rec = run(repo, NOW, "commit")
        check(rec["state"] == "refused-by-guard" and head() == h1 and not staged(repo) and rc == 1,
              "5  a guard refusal unstages exactly our paths, and nothing is committed")
        with io.open(hook, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(real_hook)

        # 16: another git process holds the index lock -> git-busy, nothing staged or committed
        lock = os.path.join(repo, ".git", "index.lock")
        with open(lock, "wb"):
            pass
        rc, rec = run(repo, NOW, "commit")
        os.remove(lock)
        check(rec["state"] == "git-busy" and rc == 0 and head() == h1 and not staged(repo),
              "16 a held index.lock is git-busy (not a guard refusal), and nothing is staged")

        # 7, 12, 13, 14
        put("correspondence/answered/m.md")
        filed("11:12:00", "correspondence/open/build/m.md")
        put("correspondence/answered/amb.md")
        put("correspondence/open/owner/amb.md")
        filed("11:13:00", "correspondence/open/build/amb.md")
        put("correspondence/open/build/t.md")
        put("correspondence/open/build/t__20260913111400.md")
        filed("11:14:00", "correspondence/open/build/t.md",
              "memo for build - (SUPERSEDES an earlier file of this name - the older one is kept as "
              "t__20260913111400.md; this name now holds the newest)")
        put("correspondence/open/build/late.md")
        filed("11:15:00", "correspondence/open/build/late.md")
        filed("11:58:00", "correspondence/open/build/late.md")
        rc, rec = run(repo, NOW, "commit")
        h2 = head()
        got = files_in(h2) if h2 != h1 else set()
        check("correspondence/answered/m.md" in got,
              "7  a letter that moved on after filing is committed where it sits now")
        check(not any(x.endswith("amb.md") for x in got),
              "13 two files by one filename is AMBIGUOUS: neither is committed")
        check({"correspondence/open/build/t.md", "correspondence/open/build/t__20260913111400.md"} <= got,
              "12 a superseding filing commits the kept older copy too")
        check("correspondence/open/build/late.md" not in got,
              "14 a path re-filed in the last beat waits, whatever its first filing")
        check("correspondence/open/build/b.md" in got, "   the letter held back by the busy index goes next")

        # 9: rule 5, the bulk gate
        for i in range(3):
            put("correspondence/open/build/bulk%d.md" % i)
            filed("11:3%d:00" % i, "correspondence/open/build/bulk%d.md" % i)
        rc, rec = run(repo, NOW, "commit", bulk=2)
        check(rec["state"] == "bulk" and head() == h2 and not staged(repo),
              "9  a batch over BULK is refused without the approval")
        rc, rec = run(repo, NOW, "commit", bulk=2, approve="0" * 16)
        check(rec["state"] == "bulk" and head() == h2, "9b an approval for a DIFFERENT batch id is refused")
        until = datetime.datetime.strptime(rec["until"], STAMP)
        rc, rec = run(repo, NOW, "commit", until=until, approve=rec["batch_id"], bulk=2)
        check(rec["state"] == "committed" and files_in(head()) ==
              {"correspondence/open/build/bulk%d.md" % i for i in range(3)},
              "9c the approved batch, cut at the same --until, commits")
    except Exception as exc:                        # noqa: BLE001
        check(False, "the self-test itself ran (%s: %s)" % (type(exc).__name__, exc))
    finally:
        def _force(func, path, _info):
            os.chmod(path, stat.S_IWRITE)
            func(path)
        shutil.rmtree(tmp, onerror=_force)

    caught, total = sum(results), len(results)
    print("\n%d of %d cases landed." % (caught, total))
    if caught != total or total < 20:
        print("SELF-TEST FAILED - this committer must not be trusted.")
        return 3
    print("SELF-TEST PASSED. Exiting NON-ZERO on purpose: the suite requires a "
          "control's self-test to be rejected. This is the GOOD outcome.")
    return 1


def _arg(argv, name):
    return argv[argv.index(name) + 1] if name in argv and argv.index(name) + 1 < len(argv) else None


def main(argv):
    if "--self-test" in argv:
        return self_test()
    now = datetime.datetime.now().replace(microsecond=0)
    until = _arg(argv, "--until")
    until = datetime.datetime.strptime(until, STAMP) if until else None
    mode = "beat" if "--beat" in argv else "commit" if "--commit" in argv else "dry"
    rc, _ = run(ROOT, now, mode, until=until, approve=_arg(argv, "--approve"))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
