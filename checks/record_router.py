#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
record_router.py - B2, the router. Each actionable B1 gap becomes a letter, through
inbox/, to the desk that WROTE the document holding it. Answers come back through
the mail unchanged. REAL FILING ENABLED 2026-09-13 on Architecture's word, after the
dry run and the 56-to-76 gate (`..._three-architecture-rulings-b2-enable-cadence-...`
and `..._build-now-b2-live-cutoff-boot-uncommitted.md`). It files after every full
sweep, from the same post-sweep hook as B1 (`record_audit.py --route`), handed B1's
result in-process so B1 never runs twice. It never gates anything.

RULE16: INDEPENDENT - the routing truth is each document's OWN declaration of who
wrote it, read by the exact forms below; the gaps come from B1, which reads the
filesystem; the memory of what was filed is the mail itself. OWNERS.md is not read:
it answers who MAY WRITE a path, and B2 needs who WROTE a document (Architecture,
2026-09-13, correcting its own earlier order).

Built to `claude/PROPOSAL_b2-the-router-2026-09-13.md`, amendment 2.

WHAT IS ROUTED     B1's ROUTABLE rows. Rows inside letters are "unfixable by design"
                   (the text above ANSWERS: is never edited) and are never filed.
                   Transient citations and class3 are not routed either.
WHERE              the declared writer's tray. The project-store kind always goes to
                   Architecture - only C1 can open the store. An Owner declaration
                   goes to Architecture, NEVER to owner: his tray is for decisions,
                   and a router able to post into it is a machine generating his work.
NEVER GUESSED      no declaration -> UNDETERMINED; two writers -> AMBIGUOUS, both
                   named (rule 19); a writer the table does not know -> UNKNOWN,
                   named and reported, never silently undetermined. All three go to
                   Architecture, labelled, and are counted separately.
NEVER TWICE        each row carries `Router-key: <source> | <citation>`. Before filing,
                   every .md under correspondence/, inbox/ and _needs_review/ is read
                   for those lines; a key found anywhere is never filed again. THE
                   MEMORY IS THE MAIL - there is no state file to drift from it.
WRITES             only inbox/<date>_memo_<tray>_router-....md, and only on a real
                   run (--file, or the post-sweep hook). It never moves, edits or deletes.

THE DECLARATION FORMS - exact, and positional so a quoted ruling is not a writer:
    header (first 40 lines)   `from   <Name>, ...`   `From: <Name>`   `**<Name>, 20YY-MM-DD`
    signature (last 15 lines) `*<Name>, 20YY-MM-DD...*`
NORMALISATION, STATED (rule 17): one trailing parenthetical is a signature and is
dropped, as the mail router does (`Build (Code)` is Build); the name is then compared
case-insensitively. The table below has no two keys differing only by case.

Rule 15: every text open states encoding="utf-8".

Usage:
    python checks/record_router.py              dry run over the real record (default)
    python checks/record_router.py --file       real filing, one letter per tray, into inbox/
    python checks/record_audit.py --route       B1, then B2 filing on its result (the hook)
    python checks/record_router.py --self-test
"""
import collections
import hashlib
import io
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# writer name (normalised) -> canonical writer
WRITER = {"build": "build", "code": "build",
          "architecture": "architecture", "c1": "architecture",
          "design": "design", "research": "research", "audit": "audit",
          "owner": "owner", "sleven": "owner"}
# canonical writer -> tray. Owner is NEVER a destination.
TRAY = {"build": "build", "architecture": "architecture", "design": "design",
        "research": "research", "audit": "audit", "owner": "architecture"}
TITLE = {"build": "Build", "architecture": "Architecture", "design": "Design",
         "research": "Research", "audit": "Audit"}

HEAD_LINES, TAIL_LINES = 40, 15
F_FROM = re.compile(r"(?im)^\s{0,8}from\s{2,}([^,\n]+?)\s*(?:,.*)?$")
F_FROM_COLON = re.compile(r"(?im)^From:\s*(.+?)\s*$")
F_BYLINE = re.compile(r"(?m)^\*\*([^*,\n]{1,40}), 20\d\d-\d\d-\d\d")
F_SIGNATURE = re.compile(r"(?m)^\*([^*,\n]{1,40}), 20\d\d-\d\d-\d\d")
RE_SIGNATURE = re.compile(r"^(.*[^ \t\n\f\r])[ \t\n\f\r]+(\([^()]*\))[ \t\n\f\r]*$")
RE_KEY = re.compile(r"(?m)^Router-key:\s*(.+?)\s*$")
STORE_KINDS = ("claude/ path, no file", "project store")


def _read(path):
    with io.open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def _name(raw):
    raw = raw.strip()
    m = RE_SIGNATURE.match(raw)
    return (m.group(1) if m else raw).strip()


def declared(text):
    """-> ordered list of declared writer names (normalised, original case kept)."""
    lines = text.splitlines()
    head = "\n".join(lines[:HEAD_LINES])
    tail = "\n".join(lines[-TAIL_LINES:])
    names = []
    for rx, blob in ((F_FROM, head), (F_FROM_COLON, head), (F_BYLINE, head),
                     (F_SIGNATURE, tail)):
        for m in rx.finditer(blob):
            n = _name(m.group(1))
            if n and n not in names:
                names.append(n)
    return names


def writer_of(text):
    """-> (tray, label). Never guessed: UNDETERMINED / AMBIGUOUS / UNKNOWN."""
    names = declared(text)
    if not names:
        return "architecture", "UNDETERMINED - no declaration"
    unknown = [n for n in names if n.lower() not in WRITER]
    if unknown:
        return "architecture", "UNKNOWN WRITER - %s (a form outside the table)" % ", ".join(unknown)
    writers = sorted({WRITER[n.lower()] for n in names})
    if len(writers) > 1:
        return "architecture", "AMBIGUOUS - declares %s" % " and ".join(names)
    w = writers[0]
    # ONE RULE, ONE PLACE: the tray comes from TRAY, Owner's included. The label only
    # says so. (A second, hard-coded branch here made TRAY's owner row dead code - a
    # mutation of it survived, 2026-09-13.)
    label = "declared %s" % names[0]
    if w == "owner":
        label += " - routed to Architecture, never to owner"
    return TRAY[w], label


def row_key(row):
    return "%s | %s" % (row[0], row[1])


def mail_keys(root):
    """Every Router-key line anywhere in the mail -> set of relative files holding it."""
    found = collections.defaultdict(set)
    for base in ("correspondence", "inbox", "_needs_review"):
        top = os.path.join(root, base)
        for dp, _dn, fn in os.walk(top):
            for f in fn:
                if not f.lower().endswith(".md"):
                    continue
                p = os.path.join(dp, f)
                try:
                    text = _read(p)
                except OSError:
                    continue
                for m in RE_KEY.finditer(text):
                    found[m.group(1)].add(os.path.relpath(p, root).replace("\\", "/"))
    return found


def drift_check(root):
    """Every destination in the table must be a tray on disk. -> missing trays."""
    return sorted(t for t in set(TRAY.values())
                  if not os.path.isdir(os.path.join(root, "correspondence", "open", t)))


def plan(res, root):
    """-> dict with per-tray NEW rows, and every count named by its surface."""
    keys = mail_keys(root)
    out = {"new": collections.defaultdict(list), "already_filed": 0,
           "answered_not_dispositioned": [], "labels": collections.Counter(),
           "routable": len(res["routable"]), "in_letters": len(res.get("in_letters", []))}
    for row in res["routable"]:
        src, _tok, kind = row[0], row[1], row[2]
        if kind.startswith(STORE_KINDS):
            tray, label = "architecture", "project store - only C1 can open it"
        else:
            try:
                text = _read(os.path.join(root, *src.split("/")))
            except OSError:
                text = ""
            tray, label = writer_of(text)
        out["labels"][label.split(" - ")[0]] += 1
        k = row_key(row)
        if k in keys:
            out["already_filed"] += 1
            if any(p.startswith("correspondence/answered/") for p in keys[k]):
                out["answered_not_dispositioned"].append((k, sorted(keys[k])))
            continue
        out["new"][tray].append((row, label))
    return out


def compose(tray, rows, when):
    stamp = time.strftime("%Y-%m-%d", time.localtime(when))
    hhmm = time.strftime("%H%M", time.localtime(when))
    name = "%s_memo_%s_router-b1-found-%d-citation-gaps-%s.md" % (stamp, tray, len(rows), hhmm)
    L = ["# Memo", "",
         "To:      %s" % TITLE[tray],
         "From:    Build (router)",
         "Subject: B1 found %d citation gap(s) in documents you wrote" % len(rows),
         "Status:  Open", "",
         "**Filed by `checks/record_router.py` (B2) from B1's record audit.** Each gap below sits",
         "in a document that declares you wrote it, or is labelled if it does not say.", "",
         "**Reply under `ANSWERS:`, one line per row, in exactly one of these forms.** B3",
         "(`checks/record_repair.py`) reads them; anything else is named MALFORMED, never guessed.", "",
         "    `<source>` | `<token>` | <class> | <note>      HISTORY - class is one of",
         "                                                   example future absence history fix-pending",
         "    MOVED `<source>` | `<token>` -> `<new path>`   B3 repoints it, on Architecture's word",
         "    DEFECT `<source>` | `<token>`                  fixed at the source; B1 stops reporting it", ""]
    for row, label in rows:
        L += ["---", "",
              "    source    %s" % row[0],
              "    citation  %s" % row[1],
              "    kind      %s%s" % (row[2], ("  [%s]" % row[3]) if row[3] else ""),
              "    routed    %s" % label,
              "Router-key: %s" % row_key(row), ""]
    L += ["*Build (router), %s.*" % stamp, ""]
    return name, "\n".join(L)


def file_letters(root, letters):
    """Write each (name, text) into root/inbox/ and nowhere else. Refuses a name that exists."""
    written = []
    for name, text in letters:
        p = os.path.join(root, "inbox", name)
        if os.path.exists(p):
            raise FileExistsError(p)
        with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        written.append(p)
    return written


def summary(p):
    print("B2 router: %d routable rows; %d inside letters (unfixable by design, never filed)"
          % (p["routable"], p["in_letters"]))
    print("  already filed (a Router-key found in the mail): %d" % p["already_filed"])
    for label, n in p["labels"].most_common():
        print("  routed as %-40s %d" % (label, n))
    for tray in sorted(p["new"]):
        print("  NEW for %-14s %d" % (tray, len(p["new"][tray])))
    print("  ANSWERED, NOT DISPOSITIONED: %d" % len(p["answered_not_dispositioned"]))
    for k, files in p["answered_not_dispositioned"]:
        print("     %s  (%s)" % (k, files[0]))
    print("CANNOT: judge whether a gap matters; route a gap B1 does not find; see the project store.")


def run(res, root, do_file):
    """Route one B1 result. Writes only when do_file is True. -> exit code."""
    missing = drift_check(root)
    if missing:
        print("DRIFT - the desk table routes to tray(s) not on disk: %s. Nothing planned." % missing)
        return 1
    p = plan(res, root)
    summary(p)
    now = time.time()
    letters = [compose(tray, p["new"][tray], now) for tray in sorted(p["new"])]
    if not do_file:
        for name, text in letters:
            print("\n" + "=" * 78 + "\nDRY RUN - would file inbox/%s\n" % name + "=" * 78)
            print(text)
        print("\nDRY RUN - nothing was written.")
        return 0
    written = file_letters(root, letters)
    for p_ in written:
        print("FILED inbox/%s" % os.path.basename(p_))
    print("B2 router: filed %d letter(s) - %s" % (
        len(written), ", ".join("%s %d" % (t, len(p["new"][t])) for t in sorted(p["new"])) or "nothing new"))
    return 0


def main(argv):
    if "--self-test" in argv:
        return self_test()
    sys.path.insert(0, HERE)
    import record_audit as ra
    return run(ra.audit(ROOT, links=False), ROOT, "--file" in argv)


# ------------------------------------------------------------------ self-test
def _tree_hash(root):
    h = hashlib.sha256()
    for dp, _dn, fn in sorted(os.walk(root)):
        for f in sorted(fn):
            p = os.path.join(dp, f)
            h.update(os.path.relpath(p, root).encode("utf-8"))
            with open(p, "rb") as fh:
                h.update(fh.read())
    return h.hexdigest()


def self_test():
    import shutil
    import tempfile

    results = []

    def check(ok, what):
        results.append(bool(ok))
        print("  %-7s %s" % ("caught" if ok else "MISSED", what))

    root = tempfile.mkdtemp(prefix="cc-router-selftest-")
    try:
        for t in ("architecture", "build", "design", "research", "audit", "owner"):
            os.makedirs(os.path.join(root, "correspondence", "open", t))
        for d in ("correspondence/answered", "inbox", "_needs_review", "claude"):
            os.makedirs(os.path.join(root, *d.split("/")), exist_ok=True)

        def put(rel, body):
            with io.open(os.path.join(root, *rel.split("/")), "w", encoding="utf-8", newline="\n") as fh:
                fh.write(body)

        put("claude/c1doc.md", "# X\n\n    from    C1, architecture, 2026-09-13\n\nbody\n")
        put("claude/builddoc.md", "# X\n\n    from      Build (Code), 2026-09-13\n\nbody\n")
        put("claude/nodecl.md", "# X\n\nno declaration anywhere\n")
        put("claude/ownerdoc.md", "# X\n\n**Owner (Sleven), 2026-09-13** ruled this\n")
        put("claude/twodoc.md", "# X\n\n    from    C1, 2026-09-13\n\nbody\n\n*Build (Code), 2026-09-13.*\n")
        put("claude/quoted.md", "# NEXT\n" + "filler\n" * 50
            + "**Sleven, 2026-09-12** - a quoted ruling, deep in the body\n" + "more\n" * 30)
        put("claude/grok.md", "# X\n\n    from    Grok, 2026-09-13\n")
        put("claude/storedoc.md", "# X\n\n    from      Build (Code), 2026-09-13\n")
        put("correspondence/answered/2026-09-13_memo_build_router-old.md",
            "# Memo\n\nRouter-key: claude/builddoc.md | docs/old.md\n")
        put("inbox/2026-09-13_memo_architecture_router-pending.md",
            "# Memo\n\nRouter-key: claude/c1doc.md | docs/pending.md\n")

        R = lambda src, tok, kind="absent": (src, tok, kind, "", True)   # noqa: E731
        res = {"routable": [R("claude/builddoc.md", "docs/a.md"),
                            R("claude/c1doc.md", "docs/b.md"),
                            R("claude/nodecl.md", "docs/c.md"),
                            R("claude/ownerdoc.md", "docs/d.md"),
                            R("claude/twodoc.md", "docs/e.md"),
                            R("claude/quoted.md", "docs/f.md"),
                            R("claude/grok.md", "docs/g.md"),
                            R("claude/storedoc.md", "claude/X.md",
                              "claude/ path, no file - project store or dead, NOT decidable from here"),
                            R("claude/builddoc.md", "docs/old.md"),
                            R("claude/c1doc.md", "docs/pending.md")],
               "in_letters": [("correspondence/open/build/x.md", "docs/z.md", "absent", "", True)]}

        before = _tree_hash(root)
        p = plan(res, root)
        lab = {row[1]: label for tray in p["new"] for row, label in p["new"][tray]}
        tray_of = {row[1]: tray for tray in p["new"] for row, _l in p["new"][tray]}

        check(tray_of.get("docs/a.md") == "build", "2  `from Build (Code)` goes to build")
        check(tray_of.get("docs/b.md") == "architecture" and lab["docs/b.md"].startswith("declared C1"),
              "1  a C1 declaration goes to architecture")
        check(tray_of.get("docs/c.md") == "architecture" and lab["docs/c.md"].startswith("UNDETERMINED"),
              "3  no declaration -> architecture, labelled UNDETERMINED")
        check(tray_of.get("docs/d.md") == "architecture" and "owner" not in p["new"],
              "4  an Owner declaration -> architecture, NEVER owner")
        check(lab.get("docs/e.md", "").startswith("AMBIGUOUS") and "C1" in lab["docs/e.md"]
              and "Build" in lab["docs/e.md"], "13 two writers -> AMBIGUOUS, both named")
        check(lab.get("docs/f.md", "").startswith("UNDETERMINED"),
              "15 a quoted **Sleven, date ruling deep in the body is not a declaration")
        check(lab.get("docs/g.md", "").startswith("UNKNOWN WRITER") and "Grok" in lab["docs/g.md"],
              "16 a writer outside the table is reported UNKNOWN, not silently undetermined")
        check(tray_of.get("claude/X.md") == "architecture" and lab["claude/X.md"].startswith("project store"),
              "5  the project-store kind -> architecture, whoever wrote the document")
        check("docs/old.md" not in tray_of and "docs/pending.md" not in tray_of,
              "8/9 a key already in answered/ or in inbox/ is never filed again")
        check(len(p["answered_not_dispositioned"]) == 1
              and p["answered_not_dispositioned"][0][0] == "claude/builddoc.md | docs/old.md",
              "11 an answered key B1 still reports is ANSWERED, NOT DISPOSITIONED")
        check(p["in_letters"] == 1 and all(not r[0].startswith("correspondence/")
                                           for t in p["new"] for r, _l in p["new"][t]),
              "6  a row inside a letter is counted, never routed")
        check(_tree_hash(root) == before, "12 planning (the dry run) writes nothing")

        letters = [compose(t, p["new"][t], time.time()) for t in sorted(p["new"])]
        text = letters[0][1]
        check(all(h in text for h in ("To:", "From:    Build (router)", "Subject:", "Status:  Open",
                                      "Router-key: ")), "   a letter carries To/From/Subject/Status and its keys")
        check(all(f in text for f in ("`<source>` | `<token>` | <class> | <note>",
                                      "MOVED `<source>` | `<token>` -> `<new path>`",
                                      "DEFECT `<source>` | `<token>`")),
              "19 a letter's reply instructions are B3's three exact forms")
        check(run(res, root, False) == 0 and _tree_hash(root) == before,
              "17 run() without --file (the dry run) writes nothing")
        outside = {k: v for k, v in [(d, None) for d in ("correspondence", "claude", "_needs_review")]}
        hashes = {d: _tree_hash(os.path.join(root, d)) for d in outside}
        inbox_before = set(os.listdir(os.path.join(root, "inbox")))
        rc = run(res, root, True)
        filed = set(os.listdir(os.path.join(root, "inbox"))) - inbox_before
        check(rc == 0 and len(filed) == len(p["new"])
              and {n.split("_memo_")[1].split("_")[0] for n in filed} == set(p["new"]),
              "18 run() with --file writes one letter per tray into inbox/")
        check(all(_tree_hash(os.path.join(root, d)) == hashes[d] for d in outside),
              "   filing writes only into inbox/")
        p2 = plan(res, root)
        check(not p2["new"], "10 a second run after filing files nothing")

        os.rmdir(os.path.join(root, "correspondence", "open", "research"))
        check(drift_check(root) == ["research"], "14 a table destination with no tray on disk is DRIFT")
    except Exception as exc:                        # noqa: BLE001
        check(False, "the self-test itself ran (%s: %s)" % (type(exc).__name__, exc))
    finally:
        shutil.rmtree(root, ignore_errors=True)

    caught, total = sum(results), len(results)
    print("\n%d of %d planted cases landed." % (caught, total))
    if caught != total or total < 19:
        print("SELF-TEST FAILED - the router must not be trusted.")
        return 3
    print("SELF-TEST PASSED. Exiting NON-ZERO on purpose: the suite requires a control's "
          "self-test to be rejected. This is the GOOD outcome.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
