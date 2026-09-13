#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uncommitted_receipt.py - how much work sits uncommitted, and how old the oldest is.
Writes logs/uncommitted.json; BOOT.md reads it (watcher-go/boot_uncommitted.go).

RULE16: INDEPENDENT - the truth is git's own `status`; the rule that splits it
is checks/commit_guard.in_doc_set, IMPORTED, so the documentation set exists in
one place and one language. Architecture's go, 2026-09-13
(`..._boot-line-go-the-844-are-not-a-chore-and-a-bounced-answer-is-invisible`).

WHY. Code piles up in the working tree until Sleven sits down, and nothing said
the pile was growing. `skills/` sat uncommitted on one disk long enough to become
a finding. A number nobody can see is a number nobody acts on.

WHY A PYTHON RECEIPT AND NOT GO. "Outside the documentation set" is decided by
in_doc_set. If the Go watcher decided it too, the rule would exist twice, in two
languages, and drift. So this decides, the beat runs it, and boot.go only reads.

THE RECEIPT
    {"at": ISO, "state": "ok", "outside_doc_set": N, "outside_oldest": ISO|null,
     "doc_set": M, "doc_set_oldest": ISO|null}
    {"at": ISO, "state": "did-not-look", "reason": "..."}   git missing, timed out,
                                                          or not a repository

A receipt that could not look SAYS SO. It is never written as zero - an absent
count and a zero look identical, which is the defect this exists to stop.

git status is local (no network) and measured at ~0.1 s over 1,860 paths; it is
still given a timeout, because a lock held by another git command can stall it.

Rule 15: the receipt is written with encoding="utf-8"; git output is decoded as utf-8.

Usage:
    python checks/uncommitted_receipt.py              write logs/uncommitted.json
    python checks/uncommitted_receipt.py --self-test
"""
import datetime
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from commit_guard import in_doc_set  # noqa: E402  ONE DOC-SET RULE

OUT_REL = os.path.join("logs", "uncommitted.json")
GIT_TIMEOUT = 30


def _iso(t):
    return datetime.datetime.fromtimestamp(t).isoformat(timespec="seconds") if t else None


def measure(root, now=None):
    """-> the receipt dict. Never raises; a failure is a did-not-look receipt."""
    at = (now or datetime.datetime.now()).isoformat(timespec="seconds")
    try:
        r = subprocess.run(["git", "status", "--porcelain", "-z", "--untracked-files=all"],
                           cwd=root, capture_output=True, timeout=GIT_TIMEOUT)
    except subprocess.TimeoutExpired:
        return {"at": at, "state": "did-not-look", "reason": "git status timed out after %ds" % GIT_TIMEOUT}
    except OSError as e:
        return {"at": at, "state": "did-not-look", "reason": "git could not run (%s)" % e}
    if r.returncode != 0:
        why = r.stderr.decode("utf-8", "replace").strip().splitlines()
        return {"at": at, "state": "did-not-look",
                "reason": "git status exit %d: %s" % (r.returncode, why[0][:160] if why else "")}
    outside, docs = [], []
    for e in r.stdout.decode("utf-8", "replace").split("\0"):
        if len(e) < 4:
            continue
        st, p = e[:2], e[3:]
        added_or_modified = st == "??" or ("D" not in st and "R" not in st)
        full = os.path.join(root, *p.split("/"))
        mt = os.path.getmtime(full) if os.path.exists(full) else None
        (docs if added_or_modified and in_doc_set(p)[0] else outside).append(mt)
    old = lambda xs: _iso(min(x for x in xs if x)) if any(xs) else None   # noqa: E731
    return {"at": at, "state": "ok", "outside_doc_set": len(outside), "outside_oldest": old(outside),
            "doc_set": len(docs), "doc_set_oldest": old(docs)}


def write(root, receipt):
    out = os.path.join(root, OUT_REL)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    tmp = out + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(receipt, fh, indent=1)
    os.replace(tmp, out)
    return out


def self_test():
    import shutil
    import stat
    import tempfile

    results = []

    def check(ok, what):
        results.append(bool(ok))
        print("  %-7s %s" % ("caught" if ok else "MISSED", what))

    def git(cwd, *a):
        subprocess.run(["git"] + list(a), cwd=cwd, capture_output=True, check=True)

    def put(root, rel, body="x\n"):
        p = os.path.join(root, *rel.split("/"))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)

    tmp = tempfile.mkdtemp(prefix="cc-uncommitted-")
    try:
        repo = os.path.join(tmp, "repo")
        os.makedirs(repo)
        git(repo, "init", "-q", "-b", "main")
        git(repo, "config", "user.name", "plant")
        git(repo, "config", "user.email", "plant@example.invalid")
        git(repo, "config", "commit.gpgsign", "false")
        put(repo, "src/app.py")
        put(repo, "docs/a.md")
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", "base")

        r0 = measure(repo)
        check(r0["state"] == "ok" and r0["outside_doc_set"] == 0 and r0["doc_set"] == 0
              and r0["outside_oldest"] is None, "a clean tree reads ZERO, and says ok")
        put(repo, "src/new.py")
        put(repo, "docs/new.md")
        r1 = measure(repo)
        check(r1["outside_doc_set"] == 1 and r1["doc_set"] == 1,
              "an untracked code file and an untracked doc land on their own sides")
        put(repo, "src/app.py", "changed\n")
        r2 = measure(repo)
        check(r2["outside_doc_set"] == 2, "a modified tracked code file moves the number")
        check(r2["outside_oldest"] is not None, "the oldest age is recorded")
        git(repo, "add", "src/new.py", "src/app.py")
        git(repo, "commit", "-q", "-m", "commit them")
        r3 = measure(repo)
        check(r3["outside_doc_set"] == 0 and r3["doc_set"] == 1,
              "committing the code brings the number back down")
        put(repo, "CLAUDE.md", "rules\n")
        check(measure(repo)["outside_doc_set"] == 1, "CLAUDE.md is outside the set (NEVER), by the guard's rule")

        plain = os.path.join(tmp, "not-a-repo")
        os.makedirs(plain)
        r4 = measure(plain)
        check(r4["state"] == "did-not-look" and "outside_doc_set" not in r4,
              "not a repository -> did-not-look with a reason, never a zero")
        out = write(repo, r1)
        with io.open(out, encoding="utf-8") as fh:
            back = json.load(fh)
        check(back == r1 and not os.path.exists(out + ".tmp"), "the receipt is written whole, through a temp file")
    except Exception as exc:                        # noqa: BLE001
        check(False, "the self-test itself ran (%s: %s)" % (type(exc).__name__, exc))
    finally:
        def _force(func, path, _info):
            os.chmod(path, stat.S_IWRITE)
            func(path)
        shutil.rmtree(tmp, onerror=_force)

    caught, total = sum(results), len(results)
    print("\n%d of %d cases landed." % (caught, total))
    if caught != total or total < 8:
        print("SELF-TEST FAILED - this receipt must not be trusted.")
        return 3
    print("SELF-TEST PASSED. Exiting NON-ZERO on purpose: the suite requires a "
          "control's self-test to be rejected. This is the GOOD outcome.")
    return 1


def main(argv):
    if "--self-test" in argv:
        return self_test()
    rec = measure(ROOT)
    out = write(ROOT, rec)
    if rec["state"] == "ok":
        print("uncommitted: %d outside the documentation set (oldest %s), %d doc-set - %s"
              % (rec["outside_doc_set"], rec["outside_oldest"], rec["doc_set"], out))
    else:
        print("uncommitted: DID NOT LOOK - %s - %s" % (rec["reason"], out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
