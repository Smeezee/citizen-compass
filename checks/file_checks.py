"""
Checkers that need only the filesystem + git - no database, no network.
Deliberately stdlib-only (no psycopg2/sqlalchemy/requests imports) so
these can run anywhere Python 3 exists, including environments with no
network access and no project venv (this is exactly how they were first
run for real - see LATEST_HANDOFF.md 2026-07-30).

Each function takes `repo_root: Path` and returns list[Finding].
"""

import csv
import io
import json
import re
import subprocess
from pathlib import Path

from checks.framework import Finding

# --- data integrity (file-based) --------------------------------------------


def naming_convention_typo_check(repo_root: Path) -> list[Finding]:
    """For every ship test fixture, confirm the hardpoints.json's own
    internal ship_slug matches its folder name. This is exactly the class
    of bug caught manually in Cutlass Black (folder: cutlass-black,
    internal ship_slug: cuttlass_black) - this checker would have caught
    it automatically."""
    findings = []
    ships_dir = repo_root / "tests" / "testing-site" / "ships"
    if not ships_dir.is_dir():
        return [Finding("naming_convention_typo", None, "LIMITATION", f"{ships_dir} does not exist")]

    for ship_dir in sorted(p for p in ships_dir.iterdir() if p.is_dir()):
        hp_path = ship_dir / "hardpoints.json"
        if not hp_path.exists():
            findings.append(
                Finding("naming_convention_typo", ship_dir.name, "LIMITATION", "no hardpoints.json yet - nothing to check")
            )
            continue
        try:
            data = json.loads(hp_path.read_text(encoding="utf-8"))
        except Exception as e:
            findings.append(Finding("naming_convention_typo", ship_dir.name, "DEFECT", f"hardpoints.json is not valid JSON: {e}"))
            continue

        slug = data.get("ship_slug")
        if slug != ship_dir.name:
            findings.append(
                Finding(
                    "naming_convention_typo",
                    ship_dir.name,
                    "DEFECT",
                    f"hardpoints.json ship_slug={slug!r} does not match its folder name {ship_dir.name!r}",
                )
            )
        else:
            findings.append(Finding("naming_convention_typo", ship_dir.name, "PASS", "ship_slug matches folder name"))
    return findings


def placeholder_null_density_check(repo_root: Path) -> list[Finding]:
    """Flag hardpoints whose label is a bare placeholder (no size digit, a
    single generic word) rather than real pulled data - the same class of
    gap Cutlass Black's missile rack had before real data existed. This is
    a WARNING (backlog item), not a DEFECT - a placeholder is expected
    until real data is sourced, not a bug."""
    findings = []
    ships_dir = repo_root / "tests" / "testing-site" / "ships"
    if not ships_dir.is_dir():
        return []

    generic_labels = {"missiles", "missile", "weapon", "turret", "gun"}
    for ship_dir in sorted(p for p in ships_dir.iterdir() if p.is_dir()):
        hp_path = ship_dir / "hardpoints.json"
        if not hp_path.exists():
            continue
        try:
            data = json.loads(hp_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        placeholders = [
            hp["name"] for hp in data.get("hardpoints", [])
            if isinstance(hp.get("label"), str) and hp["label"].strip().lower() in generic_labels
        ]
        if placeholders:
            findings.append(
                Finding(
                    "placeholder_null_density",
                    ship_dir.name,
                    "WARNING",
                    f"{len(placeholders)} hardpoint(s) still have a generic placeholder label, not real "
                    f"pulled size/rack data: {placeholders}",
                )
            )
        else:
            findings.append(Finding("placeholder_null_density", ship_dir.name, "PASS", "no placeholder labels found"))
    return findings


def broken_asset_references_check(repo_root: Path) -> list[Finding]:
    """Parse HTML/JS for local src=/href= references and confirm each file
    actually exists on disk. This is exactly the class of bug the
    sc-logo-mirai.png issue was (referenced a .png that only existed as
    .svg) - this checker would have caught it automatically instead of by
    manual review."""
    findings = []
    ref_pattern = re.compile(r'(?:src|href)\s*=\s*["\']([^"\'#?]+)["\']')
    html_files = list(repo_root.glob("static/*.html")) + list(repo_root.glob("tests/testing-site/**/*.html"))

    for html_file in html_files:
        try:
            text = html_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for ref in ref_pattern.findall(text):
            if ref.startswith(("http://", "https://", "//", "data:", "mailto:")):
                continue
            # Several pages build markup at runtime via JS template
            # literals (e.g. `html += '<a href="${escapeHtml(v.path)}">'`
            # inside a <script> block) - "${...}" is a JS interpolation
            # placeholder, not a literal path, and will never exist on
            # disk. Confirmed by inspecting the actual real-repo matches
            # this checker's first real run against the live repo
            # produced (2026-07-30) - a real false-positive, not a
            # hypothetical one. Any other {{ }} / {% %} templating syntax
            # gets the same treatment for the same reason.
            if "${" in ref or "{{" in ref or "{%" in ref:
                continue
            # Resolve /static/... references from repo root; relative
            # references from the HTML file's own directory.
            target = (repo_root / ref.lstrip("/")) if ref.startswith("/") else (html_file.parent / ref)
            try:
                resolved = target.resolve()
            except Exception:
                continue
            if not resolved.exists():
                findings.append(
                    Finding(
                        "broken_asset_references",
                        str(html_file.relative_to(repo_root)),
                        "DEFECT",
                        f"references {ref!r} which does not exist on disk (resolved: {resolved})",
                    )
                )

    if not any(f.result == "DEFECT" for f in findings):
        findings.append(Finding("broken_asset_references", None, "PASS", f"checked {len(html_files)} HTML files, no broken local references found"))
    return findings


def orphaned_test_fixture_check(repo_root: Path) -> list[Finding]:
    """Cross-check tests/testing-site/ships/* fixture folders against
    tests/testing-site/data/ships-master.json - a fixture folder with no
    matching registry entry (or vice versa) is worth a human look."""
    findings = []
    ships_dir = repo_root / "tests" / "testing-site" / "ships"
    master_path = repo_root / "tests" / "testing-site" / "data" / "ships-master.json"
    if not ships_dir.is_dir() or not master_path.exists():
        return [Finding("orphaned_test_fixture", None, "LIMITATION", "ships dir or ships-master.json not found")]

    fixture_slugs = {p.name for p in ships_dir.iterdir() if p.is_dir()}
    try:
        master = json.loads(master_path.read_text(encoding="utf-8"))
    except Exception as e:
        return [Finding("orphaned_test_fixture", None, "DEFECT", f"ships-master.json is not valid JSON: {e}")]

    master_slugs = {entry.get("slug") for entry in master if isinstance(entry, dict) and entry.get("slug")}

    fixtures_without_registry_entry = fixture_slugs - master_slugs
    if fixtures_without_registry_entry:
        findings.append(
            Finding(
                "orphaned_test_fixture",
                None,
                "WARNING",
                f"{len(fixtures_without_registry_entry)} test fixture folder(s) have no matching "
                f"ships-master.json entry: {sorted(fixtures_without_registry_entry)}",
            )
        )
    else:
        findings.append(Finding("orphaned_test_fixture", None, "PASS", "every fixture folder has a matching ships-master.json entry"))
    return findings


def missing_or_corrupt_3d_model_check(repo_root: Path) -> list[Finding]:
    """For every ship folder under sc-ships/, confirm model.glb exists, is
    non-empty, and starts with the correct glTF-binary magic header
    (b'glTF' at offset 0). Stdlib-only - doesn't parse the actual mesh
    (that needs Blender's bpy, not available outside Blender's own Python),
    just confirms the file is present and not obviously corrupt. Also
    flags a missing preview image (image.webp) as a WARNING - cosmetic,
    doesn't block the 3D model, but worth tracking in the same pass."""
    findings = []
    ships_dir = repo_root / "sc-ships"
    if not ships_dir.is_dir():
        return [Finding("missing_or_corrupt_3d_model", None, "LIMITATION", f"{ships_dir} does not exist")]

    for ship_dir in sorted(p for p in ships_dir.iterdir() if p.is_dir() and not p.name.startswith(".")):
        model_path = ship_dir / "model.glb"
        image_path = ship_dir / "image.webp"

        # MODEL_SOURCE.txt records that this ship's model was copied from a
        # sibling with the same chassis. Read it BEFORE judging the model, so
        # a borrowed model is reported as the limitation it is.
        source_path = ship_dir / "MODEL_SOURCE.txt"
        source_note = None
        if source_path.exists():
            try:
                source_note = " ".join(
                    source_path.read_text(encoding="utf-8").split()
                )[:300] or "(MODEL_SOURCE.txt present but empty)"
            except Exception as e:
                source_note = f"(MODEL_SOURCE.txt unreadable: {e})"

        if not model_path.exists():
            findings.append(Finding(
                "missing_or_corrupt_3d_model", ship_dir.name, "DEFECT",
                f"{model_path.relative_to(repo_root)} does not exist"
            ))
        elif model_path.stat().st_size == 0:
            findings.append(Finding(
                "missing_or_corrupt_3d_model", ship_dir.name, "DEFECT",
                f"{model_path.relative_to(repo_root)} exists but is 0 bytes (empty file)"
            ))
        else:
            try:
                with open(model_path, "rb") as f:
                    header = f.read(4)
                if header != b"glTF":
                    findings.append(Finding(
                        "missing_or_corrupt_3d_model", ship_dir.name, "DEFECT",
                        f"{model_path.relative_to(repo_root)} does not start with the glTF-binary magic "
                        f"header - likely corrupt or not actually a valid .glb file"
                    ))
                elif source_note is not None:
                    # A model copied from a sibling chassis is NOT this ship's
                    # own art. Reporting PASS here would silently conflate
                    # "has a model" with "has its own model" - four ships are
                    # currently in exactly that state, and a plain existence
                    # check cannot tell the difference.
                    findings.append(Finding(
                        "missing_or_corrupt_3d_model", ship_dir.name, "LIMITATION",
                        f"model.glb is valid but was copied from a sibling chassis, per "
                        f"MODEL_SOURCE.txt: {source_note}"
                    ))
                else:
                    findings.append(Finding(
                        "missing_or_corrupt_3d_model", ship_dir.name, "PASS",
                        "model.glb present, non-empty, valid glTF-binary header"
                    ))
            except Exception as e:
                findings.append(Finding(
                    "missing_or_corrupt_3d_model", ship_dir.name, "WARNING",
                    f"could not read {model_path.relative_to(repo_root)}: {e}"
                ))

        if not image_path.exists():
            findings.append(Finding(
                "missing_preview_image", ship_dir.name, "WARNING",
                f"{image_path.relative_to(repo_root)} missing (cosmetic, does not block the 3D model)"
            ))

    return findings


# --- encoding hygiene ---------------------------------------------------------

# A text-mode open() with no encoding= uses the platform default. On Windows
# that is cp1252, which cannot represent the characters in real Star Citizen
# ship names. This has broken this pipeline FOUR separate times:
#   * ccpp.py, three call sites
#   * checks/framework.py:72 - the fallback log's own WRITER, which would have
#     destroyed a finding the moment any subject contained a non-ASCII name.
#     It survived only because json.dumps escapes to ASCII by default.
#   * a throwaway diagnostic script, which is why "it's only a quick script"
#     is not an exemption.
# `tok.yai` (with a macron) is a shipping product, not an edge case.
#
# Uses tokenize rather than a regex, and that choice was forced by evidence.
#
# The regex version passed a 16-case rule-12 fixture and then produced false
# positives the moment it met the real repo: it flagged this function's OWN
# DOCSTRING (which names the three calls) and every line of
# _verify_missing_encoding.py's fixture table (where the bad call sites are
# quoted STRINGS, not code). A linter that cries wolf on its own test data
# teaches people to skim it, which is precisely the harm this is meant to
# prevent.
#
# tokenize makes the distinction structural instead of textual: strings,
# docstrings and comments arrive as their own token types and are never
# mistaken for a call. That is a correctness difference, not a tidiness one.
_TEXT_CALLS = ("open", "read_text", "write_text")
_BINARY_MODE = re.compile(r"^[rwxa]\+?b\+?$")


def _text_mode_calls(source: str):
    """Yield (line_no, func_name, arg_tokens) for every open/read_text/
    write_text CALL in `source`. Occurrences inside strings, docstrings and
    comments are structurally excluded."""
    import io
    import tokenize

    toks = [
        t for t in tokenize.generate_tokens(io.StringIO(source).readline)
        if t.type not in (tokenize.NL, tokenize.NEWLINE, tokenize.INDENT,
                          tokenize.DEDENT, tokenize.COMMENT)
    ]
    for i, tok in enumerate(toks):
        if tok.type != tokenize.NAME or tok.string not in _TEXT_CALLS:
            continue
        # A definition is not a call site.
        if i and toks[i - 1].type == tokenize.NAME and toks[i - 1].string == "def":
            continue
        if i + 1 >= len(toks) or toks[i + 1].string != "(":
            continue
        depth, args, k = 0, [], i + 1
        while k < len(toks):
            t = toks[k]
            if t.type == tokenize.OP and t.string in "([{":
                depth += 1
            elif t.type == tokenize.OP and t.string in ")]}":
                depth -= 1
                if depth == 0:
                    break
            elif depth >= 1:
                args.append(t)
            k += 1
        yield tok.start[0], tok.string, args

_ENCODING_SKIP_DIRS = {
    ".git", "__pycache__", "venv", ".venv", "node_modules", "_to_delete",
    "data-layer", "sc-ships", "testing", "models", "releases", "inbox",
    "docs", "logs",
}


def missing_encoding_check(repo_root: Path) -> list[Finding]:
    """Flag every text-mode open()/read_text()/write_text() in this project's
    own Python that does not state encoding= explicitly.

    Self-enforcing version of the standing rule, so that "specify the
    encoding" stops being something anyone has to remember."""
    findings = []
    scanned = 0

    for py in sorted(repo_root.rglob("*.py")):
        rel = py.relative_to(repo_root)
        # Dotfile directories are skipped wholesale. .claude/worktrees/ holds
        # full copies of the repo, which would otherwise report every finding
        # twice - and duplicated findings are the thing this whole order is
        # about removing.
        if any(part.startswith(".") or part in _ENCODING_SKIP_DIRS
               for part in rel.parts[:-1]):
            continue
        try:
            text = py.read_text(encoding="utf-8")
        except Exception as e:
            findings.append(Finding("missing_encoding", str(rel), "WARNING",
                                     f"could not read file to scan it: {e}"))
            continue
        scanned += 1
        lines = text.splitlines()

        try:
            calls = list(_text_mode_calls(text))
        except Exception as e:
            # Unparseable source is reported, never silently skipped - a file
            # this checker could not read is exactly where a bad call would hide.
            findings.append(Finding("missing_encoding", str(rel), "WARNING",
                                     f"could not tokenize to scan it: {type(e).__name__}: {e}"))
            continue

        for line_no, func, args in calls:
            import tokenize as _tk

            has_encoding = any(
                t.type == _tk.NAME and t.string == "encoding" for t in args
            )
            binary = any(
                t.type == _tk.STRING and _BINARY_MODE.match(t.string.strip("\"'"))
                for t in args
            )
            if has_encoding or binary:
                continue
            src = lines[line_no - 1].strip() if line_no <= len(lines) else ""
            findings.append(Finding(
                "missing_encoding", f"{rel}:{line_no}", "DEFECT",
                f"{func}() with no explicit encoding= - defaults to cp1252 on "
                f"Windows and will raise on non-ASCII ship names: {src[:120]}"
            ))

    if not findings:
        findings.append(Finding("missing_encoding", None, "PASS",
                                 f"scanned {scanned} Python files, every text open specifies an encoding"))
    return findings


# SOURCE, NOT CAPTURED OUTPUT. A .txt holding a previous run's console can
# carry the byte legitimately - as a RECORD of the defect - and flagging that
# forever would train everybody to ignore this checker.
_CONTROL_SCAN_EXT = {".py", ".mjs", ".js", ".html", ".css", ".json", ".md",
                     ".ps1", ".toml", ".go"}
_CONTROL_SKIP_DIRS = {
    ".git", "__pycache__", "venv", ".venv", "node_modules", "_to_delete",
    "sc-ships", "models", "vendor", "external-sources", "derived",
    "handoff_archive", "logs", "_deploy", "fixtures",
}
# Tab, newline and carriage return are text.
_CONTROL_ALLOWED = {0x09, 0x0A, 0x0D}
# THE DEFECT SET IS NOT "EVERY CONTROL CHARACTER", AND THE DISTINCTION IS THE
# POINT. These five are exactly the ones a language's escape processing can
# silently produce FROM A LETTER - \a \b \f \v \e - so a source file carrying
# one is a mangled escape rather than a decision. Anything else in C0 can be a
# deliberate choice: roundtrip.js joins its fields on 0x01 on purpose, and
# calling that a defect would train everybody to ignore this checker, which is
# how a check stops being one.
_CONTROL_MANGLED = {0x07, 0x08, 0x0B, 0x0C, 0x1B}


def control_bytes_check(repo_root: Path) -> list[Finding]:
    """Flag any source file carrying a raw C0 control character.

    WHY THIS EXISTS, AND IT IS NOT HYGIENE.

    A regex written as `/\\bpinned\\b/` and passed through a tool that reads
    `\\b` as an escape becomes `/<0x08>pinned<0x08>/`. It is a VALID regular
    expression. It matches nothing. It is invisible in every editor, in `git
    diff`, and in a code review, because a terminal renders 0x08 as nothing at
    all.

    It has now happened four times in this repo in one session:

      _verify_sorts.mjs      /\\bpinned\\b/ - a FAILING assertion, on a correct
                             page. Announced itself.
      _verify_dim.mjs        /\\bhidden\\b/ - a PASSING assertion that could not
                             fail. Worse: it had already been reported as an ok.
      _loadout_harness.mjs   /<(div|button)\\b.../ - the tag parser matched
                             nothing, so a stub built to observe element
                             positions observed none.

    The second of those is the reason this is a machine check and not a habit.
    A byte that turns a check into a check-shaped no-op cannot be guarded by
    remembering to look for it, because looking is exactly what does not work.

    Proven in both directions by `checks/_verify_control_bytes.py`.
    """
    findings = []
    scanned = 0
    for path in sorted(repo_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in _CONTROL_SCAN_EXT:
            continue
        rel = path.relative_to(repo_root)
        if any(part.startswith(".") or part in _CONTROL_SKIP_DIRS
               for part in rel.parts[:-1]):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            # Not decodable as UTF-8 is a different finding and not this one's.
            continue
        scanned += 1
        # SPLIT ON \n ONLY, NOT str.splitlines(). splitlines() treats 0x0B and
        # 0x0C as line boundaries, so a vertical tab or a form feed is consumed
        # as whitespace between lines and never appears INSIDE one - which made
        # this checker blind to two of the five bytes it exists to find. Caught
        # by the control planting all five and getting three back.
        for n, line in enumerate(text.replace("\r\n", "\n").split("\n"), 1):
            seen = sorted({ord(c) for c in line
                           if (ord(c) < 0x20 and ord(c) not in _CONTROL_ALLOWED)
                           or ord(c) == 0x7F})
            if not seen:
                continue
            shown = line
            for b in seen:
                shown = shown.replace(chr(b), "<0x%02X>" % b)
            mangled = [b for b in seen if b in _CONTROL_MANGLED]
            other = [b for b in seen if b not in _CONTROL_MANGLED]
            if mangled:
                findings.append(Finding(
                    "control_bytes", f"{rel}:{n}", "DEFECT",
                    "escape-mangled control character(s) %s - a regex written "
                    "through a tool that reads backslash-b as an escape "
                    "becomes 0x08, which is a valid pattern matching NOTHING "
                    "and is invisible in every editor and every diff: %s"
                    % (", ".join("0x%02X" % b for b in mangled),
                       shown.strip()[:120])))
            if other:
                findings.append(Finding(
                    "control_bytes", f"{rel}:{n}", "WARNING",
                    "raw control character(s) %s in source - can be deliberate "
                    "(roundtrip.js joins fields on 0x01 on purpose), so "
                    "reported rather than failed: %s"
                    % (", ".join("0x%02X" % b for b in other),
                       shown.strip()[:120])))
    if not findings:
        findings.append(Finding(
            "control_bytes", None, "PASS",
            f"scanned {scanned} source files, none carries a raw control "
            f"character outside tab, newline and carriage return"))
    return findings


# --- ops/infra health --------------------------------------------------------


def log_growth_check(repo_root: Path, threshold_mb: int = 50) -> list[Finding]:
    findings = []
    logs_dir = repo_root / "logs"
    if not logs_dir.is_dir():
        return [Finding("log_growth", None, "LIMITATION", "logs/ does not exist yet")]
    for log_file in sorted(logs_dir.rglob("*")):
        if not log_file.is_file():
            continue
        size_mb = log_file.stat().st_size / (1024 * 1024)
        if size_mb > threshold_mb:
            findings.append(
                Finding("log_growth", str(log_file.relative_to(repo_root)), "WARNING", f"{size_mb:.1f} MB, over the {threshold_mb} MB threshold - check for runaway/unbounded growth")
            )
    if not findings:
        findings.append(Finding("log_growth", None, "PASS", f"no file under logs/ exceeds {threshold_mb} MB"))
    return findings


def backup_freshness_check(repo_root: Path, max_age_days: int = 7) -> list[Finding]:
    """Look for database backup files matching the convention recommended
    in this session's handoff (citizen_compass_backup_YYYYMMDD.dump) in a
    conventional backups/ folder. No backup mechanism has been set up yet
    as of 2026-07-30, so an absent folder is an expected LIMITATION, not a
    DEFECT - this checker's real value is surfacing when that stops being
    true and a backup starts silently going stale."""
    backups_dir = repo_root / "backups"
    if not backups_dir.is_dir():
        return [Finding("backup_freshness", None, "LIMITATION", "no backups/ folder exists yet - no backup mechanism set up as of 2026-07-30, see LATEST_HANDOFF.md")]

    import datetime

    dumps = sorted(backups_dir.glob("*.dump"))
    if not dumps:
        return [Finding("backup_freshness", None, "WARNING", "backups/ folder exists but contains no .dump files")]

    newest = max(dumps, key=lambda p: p.stat().st_mtime)
    age_days = (datetime.datetime.now().timestamp() - newest.stat().st_mtime) / 86400
    if age_days > max_age_days:
        return [Finding("backup_freshness", newest.name, "WARNING", f"newest backup is {age_days:.1f} days old, over the {max_age_days}-day freshness threshold")]
    return [Finding("backup_freshness", newest.name, "PASS", f"newest backup is {age_days:.1f} days old")]


def scheduled_task_health_check(repo_root: Path) -> list[Finding]:
    """Cannot actually query Windows Task Scheduler from this checker's
    environment (no Windows API access, confirmed - see LATEST_HANDOFF.md).
    Returns an honest LIMITATION finding rather than silently omitting this
    category or guessing a status."""
    return [
        Finding(
            "scheduled_task_health",
            "inbox_watcher Task Scheduler entry",
            "LIMITATION",
            "cannot check Task Scheduler state from this environment (no Windows Task Scheduler/process "
            "API access from the tools available to this checker) - run this check from a context with real "
            "Windows access (e.g. 'Get-ScheduledTask -TaskName *watcher*' in PowerShell) instead.",
        )
    ]


def duplicate_process_check(repo_root: Path) -> list[Finding]:
    """Detect duplicate writers - the failure this project has had twice.

    Two handoff generators ran against LATEST_HANDOFF.md for three days, each
    discarding tens of thousands of characters of the other's output; later,
    two sessions worked one layer. Both times the only visible symptom was a
    file that changed size for no apparent reason.

    THIS CHECKER USED TO BE UNCONDITIONAL. It returned the same LIMITATION
    every time - "cannot enumerate Windows processes from this environment" -
    which was true in the 2026-07-30 sandbox and has not been true since. It
    could not have detected a duplicate writer if there had been one, while
    still appearing in every run as though something had been checked. That is
    a check that cannot fail, so it now actually looks, and reports LIMITATION
    only when a command genuinely fails.

    Two writers are watched:
      * inbox_watcher.exe   - sole writer of LATEST_HANDOFF.md
      * run_checks          - sole writer of the findings tables
    """
    findings = []

    # --- 1. duplicate watcher processes ---
    try:
        proc = subprocess.run(["tasklist", "/fo", "csv", "/nh"],
                              capture_output=True, text=True, timeout=30)
        listed = proc.stdout or ""
    except Exception as e:
        listed = None
        findings.append(Finding("duplicate_process", "inbox_watcher.exe", "LIMITATION",
                                 f"could not run tasklist: {type(e).__name__}: {e}"))

    if listed is not None:
        count = sum(1 for line in listed.splitlines()
                    if line.lower().startswith('"inbox_watcher'))
        if count > 1:
            findings.append(Finding("duplicate_process", "inbox_watcher.exe", "DEFECT",
                                     f"{count} inbox_watcher processes are running. Two watchers on one "
                                     f"inbox silently overwrite each other's output - there must be exactly one."))
        elif count == 0:
            findings.append(Finding("duplicate_process", "inbox_watcher.exe", "WARNING",
                                     "no inbox_watcher process is running - the handoff pipeline is not "
                                     "being written by anything"))
        else:
            findings.append(Finding("duplicate_process", "inbox_watcher.exe", "PASS",
                                     "exactly 1 inbox_watcher process is running"))

    # --- 2. duplicate scheduled writers of the findings tables ---
    try:
        proc = subprocess.run(["schtasks", "/query", "/fo", "csv", "/v"],
                              capture_output=True, text=True, timeout=60)
        tasks_out = proc.stdout or ""
    except Exception as e:
        tasks_out = None
        findings.append(Finding("duplicate_process", "run_checks-schedule", "LIMITATION",
                                 f"could not run schtasks: {type(e).__name__}: {e}"))

    if tasks_out is not None:
        # Parsed as CSV against the named columns, NOT substring-matched.
        #
        # The first version filtered rows with `"disabled" not in line.lower()`
        # and produced a FALSE NEGATIVE against this very machine: the auditor
        # task's "Scheduled Task State" is "Enabled", but schtasks /v rows carry
        # the word "Disabled" in unrelated columns ("Idle Time", "Power
        # Management"), so the row was thrown away and the checker reported that
        # nothing was scheduled while a task was demonstrably registered and
        # running. A duplicate-writer detector that cannot see the writers is
        # worse than none, because it reports "exactly one" forever.
        writers = []
        try:
            rows = list(csv.reader(io.StringIO(tasks_out)))
            header = rows[0] if rows else []
            idx_run = next((i for i, h in enumerate(header)
                            if h.strip().lower() == "task to run"), None)
            idx_state = next((i for i, h in enumerate(header)
                              if "scheduled task state" in h.strip().lower()), None)
            if idx_run is None:
                raise ValueError("schtasks output has no 'Task To Run' column")
            for r in rows[1:]:
                if len(r) <= idx_run:
                    continue
                if "run_checks" not in r[idx_run].lower():
                    continue
                if idx_state is not None and len(r) > idx_state \
                        and r[idx_state].strip().lower() != "enabled":
                    continue
                writers.append(r[idx_run])
        except Exception as e:
            findings.append(Finding("duplicate_process", "run_checks-schedule", "LIMITATION",
                                     f"could not parse schtasks output: {type(e).__name__}: {e}"))
            tasks_out = None

    if tasks_out is not None:
        if len(writers) > 1:
            findings.append(Finding("duplicate_process", "run_checks-schedule", "DEFECT",
                                     f"{len(writers)} enabled scheduled tasks invoke run_checks. Two "
                                     f"schedules writing one findings table is exactly the duplicate-writer "
                                     f"failure this project has already had twice."))
        elif not writers:
            findings.append(Finding("duplicate_process", "run_checks-schedule", "WARNING",
                                     "no enabled scheduled task invokes run_checks - the auditor layer is "
                                     "not running unattended, so a quiet findings table proves nothing"))
        else:
            findings.append(Finding("duplicate_process", "run_checks-schedule", "PASS",
                                     "exactly 1 enabled scheduled task invokes run_checks"))

    return findings


# --- security/compliance -----------------------------------------------------

SECRET_PATTERNS = [
    (re.compile(r'AKIA[0-9A-Z]{16}'), "AWS access key"),
    (re.compile(r'-----BEGIN (RSA|OPENSSH|EC|DSA) PRIVATE KEY-----'), "private key"),
    (re.compile(r'(?i)(api[_-]?key|secret[_-]?key|password)\s*[:=]\s*["\'][^"\'\s]{8,}["\']'), "possible hardcoded credential"),
]


def secrets_in_repo_check(repo_root: Path) -> list[Finding]:
    """Grep tracked files for common secret patterns, and confirm .env
    itself isn't tracked by git."""
    findings = []
    try:
        tracked = subprocess.run(["git", "ls-files"], cwd=repo_root, capture_output=True, text=True, check=True).stdout.splitlines()
    except Exception as e:
        return [Finding("secrets_in_repo", None, "WARNING", f"could not list tracked files: {e}")]

    if ".env" in tracked:
        findings.append(Finding("secrets_in_repo", ".env", "DEFECT", ".env is tracked by git - it should be gitignored, it contains the real DATABASE_URL credential"))
    else:
        findings.append(Finding("secrets_in_repo", ".env", "PASS", ".env is not tracked by git"))

    text_extensions = {".py", ".js", ".json", ".env", ".md", ".yml", ".yaml", ".ini", ".cfg", ".go", ".html", ".ps1"}
    hits = 0
    for rel_path in tracked:
        path = repo_root / rel_path
        if path.suffix not in text_extensions or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for pattern, label in SECRET_PATTERNS:
            if pattern.search(text):
                hits += 1
                findings.append(Finding("secrets_in_repo", rel_path, "WARNING", f"matches a {label} pattern - review (may be a false positive, e.g. a placeholder/example)"))
    if hits == 0:
        findings.append(Finding("secrets_in_repo", None, "PASS", f"scanned {len(tracked)} tracked files, no secret patterns matched"))
    return findings


def large_binary_in_git_check(repo_root: Path, threshold_mb: int = 20) -> list[Finding]:
    """Flag committed blobs over the threshold that AREN'T in an expected
    large-asset location (3D models are legitimately large; a stray large
    file anywhere else is worth a look)."""
    findings = []
    try:
        out = subprocess.run(
            ["git", "ls-tree", "-r", "-l", "HEAD"], cwd=repo_root, capture_output=True, text=True, check=True
        ).stdout
    except Exception as e:
        return [Finding("large_binary_in_git", None, "WARNING", f"could not list git blobs: {e}")]

    expected_large_dirs = ("tests/testing-site/ships/", "sc-ships/", "releases/", "_zip_archive/")
    threshold_bytes = threshold_mb * 1024 * 1024
    for line in out.splitlines():
        parts = line.split()
        if len(parts) < 5 or parts[3] == "-":
            continue
        size = int(parts[3])
        path = parts[4]
        if size > threshold_bytes and not path.startswith(expected_large_dirs):
            findings.append(
                Finding("large_binary_in_git", path, "WARNING", f"{size / (1024*1024):.1f} MB committed blob outside expected large-asset directories")
            )
    if not findings:
        findings.append(Finding("large_binary_in_git", None, "PASS", f"no unexpected blob over {threshold_mb} MB"))
    return findings


def fan_kit_compliance_check(repo_root: Path) -> list[Finding]:
    """Conservative, read-only check: confirm the trademark disclaimer
    text and manufacturer logo files this project already has are still
    present - does NOT make any legal judgment, just flags if something
    that was there before has gone missing."""
    findings = []
    index_html = repo_root / "static" / "index.html"
    if index_html.exists():
        text = index_html.read_text(encoding="utf-8", errors="ignore")
        if re.search(r"(?i)trademark", text):
            findings.append(Finding("fan_kit_compliance", "static/index.html", "PASS", "trademark disclaimer text present"))
        else:
            findings.append(Finding("fan_kit_compliance", "static/index.html", "WARNING", "no text matching 'trademark' found - confirm the required disclaimer is still present"))
    logos_dir = repo_root / "static" / "logos"
    if logos_dir.is_dir():
        logo_count = len(list(logos_dir.iterdir()))
        findings.append(Finding("fan_kit_compliance", "static/logos/", "PASS" if logo_count else "WARNING", f"{logo_count} logo file(s) present"))
    return findings


# --- code/content quality ----------------------------------------------------


def broken_internal_link_check(repo_root: Path) -> list[Finding]:
    """Reuses the same broken_asset_references logic but scoped to <a
    href> links specifically, including the testing-site's own index of
    ship links - confirms every internal route/page it links to exists."""
    findings = []
    link_pattern = re.compile(r'<a[^>]+href\s*=\s*["\']([^"\'#?]+)["\']')
    html_files = list(repo_root.glob("tests/testing-site/**/*.html")) + list(repo_root.glob("static/*.html"))

    for html_file in html_files:
        try:
            text = html_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for ref in link_pattern.findall(text):
            if ref.startswith(("http://", "https://", "mailto:")):
                continue
            # Same JS-template-literal false positive as
            # broken_asset_references_check - see that function's comment.
            if "${" in ref or "{{" in ref or "{%" in ref:
                continue
            target = (repo_root / ref.lstrip("/")) if ref.startswith("/") else (html_file.parent / ref)
            try:
                resolved = target.resolve()
            except Exception:
                continue
            if not resolved.exists():
                findings.append(
                    Finding("broken_internal_link", str(html_file.relative_to(repo_root)), "DEFECT", f"links to {ref!r} which does not exist (resolved: {resolved})")
                )
    if not findings:
        findings.append(Finding("broken_internal_link", None, "PASS", f"checked {len(html_files)} HTML files, all internal links resolve"))
    return findings


# A checker may emit findings under a check_name that is not its registered
# name. missing_or_corrupt_3d_model_check emits missing_preview_image, and the
# consequence was real: no registered checker owned that name, so the lifecycle
# could never conclude anything had looked for it, and those findings were
# pinned at UNKNOWN permanently. The first lifecycle-aware run surfaced exactly
# one such finding, which is how this was found.
#
# Declaring the extra names statically - rather than inferring them from what a
# run happened to emit - is deliberate. Inferring would mean a condition that
# has genuinely gone away stops being emitted, so its name drops out of
# "what ran", so its old findings go UNKNOWN instead of CLOSED. The names a
# checker CAN emit must not depend on what it DID emit.
CHECKER_EMITS = {
    "missing_or_corrupt_3d_model": {"missing_or_corrupt_3d_model", "missing_preview_image"},
}

# Directories whose contents a player can actually see. Derived tables are NOT
# in this list on purpose: they are supposed to carry the unreleased records,
# because they are a faithful record of what is in the game files. The defect
# is publishing one, not deriving one.
PUBLISHED_ROOTS = ("releases", "static", "testing/_deploy")

# Records marked with these have not been released by CIG. Imported from the
# single definition rather than re-spelled here - rule 14.
try:
    from scripts.publication_filter import UNRELEASED_FLAGS, unreleased_reasons
except Exception:  # pragma: no cover - import shape differs when run as a script
    UNRELEASED_FLAGS = ("not_for_release", "work_in_progress")
    unreleased_reasons = None


def unreleased_content_check(repo_root: Path) -> list[Finding]:
    """Refuse to let a record CIG has not released reach a published file.

    THE RISK, stated accurately. As of 2026-08-07 this is NOT a live leak:
    nothing published reads the contract tables. 959 of 5,107 contracts (18.8%)
    carry not_for_release or work_in_progress, and they sit in
    data-layer/derived/, which is not served. The check goes in before the first
    contract page ships, because that is the cheap moment.

    WHY IT REPORTS A LIMITATION RATHER THAN A PASS WHEN IT FINDS NOTHING.
    A checker that scans for contract records in published output, finds no
    contract records at all, and reports PASS is reporting "clean" for a corpus
    it never had. That is the silent-success shape - the same defect as
    integrity_scan globbing "*.json" and passing over files it never opened. So
    when no publishable corpus exists, this says so.
    """
    findings: list[Finding] = []
    scanned_files = 0
    corpus_records = 0

    for rel in PUBLISHED_ROOTS:
        root = repo_root / rel
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*.json")):
            try:
                raw = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as e:
                findings.append(Finding(
                    "unreleased_content", str(path.relative_to(repo_root)), "LIMITATION",
                    f"could not read: {type(e).__name__}: {e}. Reported as not "
                    f"performed, never as a pass."))
                continue
            scanned_files += 1

            # Cheap pre-filter: a file that never mentions either flag cannot
            # carry a flagged record. Checked textually so a nested structure
            # this function does not understand still gets noticed.
            if not any(flag in raw for flag in UNRELEASED_FLAGS):
                continue

            try:
                data = json.loads(raw)
            except ValueError:
                findings.append(Finding(
                    "unreleased_content", str(path.relative_to(repo_root)), "WARNING",
                    f"mentions {UNRELEASED_FLAGS} but is not parseable JSON, so its "
                    f"records could not be examined. Not reported as clean."))
                continue

            flagged = []
            for record in _walk_records(data):
                corpus_records += 1
                reasons = ([f for f in UNRELEASED_FLAGS if _flag_set(record.get(f))]
                           if unreleased_reasons is None else unreleased_reasons(record))
                if reasons:
                    flagged.append((record.get("debug_name") or record.get("uuid") or "?",
                                    ",".join(reasons)))

            if flagged:
                findings.append(Finding(
                    "unreleased_content", str(path.relative_to(repo_root)), "DEFECT",
                    f"{len(flagged)} record(s) marked unreleased by CIG are present in a "
                    f"PUBLISHED file. Publishing content CIG has not released misrepresents "
                    f"the game to players and is exactly what the flags exist to prevent. "
                    f"First few: {flagged[:5]}"))

    if not findings and corpus_records == 0:
        findings.append(Finding(
            "unreleased_content", "/".join(PUBLISHED_ROOTS), "LIMITATION",
            f"scanned {scanned_files} published .json file(s) and found NO records "
            f"carrying {UNRELEASED_FLAGS} - but also no contract-shaped corpus to "
            f"examine at all. This is reported as NOT PERFORMED rather than PASS: "
            f"nothing published reads the contract tables yet, so a pass here would "
            f"be a pass over an empty corpus. It becomes a real check the moment a "
            f"contract page ships."))
    elif not findings:
        findings.append(Finding(
            "unreleased_content", "/".join(PUBLISHED_ROOTS), "PASS",
            f"examined {corpus_records} record(s) across {scanned_files} published "
            f"file(s); none carry {UNRELEASED_FLAGS}"))

    return findings


def _flag_set(value) -> bool:
    """Fallback used only if scripts.publication_filter cannot be imported."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "1"}
    if isinstance(value, (int, float)):
        return value != 0
    return False


def _walk_records(data):
    """Yield every dict in a nested JSON structure.

    Walks rather than assuming a top-level list, because a future page is as
    likely to publish {"systems": {"Stanton": [...]}} as a flat array, and a
    checker that only understood one shape would pass over the other.
    """
    stack = [data]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            yield node
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)


CHECKERS = [
    ("naming_convention_typo", naming_convention_typo_check),
    ("placeholder_null_density", placeholder_null_density_check),
    ("broken_asset_references", broken_asset_references_check),
    ("orphaned_test_fixture", orphaned_test_fixture_check),
    ("missing_or_corrupt_3d_model", missing_or_corrupt_3d_model_check),
    ("missing_encoding", missing_encoding_check),
    ("control_bytes", control_bytes_check),
    ("log_growth", log_growth_check),
    ("backup_freshness", backup_freshness_check),
    ("scheduled_task_health", scheduled_task_health_check),
    ("duplicate_process", duplicate_process_check),
    ("secrets_in_repo", secrets_in_repo_check),
    ("large_binary_in_git", large_binary_in_git_check),
    ("fan_kit_compliance", fan_kit_compliance_check),
    ("broken_internal_link", broken_internal_link_check),
    ("unreleased_content", unreleased_content_check),
]
