# -*- coding: utf-8 -*-
"""B1 - the record auditor and the link index. ONE PASS, TWO OUTPUTS. FLAGS ONLY.

Ordered by Sleven 2026-09-12 (`correspondence/open/build/2026-09-12_memo_build_b1-three-
rulings-build-now-owner-go.md`), built from
`claude/PROPOSAL_b1-the-record-auditor-and-the-link-index-2026-09-12.md`.

    python checks/record_audit.py              audit the repository; write the outputs
    python checks/record_audit.py --self-test  planted cases in a temp tree

OUTPUT A  logs/record_audit.md    the findings report (overwritten each run)
          logs/record_audit.json  a receipt: when, counts per class, cost
OUTPUT B  _links/                 one generated companion note per citing document,
                                  [[wikilinks]] Obsidian can graph. Gitignored, DERIVED.

IT NEVER GATES. It is not a _verify_* control, so no sweep counts it, and a real run
exits 0 whatever it finds. It runs after each sweep (checks/run_all_controls.py).
IT NEVER FIXES. It writes its report, its receipt and _links/, and nothing else. The
disposition ledger is written by the desk that owns each source document, never here.

ONE DEFINITION OF A CITATION. It imports check 6's own patterns (_BACKTICKED,
_REPO_PATH_SHAPE) from checks/file_checks.py rather than keeping a second copy.

RULE16: INDEPENDENT - the truth is the filesystem (does the path exist) and the
router's own log (where a letter was filed); the subject is what documents claim.
"""
import collections
import io
import json
import os
import re
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
for p in (HERE, REPO):
    if p not in sys.path:
        sys.path.insert(0, p)
from checks.file_checks import _BACKTICKED, _REPO_PATH_SHAPE   # noqa: E402

CUTOFF = "2026-09-12"                      # the citation convention was ruled this day
ABS_PREFIX = "c:/users/david/citizen-compass/"
RECORD_DIRS = ("claude", "docs", "design", "correspondence")
HISTORY_DIRS = ("docs/handoff_archive/",)  # history by definition, as check 1 prunes it
GENERATED = {"LATEST_HANDOFF.md", "BOOT.md"}
LIVING = {"CLAUDE.md", "NEXT.md", "OWNERS.md", "LIVE.md", "START-CODE.md",
          "README.md", "RECOVERY.md"}      # present state, always in scope
PRUNE = {".obsidian", "node_modules", "__pycache__", ".git", "images"}
INDEXED = ("claude", "docs", "design", "correspondence", "checks", "scripts", "tools",
           "watcher-go", "testing/_src")   # bounded; _to_delete/ deliberately NOT indexed
LEDGER = "claude/RECORD-AUDIT-DISPOSITIONS.md"
LEDGER_ROW = re.compile(r"^\s*`([^`]+)`\s*\|\s*`([^`]+)`\s*\|\s*"
                        r"(example|future|absence|history|fix-pending)\s*\|\s*(\S.*?)\s*$")
# A last path segment is a FILE only with an extension on this closed list; no dot means
# a folder; anything else (`findings_store.apply_run`) is a code reference. Rule 17.
FILE_EXTS = {"md", "py", "js", "mjs", "cjs", "json", "html", "css", "go", "mod", "sum",
             "ps1", "bat", "sh", "txt", "csv", "tsv", "glb", "gltf", "png", "jpg", "jpeg",
             "webp", "svg", "exe", "toml", "yaml", "yml", "log", "lock", "ini", "cfg",
             "xml", "pdf", "zip", "canvas", "base", "db", "sql", "env", "tmp", "diff"}
DATE_IN_NAME = re.compile(r"(20\d\d-\d\d-\d\d)")
DATE_HDR = re.compile(r"(?im)^Date:\s*(20\d\d-\d\d-\d\d)")
KIND_CLAUDE = "claude/ path, no file - project store or dead, NOT decidable from here"


def _read(path):
    with io.open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def doc_date(path, text):
    ds = DATE_IN_NAME.findall(os.path.basename(path))
    if len(set(ds)) > 1:
        return "AMBIGUOUS"
    if ds:
        return ds[-1]
    m = DATE_HDR.search(text[:4000])
    return m.group(1) if m else None


def citation(tok, tops):
    """A backticked token is a repository citation, or None. Exact, no inference."""
    t = tok.strip().replace("\\", "/")
    if t.lower().startswith(ABS_PREFIX):
        t = t[len(ABS_PREFIX):]
    if "*" in t or "..." in t or t.startswith(("http", "www.")):
        return None
    if "/" not in t:
        return t if t in LIVING else None
    if not _REPO_PATH_SHAPE.match(t) or t.split("/")[0] not in tops:
        return None
    last = t.rstrip("/").split("/")[-1]
    if "." in last and last.rsplit(".", 1)[1].lower() not in FILE_EXTS:
        return None
    return t


def audit(root, links=True):
    """One pass over the record at `root`. Returns the result dict; writes nothing
    unless links=True, and then only under root/_links (report writing is main's)."""
    t0 = time.perf_counter()
    j = lambda *a: os.path.join(root, *a)          # noqa: E731
    docs = []
    # DOT-NAMES ARE NEVER RECORD: the first real run read `.aider.chat.history.md`, a
    # gitignored tool chat log at the root, as a project document.
    for d in RECORD_DIRS:
        for dp, dn, fn in os.walk(j(d)):
            dn[:] = [x for x in dn if x not in PRUNE and not x.startswith(".")]
            docs += [os.path.relpath(os.path.join(dp, f), root).replace("\\", "/")
                     for f in fn if f.endswith(".md") and not f.startswith(".")]
    docs += [f for f in sorted(os.listdir(root))
             if f.endswith(".md") and not f.startswith(".") and f not in GENERATED
             and os.path.isfile(j(f))]
    docs = sorted(d for d in docs if d != LEDGER)   # the ledger is INPUT, not record
    tops = {e for e in os.listdir(root) if not e.startswith(".")}

    filed = collections.defaultdict(set)            # the router's own record, exact
    logp = j("logs", "inbox_watcher.log")
    if os.path.exists(logp):
        rx = re.compile(r"\] \u2713 (\S+) -> (\S+?)(?: \(|$)")
        for line in io.open(logp, encoding="utf-8", errors="replace"):
            m = rx.search(line)
            if m:
                dest = m.group(2).replace("\\", "/")
                if dest.lower().startswith(ABS_PREFIX):
                    dest = dest[len(ABS_PREFIX):]
                filed[m.group(1)].add(dest)
    names = collections.defaultdict(list)           # bounded; candidates, never a pick
    for r in INDEXED:
        for dp, dn, fn in os.walk(j(r)):
            dn[:] = [x for x in dn if x not in PRUNE]
            for f in fn:
                names[f].append(os.path.relpath(os.path.join(dp, f), root).replace("\\", "/"))

    edges = collections.defaultdict(set)
    rows = []                                   # (src, token, kind, detail, in_scope)
    scope = collections.Counter()
    cites = via_log = via_mail = 0
    transient = []                              # (source, citation) into a tray
    for src in docs:
        try:
            text = _read(j(src))
        except OSError:
            scope["unreadable"] += 1
            continue
        d = doc_date(src, text)
        if src.startswith(HISTORY_DIRS):
            ins, lab = False, "history folder"
        elif "/" not in src and src in LIVING:
            ins, lab = True, "in scope"
        elif d is None:
            ins, lab = False, "undated"
        elif d == "AMBIGUOUS":
            ins, lab = False, "ambiguous date"
        else:
            ins, lab = (d >= CUTOFF), ("in scope" if d >= CUTOFF else "before cutoff")
        scope[lab] += 1
        for m in _BACKTICKED.finditer(text):
            t = citation(m.group(1), tops)
            if t is None:
                continue
            cites += 1
            tgt = t.rstrip("/")
            # A citation INTO a tray from a document that is not itself a letter points at
            # a transient location: answering the letter moves it (Architecture, 2026-09-12).
            # Listed on its own, whether or not it resolves today; never repointed here.
            if ins and t.startswith("correspondence/open/") and not src.startswith("correspondence/"):
                transient.append((src, t))
            if os.path.exists(j(tgt)):
                if tgt != src and os.path.isfile(j(tgt)):
                    edges[src].add(tgt)             # files only: a folder is not a node
                continue
            base = os.path.basename(tgt)
            # A LETTER MOVES WHEN IT IS ANSWERED - to its sender's tray, then to answered/.
            # So a citation into correspondence/ resolves by EXACT filename wherever the
            # mail system has filed it now; only a name found nowhere is dead, and a name
            # filed in two places is AMBIGUOUS, never picked (Architecture, 2026-09-12).
            corr = (sorted(p for p in names.get(base, []) if p.startswith("correspondence/"))
                    if tgt.startswith("correspondence/") else [])
            if len(corr) == 1:
                edges[src].add(corr[0])
                via_mail += 1
                continue
            ls = text.rfind("\n", 0, m.start()) + 1
            le = text.find("\n", m.end())
            line = text[ls:le if le >= 0 else len(text)]
            if "project store" in line.lower():
                kind, det = "project store, named on the line", ""
            elif len(corr) > 1:
                kind, det = "letter filed under that name in %d places - AMBIGUOUS" % len(corr), "; ".join(corr[:3])
            elif tgt.startswith("inbox/") and base in filed:
                live = sorted(x for x in filed[base] if os.path.isfile(j(x)))
                if len(live) == 1:
                    edges[src].add(live[0])         # resolved by the router's own log
                    via_log += 1
                    continue
                kind = ("inbox letter, AMBIGUOUS - filed more than once" if live
                        else "inbox letter, filed then moved on")
                det = "; ".join(live or sorted(filed[base]))
            elif names.get(base):
                c = names[base]
                kind = ("same filename exists elsewhere - not proof it moved" if len(c) == 1
                        else "same filename exists in %d places - AMBIGUOUS" % len(c))
                det = "; ".join(c[:3])
            elif tgt.startswith("claude/"):
                kind, det = KIND_CLAUDE, ""
            else:
                kind, det = "absent", ""
            rows.append((src, t, kind, det, ins))

    # the disposition ledger: exact key (source, token); a row matching nothing is STALE
    ledger, ledger_state = {}, "absent - no dispositions recorded yet"
    if os.path.isfile(j(LEDGER)):
        ledger_state = "read"
        for line in _read(j(LEDGER)).splitlines():
            m = LEDGER_ROW.match(line)
            if m:
                ledger[(m.group(1), m.group(2))] = (m.group(3), m.group(4))
    found = [r for r in rows if r[4]]
    keys = {(r[0], r[1]) for r in found}
    dispositioned = [r for r in found if (r[0], r[1]) in ledger]
    findings = [r for r in found if (r[0], r[1]) not in ledger]
    stale = sorted(k for k in ledger if k not in keys)
    # ONE MIXED NUMBER IS THE DEFECT (Architecture, 2026-09-13). The text above a
    # letter's ANSWERS: line may never be edited, so a dead citation INSIDE a letter
    # cannot be fixed by anyone, ever. It is counted apart and named for what it is;
    # only the rest is work a desk can do.
    in_letters = [r for r in findings if r[0].startswith("correspondence/")]
    routable = [r for r in findings if not r[0].startswith("correspondence/")]

    c3, c3_state = [], "performed"
    try:
        import _verify_correspondence as vc
        if os.path.isdir(j("correspondence")):
            c3 = [f for f in vc.audit(j("correspondence"), True)[0]
                  if "ANSWERS" in f or "CLOSED:" in f]
        else:
            c3_state = "NOT PERFORMED - no correspondence/ folder"
    except Exception as e:                      # noqa: BLE001 - reported, never a pass
        c3_state = "NOT PERFORMED - %s: %s" % (type(e).__name__, e)
    nxt = j("NEXT.md")
    dw = len(re.findall(r"(?m)^\*\*DONE-WHEN\*\*", _read(nxt))) if os.path.isfile(nxt) else None

    lk = {"sources": len(edges), "edges": sum(len(v) for v in edges.values()),
          "written": 0, "unchanged": 0, "moved_aside": 0}
    if links:
        lk.update(write_links(root, edges))
    return {"root": root, "documents": len(docs), "scope": dict(scope), "citations": cites,
            "resolved_via_log": via_log, "resolved_via_mail": via_mail,
            "transient": sorted(set(transient)), "unresolved": len(rows),
            "baseline": [r for r in rows if not r[4]], "findings": findings,
            "in_letters": in_letters, "routable": routable,
            "dispositioned": dispositioned, "stale": stale, "ledger_state": ledger_state,
            "class3": c3, "class3_state": c3_state, "done_when_lines": dw,
            "links": lk, "edges": {k: sorted(v) for k, v in edges.items()},
            "seconds": round(time.perf_counter() - t0, 2)}


def _wl(path):
    return path[:-3] if path.endswith(".md") else path


def write_links(root, edges):
    """Companion notes: rewritten only when their content changes; a note no source
    produces any more is MOVED to _to_delete/ (rule 1), never deleted."""
    d = os.path.join(root, "_links")
    os.makedirs(d, exist_ok=True)
    want = {}
    for src, tgts in edges.items():
        want[src.replace("/", "__")] = (
            "<!-- generated by checks/record_audit.py after each sweep; never hand-edited -->\n"
            "source: [[%s]]\n\ncites:\n%s\n" % (_wl(src), "\n".join("- [[%s]]" % _wl(t) for t in sorted(tgts))))
    written = unchanged = moved = 0
    stamp = time.strftime("%Y%m%d_%H%M%S")
    for name in sorted(os.listdir(d)):
        if name not in want:
            aside = os.path.join(root, "_to_delete", "_links_stale_" + stamp)
            os.makedirs(aside, exist_ok=True)
            shutil.move(os.path.join(d, name), os.path.join(aside, name))
            moved += 1
    for name, body in want.items():
        p = os.path.join(d, name)
        if os.path.isfile(p) and _read(p) == body:
            unchanged += 1
            continue
        with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
        written += 1
    return {"written": written, "unchanged": unchanged, "moved_aside": moved}


def report(res, when):
    f = res["findings"]
    kinds = collections.Counter(r[2] for r in f)
    L = ["# RECORD AUDIT - REPORT ONLY. It never gates a deploy and never fixes anything.", "",
         "Generated %s by checks/record_audit.py, after the sweep. Run time %.2f s." % (when, res["seconds"]), "",
         "## WHAT WAS READ",
         "    %d documents - claude/, docs/, design/, correspondence/ and the root .md files" % res["documents"]]
    L += ["    %-16s %d" % (k, v) for k, v in sorted(res["scope"].items(), key=lambda kv: -kv[1])]
    L += ["    %d citations: %d resolve on disk, %d through the router's log, %d where the mail "
          "system filed the letter, %d do not"
          % (res["citations"], res["citations"] - res["unresolved"] - res["resolved_via_log"]
             - res["resolved_via_mail"], res["resolved_via_log"], res["resolved_via_mail"],
             res["unresolved"]), "",
          "## BASELINE (history, undated or before %s) - a count, never rows" % CUTOFF,
          "    %d unresolved citations in %d documents." % (len(res["baseline"]), len({r[0] for r in res["baseline"]})), "",
          "## TRANSIENT CITATIONS - %d, from a non-letter document into correspondence/open/"
          % len(res["transient"]),
          "    Answering a letter moves it, so these go dead without anyone touching the citing"
          " document. Flagged, never repointed."]
    L += ["    %s  ->  `%s`" % tr for tr in res["transient"]]
    rt, lt = res["routable"], res["in_letters"]
    L += ["",
          "## 1. DEAD CITATIONS - %d ROUTABLE in %d documents; %d INSIDE LETTERS, unfixable by "
          "design, in %d letters; %d more dispositioned (%s)"
          % (len(rt), len({r[0] for r in rt}), len(lt), len({r[0] for r in lt}),
             len(res["dispositioned"]), LEDGER),
          "    Two numbers, never one (Architecture, 2026-09-13): the text above a letter's ANSWERS:",
          "    line may never be edited, so a dead citation inside a letter is true and permanently",
          "    unactionable. Only the routable rows are work a desk can do.", "",
          "### routable - work a desk can do"]
    L += ["      %4d  %s" % (n, k) for k, n in collections.Counter(r[2] for r in rt).most_common()]
    for src in sorted({r[0] for r in rt}):
        L.append("  %s" % src)
        L += ["      `%s`  -  %s%s" % (r[1], r[2], "  [%s]" % r[3] if r[3] else "") for r in rt if r[0] == src]
    L += ["", "### inside letters - unfixable by design, never routed"]
    for src in sorted({r[0] for r in lt}):
        L.append("  %s" % src)
        L += ["      `%s`  -  %s%s" % (r[1], r[2], "  [%s]" % r[3] if r[3] else "") for r in lt if r[0] == src]
    L += ["", "## STALE DISPOSITIONS - %d ledger row(s) matching no current finding" % len(res["stale"])]
    L += ["    `%s` | `%s`" % k for k in res["stale"]]
    L += ["    ledger: %s" % res["ledger_state"], "",
          "## 2. SATISFIED BUT OPEN - NOT PERFORMED",
          "    NEXT.md's %s DONE-WHEN lines are prose; deciding one is met is judgement." % res["done_when_lines"], "",
          "## 3. CLOSED WITHOUT A MARKER - %s, %d found" % (res["class3_state"], len(res["class3"]))]
    L += ["    - " + x[:200] for x in res["class3"][:20]]
    L += ["", "## 4. PROJECT-ONLY DOCUMENTS - ONE-SIDED",
          "    This machine cannot read the claude.ai project store; the %d '%s' rows are the only"
          % (kinds.get(KIND_CLAUDE, 0), KIND_CLAUDE),
          "    view from here, and they are not a complete answer.", "",
          "## LINK INDEX (_links/) - %(sources)d companion notes, %(edges)d edges; "
          "%(written)d written, %(unchanged)d unchanged, %(moved_aside)d moved aside" % res["links"], "",
          "## WHAT THIS CANNOT SEE",
          "    - the claude.ai project store; whether a DONE-WHEN is satisfied",
          "    - citations written as prose rather than as a backticked path",
          "    - a citation naming a thing to say it does not exist, until its owner dispositions it",
          "    - documents outside claude/, docs/, design/, correspondence/ and the root, as sources", ""]
    return "\n".join(L)


def main(argv):
    if "--self-test" in argv:
        return self_test()
    when = time.strftime("%Y-%m-%d %H:%M:%S")
    res = audit(REPO, links=True)
    os.makedirs(os.path.join(REPO, "logs"), exist_ok=True)
    with io.open(os.path.join(REPO, "logs", "record_audit.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(report(res, when))
    receipt = {"at": when, "documents": res["documents"], "citations": res["citations"],
               "resolved_via_log": res["resolved_via_log"],
               "resolved_via_mail": res["resolved_via_mail"], "transient": len(res["transient"]),
               "baseline": len(res["baseline"]),
               "findings_routable": len(res["routable"]),
               "findings_in_letters_unfixable_by_design": len(res["in_letters"]),
               "dispositioned": len(res["dispositioned"]),
               "stale_dispositions": len(res["stale"]), "class3": len(res["class3"]),
               "class3_state": res["class3_state"], "links": res["links"], "seconds": res["seconds"]}
    with io.open(os.path.join(REPO, "logs", "record_audit.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(receipt, fh, indent=1)
    print("record audit: %d routable + %d inside letters (unfixable by design), %d dispositioned, "
          "%d stale, %d baseline; %d companion notes (%d written); %.2f s - logs/record_audit.md"
          % (receipt["findings_routable"], receipt["findings_in_letters_unfixable_by_design"],
             receipt["dispositioned"], receipt["stale_dispositions"],
             receipt["baseline"], res["links"]["sources"], res["links"]["written"], res["seconds"]))
    # B2 ON THIS RESULT, in-process, so B1 never runs twice (the post-sweep hook passes
    # --route). The router files letters into inbox/ only; whatever it does, this audit's
    # report, receipt and exit code are unchanged.
    if "--route" in argv:
        try:
            import record_router
            rc = record_router.run(res, REPO, True)
            if rc != 0:
                print("B2 router: FAILED (exit %d) - the audit is unaffected" % rc)
        except Exception as exc:                # noqa: BLE001 - reported, never gates
            print("B2 router: NOT RUN (%s: %s) - the audit is unaffected" % (type(exc).__name__, exc))
    return 0                                    # report only: it never gates


# ------------------------------------------------------------------ self-test
def self_test():
    fails = []

    def check(ok, what):
        print("  %-6s %s" % ("ok" if ok else "FAIL", what))
        if not ok:
            fails.append(what)

    def put(root, rel, body):
        p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(p) or root, exist_ok=True)
        with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)

    root = tempfile.mkdtemp(prefix="record_audit_selftest_")
    try:
        # inbox/ exists in the real repository, so it must exist here too - without
        # it no `inbox/...` token is a citation at all (the first self-test run showed it)
        for d in ("claude", "docs/sub", "docs/handoff_archive", "design", "checks", "logs", "inbox"):
            os.makedirs(os.path.join(root, d), exist_ok=True)
        put(root, "docs/real.md", "x\n")
        put(root, "claude/moved.md", "x\n")
        put(root, "claude/twice.md", "x\n")
        put(root, "design/twice.md", "x\n")
        put(root, "correspondence/open/build/letter.md", "x\n")
        put(root, "logs/inbox_watcher.log",
            "[2026-09-12 10:00:00] \u2713 letter.md -> correspondence\\open\\build\\letter.md (memo)\n")
        put(root, "CLAUDE.md", "See `docs/real.md`, `docs/gone.md` and the folder `docs/sub`.\n")
        put(root, "docs/NOTE_old-2026-08-01.md", "It was `docs/gone.md`.\n")
        put(root, "docs/handoff_archive/20260912_1_2026-09-12_u.md", "It was `docs/gone.md`.\n")
        put(root, "claude/NOTE_a-2026-09-12.md",
            "Filed as `inbox/letter.md`; also `inbox/nolog.md`; the call `checks/mod.func`.\n"
            "The design (project store: `claude/DESIGN_x.md`).\n"
            "Now at `docs/moved.md`, and `docs/twice.md`.\n")
        put(root, "claude/X_2026-09-12_2026-09-13.md", "`docs/gone.md`\n")

        put(root, ".aider.chat.history.md", "A tool's own log citing `docs/gone.md`.\n")
        # the mail system moves a letter when it is answered (Architecture, 2026-09-12)
        put(root, "correspondence/answered/moved-letter.md", "x\n")
        put(root, "correspondence/open/owner/twice-letter.md", "x\n")
        put(root, "correspondence/answered/twice-letter.md", "x\n")
        put(root, "correspondence/open/build/2026-09-12_memo_x.md",
            "See `correspondence/open/architecture/moved-letter.md`, "
            "`correspondence/open/architecture/gone-letter.md` and "
            "`correspondence/open/architecture/twice-letter.md`.\n")
        put(root, "claude/NOTE_b-2026-09-12.md", "The rule cites `correspondence/open/build/letter.md`.\n")
        a = audit(root, links=True)
        rows = {(r[0], r[1]): r[2] for r in a["findings"]}
        mx = "correspondence/open/build/2026-09-12_memo_x.md"
        check((mx, "correspondence/open/architecture/moved-letter.md") not in rows
              and "correspondence/answered/moved-letter.md" in a["edges"].get(mx, []),
              "12 a letter cited at its old tray path, now in answered/, is NOT dead")
        check(rows.get((mx, "correspondence/open/architecture/gone-letter.md")) == "absent",
              "12b a letter filed nowhere IS dead")
        check(str(rows.get((mx, "correspondence/open/architecture/twice-letter.md"))).startswith(
              "letter filed under that name in 2 places"), "12c a letter filed in two places is AMBIGUOUS")
        check(("claude/NOTE_b-2026-09-12.md", "correspondence/open/build/letter.md") in a["transient"]
              and not any(s == mx for s, _ in a["transient"]),
              "13 a non-letter citing into a tray is TRANSIENT; a letter doing so is not")
        check(not any(r[0].startswith(".") for r in a["findings"] + a["baseline"]),
              "11 a root dotfile (a tool's own log) is never read as record")
        check(rows.get(("CLAUDE.md", "docs/gone.md")) == "absent",
              "1  an in-scope dead citation is a row")
        check(not any(r[0].startswith(("docs/NOTE_old", "docs/handoff_archive")) for r in a["findings"])
              and len(a["baseline"]) >= 2, "2  the same citation in pre-cutoff and history documents is baseline only")
        check(("claude/NOTE_a-2026-09-12.md", "inbox/letter.md") not in rows and a["resolved_via_log"] == 1
              and "correspondence/open/build/letter.md" in a["edges"].get("claude/NOTE_a-2026-09-12.md", []),
              "3  a letter the router log filed is GREEN and an edge")
        check(rows.get(("claude/NOTE_a-2026-09-12.md", "inbox/nolog.md")) == "absent",
              "3b an inbox path with no log line is a row")
        check(not any(t == "checks/mod.func" for _, t in rows), "4  a dotted code reference is not a citation")
        check(rows.get(("claude/NOTE_a-2026-09-12.md", "claude/DESIGN_x.md")) == "project store, named on the line",
              "5  'project store' on the line is its own kind")
        check(rows.get(("claude/NOTE_a-2026-09-12.md", "docs/moved.md")) == "same filename exists elsewhere - not proof it moved",
              "6a one same-name candidate is reported, never called moved")
        check(rows.get(("claude/NOTE_a-2026-09-12.md", "docs/twice.md")) == "same filename exists in 2 places - AMBIGUOUS",
              "6b two candidates are AMBIGUOUS, none picked")
        check("docs/real.md" in a["edges"].get("CLAUDE.md", []) and "docs/sub" not in a["edges"].get("CLAUDE.md", []),
              "8  a file citation is an edge; a folder citation is not")
        with io.open(os.path.join(root, "_links", "CLAUDE.md"), encoding="utf-8") as fh:
            check("- [[docs/real]]" in fh.read(), "8b the edge is written into the source's companion note")
        check(a["scope"].get("ambiguous date") == 1, "9  a filename with two dates is counted as ambiguous")
        check(any(r[0] == mx for r in a["in_letters"])
              and all(r[0].startswith("correspondence/") for r in a["in_letters"])
              and not any(r[0].startswith("correspondence/") for r in a["routable"])
              and ("CLAUDE.md", "docs/gone.md") in {(r[0], r[1]) for r in a["routable"]},
              "14 a dead citation inside a letter is counted apart; one elsewhere is routable")
        rep = report(a, "self-test")
        check("INSIDE LETTERS, unfixable by" in rep and "ROUTABLE in" in rep,
              "14b the headline names both surfaces - never one mixed number")

        put(root, LEDGER, "`CLAUDE.md` | `docs/gone.md` | example | a planted example\n"
                          "`docs/none.md` | `docs/nothing.md` | history | matches nothing\n")
        b = audit(root, links=True)
        check(("CLAUDE.md", "docs/gone.md") not in {(r[0], r[1]) for r in b["findings"]}
              and len(b["dispositioned"]) == 1, "7  a disposition takes its finding out of the rows")
        check(b["stale"] == [("docs/none.md", "docs/nothing.md")], "7b a disposition matching nothing is STALE")
        check(b["links"]["written"] == 0 and b["links"]["unchanged"] == b["links"]["sources"],
              "10 an unchanged index rewrites nothing")
        os.remove(os.path.join(root, "claude", "NOTE_a-2026-09-12.md"))
        c = audit(root, links=True)
        check(c["links"]["moved_aside"] == 1 and not os.path.exists(
              os.path.join(root, "_links", "claude__NOTE_a-2026-09-12.md")),
              "10b a companion no source produces is moved aside, not deleted")
        check(os.path.isdir(os.path.join(root, "_to_delete")), "10c the moved note is in _to_delete/")
    finally:
        shutil.rmtree(root, ignore_errors=True)    # the self-test's OWN temp tree
    print("\nSELF-TEST %s - %d failure(s)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
