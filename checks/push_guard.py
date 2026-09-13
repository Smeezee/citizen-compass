#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
push_guard.py - the pre-push half of the rule 2 documentation guard.

RULE16: INDEPENDENT - the truth is git's own statement of what this push would
send (the ref lines git hands a pre-push hook, and the commits in each range);
the rule it holds them to is commit_guard.py's documentation set, IMPORTED
rather than copied so the two hooks cannot disagree.

Approved by Architecture 2026-09-13 (`..._pre-push-amendment-accepted-build-it-
and-three-rulings-on-b2.md`), built to `claude/PROPOSAL_the-pre-push-guard-
2026-09-12.md` and its 2026-09-13 amendment.

THE HAZARD. The commit guard stops a desk COMMITTING code. Nothing stopped a
desk PUSHING a commit somebody else made - and a push sends every local commit
the remote lacks, not only the tip. 183a239 (the watcher source, Sleven's commit,
no push decided) rode on local main under every documentation push.

WHAT IT DOES. For every ref git says it will push:

    SUBJECT  the commit the pushed ref names        "named by this push"
    CARRIED  every other commit the push sends      "rides along"

Each commit's own paths are judged by commit_guard.judge: a path outside the
documentation set, or any rename or deletion, refuses the push. CARRIED is
printed first - it is the one the pusher does not know about.

THE LABEL IS STRUCTURE, NOT INTENT. In a push of three commits somebody wrote on
purpose, two print CARRIED. The words say only what git knows.

MERGES ARE READ WITH --cc. `diff-tree -m` diffs a merge against each parent and
blames a docs merge for every path its parents brought in (measured 2026-09-13:
29 lines against 8f40050, all of them 183a239's). --cc lists only what the merge
changed beyond all of its parents, so an evil merge still shows.

A REMOTE BRANCH DELETION IS REFUSED. It sends no commits and is not a
documentation push.

A COMMIT THAT CHANGES NO PATH PASSES. An empty commit, or a merge that resolved
nothing, has nothing to judge.

THE OVERRIDE is git's own `git push --no-verify`, reserved for Sleven's hand by
rule 2. No flag, environment variable or file is read.

WHAT IT CANNOT SEE: a push from another clone (hooks are local), and whether a
documentation push is WANTED - rule 2 still decides whether a push happens.

Exit 0 pass, 1 refused, 2 could not look (refused, never passed).

Rule 15: git's output is decoded as utf-8 explicitly; every file open states it.

Usage, as the hook:    push_guard.py <remote> <url>   (ref lines on stdin)
       python checks/push_guard.py --self-test
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from commit_guard import in_doc_set, judge  # noqa: E402,F401  ONE LIST, TWO HOOKS

ZERO = "0" * 40
SHOW = 30
ORDER = {"CARRIED": 0, "SUBJECT": 1, "DELETE": 2}
WHAT = {"CARRIED": "rides along - not named by this push",
        "SUBJECT": "named by this push",
        "DELETE": "a remote branch deletion"}


def git(repo, *args):
    r = subprocess.run(["git"] + list(args), cwd=repo, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("git %s: %s" % (" ".join(args),
                                           r.stderr.decode("utf-8", "replace").strip()))
    return r.stdout.decode("utf-8", "replace")


def commits_sent(repo, remote, local, remote_sha):
    """Every commit this ref's push would send, newest first."""
    if remote_sha == ZERO:
        out = git(repo, "rev-list", local, "--not", "--remotes=%s" % remote)
    else:
        out = git(repo, "rev-list", "%s..%s" % (remote_sha, local))
    return [c for c in out.split() if c]


def parse_z(raw):
    parts = raw.split("\0")
    entries, i = [], 0
    while i < len(parts):
        tok = parts[i].strip()
        if not tok:
            i += 1
            continue
        if tok.upper().startswith("R") and i + 2 < len(parts):
            entries.append((tok, parts[i + 1] + " -> " + parts[i + 2]))
            i += 3
            continue
        if i + 1 < len(parts):
            entries.append((tok, parts[i + 1]))
            i += 2
            continue
        i += 1
    return entries


def paths_of(repo, commit):
    """(status, path) for what THIS commit changed - a merge by --cc only."""
    parents = git(repo, "rev-list", "--parents", "-n", "1", commit).split()[1:]
    if len(parents) > 1:
        out = git(repo, "diff-tree", "--no-commit-id", "--name-status", "-r",
                  "--cc", commit)
        entries = []
        for line in out.splitlines():
            if "\t" in line:
                st, path = line.split("\t", 1)
                entries.append(("D" if "D" in st.upper() else "M", path))
        return entries
    return parse_z(git(repo, "diff-tree", "--no-commit-id", "--name-status", "-r",
                       "-M", "-z", "--root", commit))


def judge_push(repo, remote, lines):
    """lines: (local_ref, local_sha, remote_ref, remote_sha) as git gives them.
    Returns (offenders, notes). Raises if git cannot say what would be sent."""
    offenders, notes = [], []
    for _local_ref, local, remote_ref, remote_sha in lines:
        if local == ZERO:
            offenders.append(("DELETE", remote_sha[:7], "", remote_ref,
                              ["deletes %s on %s - a remote branch deletion is not "
                               "a documentation push" % (remote_ref, remote)]))
            continue
        for c in commits_sent(repo, remote, local, remote_sha):
            entries = paths_of(repo, c)
            refusals = judge(entries) if entries else []
            label = "SUBJECT" if c == local else "CARRIED"
            if refusals:
                subj = git(repo, "log", "-1", "--format=%s", c).strip()
                offenders.append((label, c[:7], subj, remote_ref, refusals))
            elif c == local:
                notes.append("The commit this push names for %s, %s, is inside the "
                             "documentation set." % (remote_ref, c[:7]))
    return offenders, notes


def report(offenders, notes, remote, w=sys.stderr.write):
    if not offenders:
        return 0
    w("\nPUSH REFUSED - %d commit(s) or ref(s) outside the documentation set would "
      "go to %s\n\n" % (len(offenders), remote))
    for label, sha, subj, ref, refusals in sorted(offenders, key=lambda o: ORDER[o[0]]):
        w("  %-8s %s  %s  (%s)\n" % (label, sha, subj, ref))
        w("           %s\n" % WHAT[label])
        for r in refusals[:SHOW]:
            w("           - %s\n" % r)
        if len(refusals) > SHOW:
            w("           ... and %d more\n" % (len(refusals) - SHOW))
    for n in notes:
        w("\n  %s\n" % n)
    w("\nSleven's hand passes it: git push --no-verify. No desk uses that (rule 2).\n\n")
    return 1


def main(argv):
    if "--self-test" in argv:
        return self_test()
    remote = argv[0] if argv else "origin"
    lines = []
    for raw in sys.stdin.buffer.read().decode("utf-8", "replace").splitlines():
        f = raw.split()
        if len(f) == 4:
            lines.append(tuple(f))
        elif f:
            sys.stderr.write("push_guard: unreadable ref line %r. Refusing.\n" % raw)
            return 2
    try:
        offenders, notes = judge_push(os.getcwd(), remote, lines)
    except Exception as exc:                        # noqa: BLE001 - fail closed
        sys.stderr.write("push_guard: could not read what this push would send "
                         "(%s). Refusing.\n" % exc)
        return 2
    return report(offenders, notes, remote)


# --- self-test: real pushes into a throwaway bare repository -----------------

def self_test():
    import shutil
    import stat
    import tempfile

    me = os.path.abspath(__file__).replace("\\", "/")
    py = sys.executable.replace("\\", "/")
    tmp = tempfile.mkdtemp(prefix="cc-push-guard-")
    results = []

    def run(cwd, *args):
        r = subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True)
        return r.returncode, (r.stdout + r.stderr).decode("utf-8", "replace")

    def check(label, cond):
        results.append(bool(cond))
        print("  %-7s %s" % ("caught" if cond else "MISSED", label))

    try:
        bare = os.path.join(tmp, "remote.git")
        work = os.path.join(tmp, "work")
        hooks = os.path.join(tmp, "hooks")
        os.makedirs(hooks)
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", bare], check=True)
        subprocess.run(["git", "init", "-q", "-b", "main", work], check=True)
        for k, v in (("user.name", "plant"), ("user.email", "plant@example.invalid"),
                     ("core.hooksPath", hooks.replace("\\", "/")),
                     ("commit.gpgsign", "false"), ("core.autocrlf", "false")):
            run(work, "config", k, v)
        run(work, "remote", "add", "origin", bare.replace("\\", "/"))
        with open(os.path.join(hooks, "pre-push"), "w", encoding="utf-8",
                  newline="\n") as fh:
            fh.write('#!/bin/sh\nexec "%s" "%s" "$@"\n' % (py, me))

        def commit(files, msg):
            for rel, body in files.items():
                p = os.path.join(work, *rel.split("/"))
                os.makedirs(os.path.dirname(p), exist_ok=True)
                with open(p, "w", encoding="utf-8", newline="\n") as fh:
                    fh.write(body)
                run(work, "add", rel)
            code, out = run(work, "commit", "-q", "-m", msg)
            if code != 0:
                raise RuntimeError("plant commit failed: " + out)
            return run(work, "rev-parse", "HEAD")[1].strip()

        def push(*args):
            return run(work, "push", "origin", *args)

        def reset_main():
            run(work, "checkout", "-q", "main")
            run(work, "reset", "-q", "--hard", "origin/main")

        def labelled(out, label, sha):
            return ("%-8s %s" % (label, sha[:7])) in out

        # 1. docs-only, under docs/ AND claude/ - the whole set, via the import
        commit({"docs/a.md": "a\n", "claude/b.md": "b\n"}, "docs one")
        code, out = push("main")
        check("1  docs-only push (docs/ and claude/) passes", code == 0)

        # 2. the 183a239 shape: a code commit carried under a docs tip
        x = commit({"src/app.py": "x = 1\n"}, "code X")
        t = commit({"docs/c.md": "c\n"}, "docs tip")
        code, out = push("main")
        check("2  code commit under a docs tip is refused, labelled CARRIED",
              code != 0 and labelled(out, "CARRIED", x)
              and "rides along" in out and not labelled(out, "SUBJECT", t)
              and "The commit this push names" in out)
        reset_main()

        # 3. a single code commit is the SUBJECT
        x2 = commit({"src/two.py": "y = 2\n"}, "code only")
        code, out = push("main")
        check("3  a single code commit is refused, labelled SUBJECT",
              code != 0 and labelled(out, "SUBJECT", x2))
        reset_main()

        # 4. CLAUDE.md is NEVER
        commit({"CLAUDE.md": "rules\n"}, "rules")
        code, out = push("main")
        check("4  a CLAUDE.md commit is refused", code != 0 and "CLAUDE.md" in out)
        reset_main()

        # 5. new branches: docs passes, a carried code commit does not
        run(work, "checkout", "-q", "-b", "feat-docs")
        commit({"docs/d.md": "d\n"}, "docs on a branch")
        code, out = push("feat-docs")
        check("5a a new docs-only branch passes", code == 0)
        reset_main()
        run(work, "checkout", "-q", "-b", "feat-code")
        y = commit({"src/y.py": "y\n"}, "code on a branch")
        commit({"docs/e.md": "e\n"}, "docs on top")
        code, out = push("feat-code")
        check("5b a new branch carrying a code commit is refused, CARRIED",
              code != 0 and labelled(out, "CARRIED", y))
        reset_main()

        # 6. a rename inside docs/ is refused
        run(work, "mv", "docs/a.md", "docs/a2.md")
        run(work, "commit", "-q", "-m", "rename")
        code, out = push("main")
        check("6  a rename inside docs/ is refused", code != 0 and "RENAME" in out)
        reset_main()

        # 7. the override exists and works
        z = commit({"src/z.py": "z\n"}, "code Z")
        code, out = push("--no-verify", "main")
        remote_main = run(bare, "rev-parse", "main")[1].strip()
        check("7  --no-verify passes it (the documented override)",
              code == 0 and remote_main == z)
        run(work, "fetch", "-q", "origin")

        # 8. a docs tip that is a MERGE bringing in a code commit
        run(work, "checkout", "-q", "-b", "side")
        w = commit({"src/w.py": "w\n"}, "code W on side")
        run(work, "checkout", "-q", "main")
        commit({"docs/f.md": "f\n"}, "docs on main")
        run(work, "merge", "-q", "--no-ff", "side", "-m", "merge side")
        m = run(work, "rev-parse", "HEAD")[1].strip()
        code, out = push("main")
        check("8  a merge is not blamed for its parent's code; that commit is CARRIED",
              code != 0 and labelled(out, "CARRIED", w) and not labelled(out, "SUBJECT", m))
        reset_main()

        # 9. an evil merge: the resolution itself adds code
        run(work, "checkout", "-q", "-b", "side2")
        commit({"docs/g.md": "g\n"}, "docs on side2")
        run(work, "checkout", "-q", "main")
        commit({"docs/h.md": "h\n"}, "docs on main again")
        run(work, "merge", "-q", "--no-ff", "--no-commit", "side2")
        with open(os.path.join(work, "evil.py"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("import os\n")
        run(work, "add", "evil.py")
        run(work, "commit", "-q", "-m", "evil merge")
        e = run(work, "rev-parse", "HEAD")[1].strip()
        code, out = push("main")
        check("9  an evil merge is refused as SUBJECT, naming the file",
              code != 0 and labelled(out, "SUBJECT", e) and "evil.py" in out)
        reset_main()

        # 10. deleting a remote branch
        code, out = push(":feat-docs")
        check("10 a remote branch deletion is refused, by name",
              code != 0 and "remote branch deletion" in out)
    except Exception as exc:                        # noqa: BLE001
        check("the self-test itself ran (%s: %s)" % (type(exc).__name__, exc), False)
    finally:
        def _force(func, path, _info):
            os.chmod(path, stat.S_IWRITE)
            func(path)
        shutil.rmtree(tmp, onerror=_force)

    caught, total = sum(results), len(results)
    print("\n%d of %d planted pushes landed." % (caught, total))
    if caught != total or total < 11:
        print("SELF-TEST FAILED - this guard missed a push it must refuse or "
              "refused one it must pass. It must not be trusted.")
        return 3
    print("SELF-TEST PASSED. Exiting NON-ZERO on purpose: the suite requires a "
          "control's self-test to be rejected. This is the GOOD outcome.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
