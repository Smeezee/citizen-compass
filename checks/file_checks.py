"""
Checkers that need only the filesystem + git - no database, no network.
Deliberately stdlib-only (no psycopg2/sqlalchemy/requests imports) so
these can run anywhere Python 3 exists, including environments with no
network access and no project venv (this is exactly how they were first
run for real - see LATEST_HANDOFF.md 2026-07-30).

Each function takes `repo_root: Path` and returns list[Finding].
"""

import csv
import datetime
import hashlib
import io
import json
import os
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

    # SCAFFOLDING IS NOT A SHIP. `_corrupt_backup`, `_to_delete` and `_stage`
    # are housekeeping directories that this repo puts under sc-ships/, and
    # reporting one of them as "a ship with no model.glb" is a DEFECT this
    # checker invented. It cost a real one: the end-to-end guard pins the
    # number of genuinely-missing models at 6, and an empty `_corrupt_backup`
    # made it 7 - a fabricated finding hiding inside a true count.
    # Underscore is this project's own prefix for not-content; ship names
    # never start with one.
    for ship_dir in sorted(p for p in ships_dir.iterdir()
                           if p.is_dir()
                           and not p.name.startswith(".")
                           and not p.name.startswith("_")):
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


# --- document truth ----------------------------------------------------------
#
# THE SIX DOCUMENT CHECKS. Ordered by Sleven 2026-09-08: he asked for a
# repeatable way to fact-check the project's own files, was offered automatic
# checks or a standing manual pass, and answered BOTH. These are the automatic
# half. Each one is tied to an incident that already happened here.
#
# THEY ARE AUDITOR-LAYER, NOT SWEEP. They flag; they never gate a deploy, and
# they add zero seconds to the deploy sweep because nothing in the sweep calls
# them.
#
# THE STANDING LIMIT, WHICH IS PART OF THE ORDER RATHER THAN ADVICE:
# a check that flags constantly becomes wallpaper. Each of these must be QUIET
# when things are fine. Where a rule is being introduced over a backlog that
# predates it, the backlog is reported as ONE line carrying a count - never as
# one finding per historical file, which is how a checker gets switched off
# inside a week.

# THE SCOPE RULE, AND IT IS NOT OPTIONAL.
#
# History is allowed to name dead paths. Documents asserting a PRESENT state are
# not. docs/handoff_archive/ holds 773 documents that correctly describe a
# repository that no longer exists; a check firing on those produces hundreds of
# correct, useless findings.
#
# So: this list, and nothing else.
#
# CURRENT-STATE LEFT THIS LIST ON 2026-09-12 (Architecture's approval,
# memo_build_check-6-is-approved-and-three-things-are-mine-to-fix). BOOT.md is
# the state now and docs/CURRENT-STATE.md is history - which, by the rule above,
# may name dead paths. Kept here it was already reporting 10 dead paths in a file
# nobody updates, a count that could only grow. The root CURRENT-STATE.md entry
# went with it; that file no longer exists.
#
# AND BOOT.md IS DELIBERATELY NOT HERE. It prints MISSING paths on purpose - that
# is its honesty rule - so this check would report every honest MISSING line as
# a defect. _verify_document_checks.py holds both of these.
PRESENT_STATE_DOCS = (
    "CLAUDE.md",
    "OWNERS.md",
    "NEXT.md",
    "LIVE.md",
    "START-CODE.md",
    "docs/UX_DOCTRINE.md",
    "docs/ARCHITECTURE_DECISIONS.md",
)
PRESENT_STATE_GLOBS = ("docs/DECISION_*.md", "docs/RULING_*.md")


def _present_state_documents(repo_root: Path) -> list[Path]:
    """Every document asserting a present state, per the scope rule above. An
    entry that does not exist is simply absent from the list - a missing state
    document is check 1's business, not check 6's."""
    out = [repo_root / rel for rel in PRESENT_STATE_DOCS]
    for pattern in PRESENT_STATE_GLOBS:
        out.extend(sorted(repo_root.glob(pattern)))
    return [p for p in out if p.is_file()]


def _doc_text(path: Path) -> str | None:
    """Rule 15: the encoding is stated. Returns None when the file cannot be
    read, so every caller reports NOT PERFORMED rather than clean."""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def _rel(repo_root: Path, path: Path) -> str:
    return str(path.relative_to(repo_root)).replace("\\", "/")


# --- 1. state_document_agreement ---------------------------------------------

# Basenames that CLAIM to be the current state of the project. A file is in this
# family because of what its name promises, not because of what it contains.
STATE_DOC_NAMES = ("CURRENT-STATE.md", "CURRENT_STATE.md", "PROJECT-STATE.md")

# Where a session is told to start reading, and where ownership is recorded.
ONBOARDING_DOCS = ("CLAUDE.md", "START-CODE.md", "README.md", "OWNERS.md")

# Directory names never descended into when looking for a state document.
#
# THIS IS A COST FIX, MEASURED. The first version used Path.rglob over the whole
# tree and took 19.4 SECONDS - this repository holds ~29,000 files cloned from
# third-party sources, and a bare rglob walks every one of them. Pruning takes it
# under a tenth of a second. None of these can hold a state document:
# external-sources is landed third-party data, handoff_archive is history,
# _to_delete is the rule 1 holding pen, and the rest are machinery.
STATE_SCAN_PRUNE = frozenset((
    ".git", ".claude", "node_modules", "venv", "__pycache__",
    "_to_delete", "handoff_archive", "external-sources", "snapshots",
    "captures", "models", "releases",
))


def _find_state_documents(repo_root: Path) -> list[Path]:
    """Every file in the tree whose NAME claims to be project state, found by
    a pruned walk rather than a full one."""
    found = []
    for dirpath, dirnames, filenames in os.walk(repo_root):
        dirnames[:] = [d for d in dirnames if d not in STATE_SCAN_PRUNE]
        for name in filenames:
            if name in STATE_DOC_NAMES:
                found.append(Path(dirpath) / name)
    return sorted(found)

_STATE_REF = re.compile(r"`([^`\n]*(?:CURRENT-STATE|CURRENT_STATE|PROJECT-STATE)\.md)`")


def state_document_agreement_check(repo_root: Path) -> list[Finding]:
    """Two files claiming to be the current state, and onboarding pointing at
    the wrong one.

    THE INCIDENT. On 2026-09-07 the audit desk produced a nineteen-finding
    project audit from the root CURRENT-STATE.md - a 76-line note from
    2026-08-02 about which URL is which - and never opened the 1,403-line
    authoritative one in docs/. Two findings lost their recommendations and one
    was withdrawn entirely. The root file's NAME claimed to be project state and
    its content was not, and the boot instructions pointed at it first.

    THREE ARMS.
      A  more than one state document on disk, and one of them does not name the
         newest as authoritative
      B  an onboarding or ownership document names a state document that is NOT
         ON DISK - the pointer outlived the file
      C  onboarding names a state document that is older than another one on
         disk, which is the 2026-09-07 incident exactly

    'Newest' is decided by modification time and nothing else. That is a weak
    signal on its own, which is why arm A wants an explicit pointer rather than
    trusting the clock: the finding is THE ABSENCE OF A POINTER, not the age.
    """
    findings: list[Finding] = []

    on_disk = _find_state_documents(repo_root)
    rel = {p: _rel(repo_root, p) for p in on_disk}

    if not on_disk:
        return [Finding(
            "state_document_agreement", None, "LIMITATION",
            "no file named " + " or ".join(STATE_DOC_NAMES) + " exists anywhere in "
            "the tree, so there is nothing to compare. Reported as NOT PERFORMED "
            "rather than as a pass over an empty set.")]

    newest = max(on_disk, key=lambda p: p.stat().st_mtime)

    # Arm A - siblings must name the newest one.
    if len(on_disk) > 1:
        for p in on_disk:
            if p == newest:
                continue
            text = _doc_text(p)
            if text is None:
                findings.append(Finding(
                    "state_document_agreement", rel[p], "LIMITATION",
                    "could not be read, so whether it points at the authoritative "
                    "state document is unknown. Not reported as clean."))
                continue
            if rel[newest] not in text:
                findings.append(Finding(
                    "state_document_agreement", rel[p], "DEFECT",
                    f"claims to be project state by its name and does NOT name "
                    f"{rel[newest]} - the newest state document - anywhere in its "
                    f"text. Two files claiming one job with no pointer between them "
                    f"is how a reader ends up in the wrong one. Either point at the "
                    f"authoritative file in its first lines, or rename this one to "
                    f"say what it actually covers."))

    # Arms B and C - what the onboarding documents point at.
    for name in ONBOARDING_DOCS:
        doc = repo_root / name
        if not doc.is_file():
            continue
        text = _doc_text(doc)
        if text is None:
            findings.append(Finding(
                "state_document_agreement", name, "LIMITATION",
                "could not be read, so its state-document pointers were not "
                "examined. Not reported as clean."))
            continue
        for ref in sorted(set(_STATE_REF.findall(text))):
            target = repo_root / ref
            if not target.is_file():
                findings.append(Finding(
                    "state_document_agreement", name, "DEFECT",
                    f"points a reader at {ref!r}, which is not on disk. A pointer "
                    f"that outlived its file sends the reader nowhere, and there is "
                    f"no error to tell them so."))
            elif len(on_disk) > 1 and target.resolve() != newest.resolve():
                findings.append(Finding(
                    "state_document_agreement", name, "DEFECT",
                    f"points a reader at {ref!r}, which is OLDER than {rel[newest]}. "
                    f"This is the 2026-09-07 incident exactly: a whole audit was "
                    f"produced from the stale file because onboarding named it "
                    f"first."))

    if not findings:
        present_onboarding = [n for n in ONBOARDING_DOCS if (repo_root / n).is_file()]
        findings.append(Finding(
            "state_document_agreement", None, "PASS",
            f"{len(on_disk)} state document(s) on disk ({', '.join(rel.values())}); "
            f"newest is {rel[newest]}; every state-document pointer in "
            f"{', '.join(present_onboarding)} resolves to a file that exists and "
            f"none names an older sibling"))
    return findings


# --- 2. finding_resolution_marker --------------------------------------------

# THE RULE STARTS HERE. Documents written before this date predate it and are
# reported as ONE backlog line, not as one finding each - see the standing limit
# at the top of this section. 91 FINDING documents existed on the day the rule
# was written and 85 carried no marker of any kind; firing 85 times on day one
# would have retired this checker inside a week.
FINDING_MARKER_RULE_STARTS = "2026-09-09"

_MARKER = re.compile(
    r"^[ \t>*_]*(?:\*\*)?\s*(?:Status|STATUS|Resolution|RESOLUTION)\s*(?:\*\*)?\s*:"
    r"\s*(?:\*\*)?\s*(OPEN|CLOSED|WITHDRAWN|SUPERSEDED)\b",
    re.MULTILINE)
_ISO_DATE = re.compile(r"\b20\d{2}-\d{2}-\d{2}\b")
_DATED_NAME = re.compile(r"(20\d{2}-\d{2}-\d{2})")


def finding_resolution_marker_check(repo_root: Path) -> list[Finding]:
    """A FINDING_*.md with no OPEN / CLOSED / WITHDRAWN line and a date.

    THE INCIDENT. This project writes findings constantly and closes them in
    conversation. A reader six months later cannot tell a live problem from one
    that was fixed the same evening, and has to reconstruct it from surrounding
    documents - which is how a closed finding gets re-opened and worked twice.

    WHAT COUNTS AS A MARKER: a line reading Status: or Resolution: followed by
    OPEN, CLOSED, WITHDRAWN or SUPERSEDED, AND an ISO date somewhere in the
    document. Both, because a status with no date does not say when it became
    true, and this project has already been bitten by a status that was correct
    when written and stale when read.

    THE CUTOFF IS THE WHOLE DESIGN. Only documents dated on or after
    FINDING_MARKER_RULE_STARTS are held to it. The backlog is one LIMITATION
    line carrying a count that should only ever go down.
    """
    findings: list[Finding] = []
    docs = sorted(repo_root.glob("docs/FINDING_*.md"))
    if not docs:
        return [Finding(
            "finding_resolution_marker", "docs/FINDING_*.md", "LIMITATION",
            "no FINDING documents found, so nothing was examined. Reported as NOT "
            "PERFORMED rather than as a pass over an empty corpus.")]

    backlog: list[str] = []
    unreadable = 0
    checked = 0
    in_scope = 0
    for doc in docs:
        rel = _rel(repo_root, doc)
        text = _doc_text(doc)
        if text is None:
            unreadable += 1
            findings.append(Finding(
                "finding_resolution_marker", rel, "LIMITATION",
                "could not be read, so its resolution marker was not examined. Not "
                "reported as clean."))
            continue
        checked += 1
        name_hit = _DATED_NAME.search(doc.name)
        this_date = (name_hit.group(1) if name_hit
                     else datetime.date.fromtimestamp(doc.stat().st_mtime).isoformat())
        if _MARKER.search(text) and _ISO_DATE.search(text):
            if this_date >= FINDING_MARKER_RULE_STARTS:
                in_scope += 1
            continue

        # The document's own date: the one in its filename if it has one,
        # otherwise its modification time. Never guessed, never inferred from
        # neighbours.
        doc_date = this_date

        if doc_date < FINDING_MARKER_RULE_STARTS:
            backlog.append(rel)
            continue
        in_scope += 1

        missing = []
        if not _MARKER.search(text):
            missing.append("no Status:/Resolution: line reading OPEN, CLOSED, "
                           "WITHDRAWN or SUPERSEDED")
        if not _ISO_DATE.search(text):
            missing.append("no ISO date anywhere in the document")
        findings.append(Finding(
            "finding_resolution_marker", rel, "DEFECT",
            f"dated {doc_date}, on or after the rule start "
            f"{FINDING_MARKER_RULE_STARTS}, and has {' and '.join(missing)}. A "
            f"finding nobody can date and nobody can tell the status of gets worked "
            f"twice."))

    if backlog:
        findings.append(Finding(
            "finding_resolution_marker", "docs/FINDING_*.md", "LIMITATION",
            f"{len(backlog)} of {checked} FINDING document(s) predate "
            f"{FINDING_MARKER_RULE_STARTS} and carry no resolution marker. This is a "
            f"KNOWN BACKLOG, reported as one line rather than {len(backlog)} "
            f"findings, deliberately - see the standing limit in this section. The "
            f"count is the thing to watch and it should only ever go down. First "
            f"few: {backlog[:5]}"))

    if any(f.result == "DEFECT" for f in findings):
        return findings

    # NO PASS OVER AN EMPTY SET. If not one document is yet in scope, saying
    # "every document in scope carries a marker" is true of nothing and reads as
    # a clean bill of health - the silent-success shape this project keeps
    # finding. It says so instead, and starts passing the day the first
    # in-scope document is written.
    if in_scope == 0:
        findings.append(Finding(
            "finding_resolution_marker", "docs/FINDING_*.md", "LIMITATION",
            f"{checked} FINDING document(s) examined"
            + (f", {unreadable} unreadable" if unreadable else "")
            + f", and NONE is dated on or after the rule start "
              f"{FINDING_MARKER_RULE_STARTS}. Nothing is in scope yet, so this is "
              f"reported as NOT PERFORMED rather than as a pass over an empty set."))
    else:
        findings.insert(0, Finding(
            "finding_resolution_marker", "docs/FINDING_*.md", "PASS",
            f"{checked} FINDING document(s) examined"
            + (f", {unreadable} unreadable" if unreadable else "")
            + f"; all {in_scope} dated on or after {FINDING_MARKER_RULE_STARTS} "
              f"carry a status marker and a date"))
    return findings


# --- 3. derived_number_freshness ---------------------------------------------

# WHAT IS DERIVED FROM WHAT. Each entry: the generated artifact, the files it is
# generated FROM, and the tool that does it. Adding an entry is one line.
#
# The snapshot directory is deliberately NOT written here. It is read out of the
# generator's own source, so this check learns which snapshot feeds the output
# from the thing that does the feeding - rule 16, a different source than the
# artifact being judged.
DERIVED_ARTIFACTS = [
    {
        "output": "testing/_src/loadout_data.gen.js",
        "generator": "build_loadout_data.py",
        "inputs": ["data-layer/ship_resolution.json"],
        "snapshot_inputs": ["ships.json", "ship-items.json"],
    },
]

FRESHNESS_STATE = "checks/.derived_freshness.json"
_SNAPSHOT_CONST = re.compile(r'^SNAPSHOT\s*=\s*"([^"]+)"', re.MULTILINE)
_SNAPSHOT_DIR = "data-layer/external-sources/scunpacked-data/snapshots"


def _sha256(path: Path) -> str | None:
    try:
        digest = hashlib.sha256()
        with open(path, "rb") as fh:
            for block in iter(lambda: fh.read(1 << 20), b""):
                digest.update(block)
        return digest.hexdigest()
    except OSError:
        return None


def derived_number_freshness_check(repo_root: Path) -> list[Finding]:
    """A number meant to be regenerated has stopped moving.

    THE INCIDENT, and it is written in the generator's own comment:
    build_loadout_data.py carried LAST_VERIFIED_PATCH = "4.9" for WEEKS after the
    snapshot beside it had moved on to 4.10. The site published a hand-typed
    summary of evidence that was already on disk and already newer. Nothing was
    broken, nothing failed, and the number was simply wrong for a month.

    HOW IT DECIDES, AND WHY NOT MODIFICATION TIMES. A git checkout stamps every
    file with the checkout time, so an mtime comparison reports whatever the last
    clone did - a check that cannot fail on demand, which is the exact shape rule
    12 is about. So this hashes CONTENT: the inputs together, and the output.

      inputs changed, output did not  ->  DEFECT. The thing it is derived from
                                          moved and the derived thing did not.
      both changed, or neither        ->  quiet, and the baseline is updated.

    THE BASELINE IS A SIDECAR the checker maintains itself
    (checks/.derived_freshness.json). A first run has nothing to compare against
    and reports LIMITATION, because saying PASS there would be a pass over no
    evidence at all.
    """
    findings: list[Finding] = []
    state_path = repo_root / FRESHNESS_STATE
    try:
        state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
    except (OSError, ValueError):
        state = {}
    if not isinstance(state, dict):
        state = {}
    new_state = dict(state)

    for entry in DERIVED_ARTIFACTS:
        out_rel = entry["output"]
        out_path = repo_root / out_rel
        inputs = [repo_root / i for i in entry["inputs"]]

        # Resolve the snapshot-relative inputs from the generator's own source.
        if entry.get("snapshot_inputs"):
            gen_text = _doc_text(repo_root / entry["generator"])
            snap = _SNAPSHOT_CONST.search(gen_text) if gen_text else None
            if snap is None:
                findings.append(Finding(
                    "derived_number_freshness", out_rel, "LIMITATION",
                    f"could not read the SNAPSHOT constant out of "
                    f"{entry['generator']}, so this artifact's real inputs are "
                    f"unknown and its freshness was NOT CHECKED. Reported rather "
                    f"than assumed fresh."))
                continue
            snapdir = repo_root / _SNAPSHOT_DIR / snap.group(1)
            inputs.extend(snapdir / n for n in entry["snapshot_inputs"])

        if not out_path.exists():
            findings.append(Finding(
                "derived_number_freshness", out_rel, "DEFECT",
                f"is registered as a derived artifact and is not on disk. It has "
                f"not stopped moving - it is not there at all. Generator: "
                f"{entry['generator']}."))
            continue

        missing = [_rel(repo_root, p) for p in inputs if not p.exists()]
        if missing:
            findings.append(Finding(
                "derived_number_freshness", out_rel, "LIMITATION",
                f"input(s) not on disk: {missing}. Freshness was NOT CHECKED for "
                f"this artifact - an absent input cannot be compared, and a pass "
                f"here would be a pass over nothing."))
            continue

        input_digests: list[str] | None = []
        for p in sorted(inputs):
            digest = _sha256(p)
            if digest is None:
                input_digests = None
                break
            input_digests.append(digest)
        out_digest = _sha256(out_path)
        if input_digests is None or out_digest is None:
            findings.append(Finding(
                "derived_number_freshness", out_rel, "LIMITATION",
                "an input or the output could not be read, so freshness was NOT "
                "CHECKED. Not reported as fresh."))
            continue

        inputs_sha = hashlib.sha256("".join(input_digests).encode("utf-8")).hexdigest()
        new_state[out_rel] = {"inputs_sha": inputs_sha, "output_sha": out_digest}
        previous = state.get(out_rel)

        if not isinstance(previous, dict) or "inputs_sha" not in previous:
            findings.append(Finding(
                "derived_number_freshness", out_rel, "LIMITATION",
                f"first run for this artifact - the baseline was recorded in "
                f"{FRESHNESS_STATE} and there is nothing to compare it against yet. "
                f"Reported as NOT PERFORMED rather than as a pass."))
            continue

        if previous["inputs_sha"] != inputs_sha and previous.get("output_sha") == out_digest:
            findings.append(Finding(
                "derived_number_freshness", out_rel, "DEFECT",
                f"its inputs changed and it did NOT. The {len(inputs)} input file(s) "
                f"have different contents than when this last ran, and the derived "
                f"artifact is byte-for-byte identical. Re-run {entry['generator']}. "
                f"This is the LAST_VERIFIED_PATCH = \"4.9\" shape: a number that "
                f"stopped moving while the thing it describes moved on."))

    try:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(new_state, indent=1, sort_keys=True),
                              encoding="utf-8")
    except OSError as e:
        findings.append(Finding(
            "derived_number_freshness", FRESHNESS_STATE, "LIMITATION",
            f"could not write the freshness baseline: {type(e).__name__}: {e}. The "
            f"next run will have nothing to compare against and will say so."))

    if not findings:
        findings.append(Finding(
            "derived_number_freshness", None, "PASS",
            f"{len(DERIVED_ARTIFACTS)} derived artifact(s) checked; none is stale "
            f"against the inputs it is generated from"))
    return findings


# --- 4. published_patch_currency ---------------------------------------------

PUBLISHED_PAGES = ("static/preview.html", "releases/latest.html")
_PAGE_PATCH = re.compile(r"Patch:\s*Alpha\s+(\d+(?:\.\d+)+)")
_MANIFEST_SUBJECT_PATCH = re.compile(r"(\d+\.\d+(?:\.\d+)?)-(?:LIVE|PTU|EPTU)", re.IGNORECASE)


def _version_tuple(text: str) -> tuple[int, ...]:
    return tuple(int(part) for part in text.split(".") if part.isdigit())


def published_patch_currency_check(repo_root: Path) -> list[Finding]:
    """The patch the public page states is behind the newest patch we know of.

    THE INCIDENT. The live site said 4.9 for a month after the data under it had
    moved on - docs/FINDING_the-live-site-was-a-month-wrong-about-the-patch-and-
    has-two-source-files-2026-08-30.md. The evidence was on disk the whole time.

    RULE 16, INDEPENDENT. The two sides come from different places and neither is
    derived from the other:
      subject      the 'Patch: Alpha X.Y.Z' line the published page renders
      expectation  the upstream commit subject recorded in the external source
                   manifests - '4.10.0-LIVE.12519617' - which is what the landed
                   data actually IS, captured by the pull at landing time

    IT DOES NOT GUESS. No manifest, no parseable subject, or no patch line on the
    page: each is reported as NOT PERFORMED, naming what was missing. A silent
    pass here would be the site claiming currency against nothing.
    """
    findings: list[Finding] = []

    manifest_dir = repo_root / "data-layer" / "external-source-manifests"
    manifests = sorted(manifest_dir.glob("*/*.json"))
    known: list[tuple[tuple[int, ...], str, str]] = []
    for manifest in manifests:
        text = _doc_text(manifest)
        if text is None:
            continue
        try:
            data = json.loads(text)
        except ValueError:
            continue
        if not isinstance(data, dict):
            continue
        git_meta = data.get("git_metadata_captured_before_stripping")
        subject = git_meta.get("git_head_subject") if isinstance(git_meta, dict) else None
        if not isinstance(subject, str):
            continue
        hit = _MANIFEST_SUBJECT_PATCH.search(subject)
        if hit:
            known.append((_version_tuple(hit.group(1)), hit.group(1),
                          _rel(repo_root, manifest)))

    if not known:
        return [Finding(
            "published_patch_currency", "data-layer/external-source-manifests",
            "LIMITATION",
            f"examined {len(manifests)} manifest(s) and none carried a parseable "
            f"game build in git_head_subject, so there is no independent answer to "
            f"compare the page against. Reported as NOT PERFORMED - never as a "
            f"pass, because a pass here would mean the site is current according to "
            f"nothing.")]

    newest_version, newest_string, newest_source = max(known)

    for rel in PUBLISHED_PAGES:
        page = repo_root / rel
        if not page.is_file():
            continue
        text = _doc_text(page)
        if text is None:
            findings.append(Finding(
                "published_patch_currency", rel, "LIMITATION",
                "the published page could not be read, so the patch it states was "
                "not examined. Not reported as current."))
            continue
        hit = _PAGE_PATCH.search(text)
        if hit is None:
            findings.append(Finding(
                "published_patch_currency", rel, "WARNING",
                "no 'Patch: Alpha X.Y.Z' line found on a published page. Either the "
                "page stopped stating which patch it describes - which is rule 20's "
                "whole subject, a number with no date on it - or this check is "
                "looking for wording that has since changed. Reported rather than "
                "passed."))
            continue
        stated = hit.group(1)
        if _version_tuple(stated) < newest_version:
            findings.append(Finding(
                "published_patch_currency", rel, "DEFECT",
                f"states Alpha {stated}; the newest game build on disk is "
                f"{newest_string}, recorded in {newest_source}. The public page is "
                f"behind data we already hold. The live site was a month wrong about "
                f"exactly this once already."))
        elif _version_tuple(stated) > newest_version:
            findings.append(Finding(
                "published_patch_currency", rel, "WARNING",
                f"states Alpha {stated}, which is NEWER than anything on disk "
                f"({newest_string}, from {newest_source}). The page is claiming a "
                f"patch no landed snapshot backs. Reported, not corrected - it may "
                f"be a hand-typed number running ahead of the pull."))

    if not findings:
        findings.append(Finding(
            "published_patch_currency", ", ".join(PUBLISHED_PAGES), "PASS",
            f"published page(s) state the current build {newest_string}, matching "
            f"{newest_source} ({len(known)} manifest(s) read)"))
    return findings


# --- 5. sweep_runtime_drift --------------------------------------------------

SWEEP_RECEIPT = "checks/.last_sweep.json"
SWEEP_HISTORY = "checks/.sweep_runtime_history.json"
# What counts as material. BOTH must be true, so a fast sweep wobbling by a few
# seconds never speaks and a real regression always does.
SWEEP_DRIFT_FRACTION = 0.25
SWEEP_DRIFT_SECONDS = 60.0
SWEEP_HISTORY_KEEP = 20


def sweep_runtime_drift_check(repo_root: Path) -> list[Finding]:
    """A full sweep's time moves materially against the previous receipt.

    WHY IT IS WORTH A CHECK. One control is already 42.7% of the sweep. Controls
    keep being added, and the cost of the whole gate is what decides whether
    anybody still runs it before deploying. A sweep that quietly doubles is how a
    gate stops being run at all - and nothing in this project was watching that
    number.

    IT COMPARES RECEIPTS, NOT CLOCKS. checks/.last_sweep.json is a SINGLE
    RECEIPT, overwritten by each sweep, so there is no history in it to compare
    against. This check keeps its own small rolling history keyed by the
    receipt's own 'at' timestamp, and only ever appends a receipt it has not
    already seen. IT NEVER WRITES THE RECEIPT - rule 14, one writer, and the
    sweep owns that file.

    PARTIAL AND FAILED SWEEPS ARE RECORDED AND NOT COMPARED. A sweep that skipped
    controls took less time for a reason that has nothing to do with drift, and
    comparing it would manufacture a finding.
    """
    findings: list[Finding] = []
    receipt_path = repo_root / SWEEP_RECEIPT
    if not receipt_path.exists():
        return [Finding(
            "sweep_runtime_drift", SWEEP_RECEIPT, "LIMITATION",
            "no sweep receipt on disk, so there is no runtime to compare. Reported "
            "as NOT PERFORMED.")]
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return [Finding(
            "sweep_runtime_drift", SWEEP_RECEIPT, "LIMITATION",
            f"the sweep receipt could not be read or parsed ({type(e).__name__}), so "
            f"runtime drift was NOT CHECKED. Not reported as steady.")]

    at = receipt.get("at")
    seconds = receipt.get("seconds")
    if not isinstance(at, str) or not isinstance(seconds, (int, float)):
        return [Finding(
            "sweep_runtime_drift", SWEEP_RECEIPT, "LIMITATION",
            "the sweep receipt carries no 'at' or no 'seconds', so there is nothing "
            "to compare. Reported as NOT PERFORMED.")]

    history_path = repo_root / SWEEP_HISTORY
    try:
        history = json.loads(history_path.read_text(encoding="utf-8")) if history_path.exists() else []
    except (OSError, ValueError):
        history = []
    if not isinstance(history, list):
        history = []

    partial = bool(receipt.get("partial") or receipt.get("failed") or receipt.get("not_run"))
    timings = receipt.get("timings") if isinstance(receipt.get("timings"), dict) else {}
    entry = {"at": at, "seconds": float(seconds), "passed": receipt.get("passed"),
             "partial": partial, "timings": timings}

    already_seen = {h.get("at") for h in history if isinstance(h, dict)}
    if at not in already_seen:
        history.append(entry)
        history = history[-SWEEP_HISTORY_KEEP:]
        try:
            history_path.parent.mkdir(parents=True, exist_ok=True)
            history_path.write_text(json.dumps(history, indent=1), encoding="utf-8")
        except OSError as e:
            findings.append(Finding(
                "sweep_runtime_drift", SWEEP_HISTORY, "LIMITATION",
                f"could not write the runtime history ({type(e).__name__}), so the "
                f"next run will have nothing to compare against and will say so."))

    comparable = [h for h in history
                  if isinstance(h, dict) and not h.get("partial") and h.get("at") != at
                  and isinstance(h.get("seconds"), (int, float))]

    if partial:
        findings.append(Finding(
            "sweep_runtime_drift", SWEEP_RECEIPT, "LIMITATION",
            f"the receipt at {at} is partial or carries failures, so its "
            f"{float(seconds):.0f}s was recorded but NOT compared. A sweep that did "
            f"not finish took less time for a reason that is not drift."))
    elif not comparable:
        findings.append(Finding(
            "sweep_runtime_drift", SWEEP_RECEIPT, "LIMITATION",
            f"the receipt at {at} ({float(seconds):.0f}s) was recorded; there is no "
            f"earlier complete receipt in {SWEEP_HISTORY} to compare it against yet. "
            f"Reported as NOT PERFORMED rather than as steady."))
    else:
        previous = comparable[-1]
        delta = float(seconds) - float(previous["seconds"])
        fraction = abs(delta) / float(previous["seconds"]) if previous["seconds"] else 0.0
        if abs(delta) >= SWEEP_DRIFT_SECONDS and fraction >= SWEEP_DRIFT_FRACTION:
            was = previous.get("timings") or {}
            movers = [(now - was[name], name, was[name], now)
                      for name, now in timings.items()
                      if isinstance(now, (int, float)) and isinstance(was.get(name), (int, float))]
            movers.sort(key=lambda m: abs(m[0]), reverse=True)
            biggest = (", ".join(f"{name} {before:.1f}s -> {after:.1f}s"
                                 for _, name, before, after in movers[:3])
                       or "no per-control timings present on both receipts")
            findings.append(Finding(
                "sweep_runtime_drift", SWEEP_RECEIPT, "WARNING",
                f"the full sweep moved {delta:+.0f}s ({fraction * 100:.0f}%) against "
                f"the previous complete receipt: {float(previous['seconds']):.0f}s at "
                f"{previous['at']} -> {float(seconds):.0f}s at {at}. Biggest movers: "
                f"{biggest}. FLAG ONLY - a sweep taking longer is not a defect, it is "
                f"a cost, and the cost is what decides whether the gate keeps being "
                f"run."))

    if not findings:
        findings.append(Finding(
            "sweep_runtime_drift", SWEEP_RECEIPT, "PASS",
            f"full sweep at {at} took {float(seconds):.0f}s, within "
            f"{SWEEP_DRIFT_FRACTION * 100:.0f}% of the previous complete receipt "
            f"({len(comparable)} in history)"))
    return findings


# --- 6. named_thing_exists ---------------------------------------------------

# Namespaces a present-state document may legitimately name without the path
# being on this disk. Each is here for a stated reason, and this list is the
# whole exception - nothing else is excused.
#
#   claude/          the claude.ai project workspace. Partially mirrored here,
#                    authoritative there. A path under it is not this repo's to
#                    resolve.
#   correspondence/  a MOVING filing system. A letter is answered and moves from
#                    open/<desk>/ to answered/ under a new name, by design. A
#                    path into it records where a letter WAS, never a claim about
#                    where it is now.
#   inbox/           the same, one step earlier: the watcher files it and empties
#                    the folder.
#   _to_delete/      the rule 1 holding pen, gitignored, emptied by Sleven. Its
#                    contents are transient on purpose - and a document naming a
#                    path in there is usually saying it is GONE, which is the
#                    opposite of the claim this check tests.
NAMED_THING_EXEMPT_PREFIXES = ("claude/", "correspondence/", "inbox/", "_to_delete/")

_BACKTICKED = re.compile(r"`([^`\n]{3,160})`")
_REPO_PATH_SHAPE = re.compile(r"^[A-Za-z0-9_.\-]+(?:/[A-Za-z0-9_.\-]+)+/?$")


def named_thing_exists_check(repo_root: Path) -> list[Finding]:
    """A document asserting a present state names a file, folder or tool that is
    not there.

    THE INCIDENT, and it is the sharpest one in the set. CLAUDE.md said the
    retired Python handoff files were moved to
    _to_delete/python_handoff_path_retired_20260801/. That folder does not exist
    and the files are nowhere on disk; they were in git at 5081be4 the whole
    time. Rule 1's entire promise is that things are moved aside rather than
    deleted - and THE DOCUMENT CARRYING THAT PROMISE was describing a location
    that was not there. Anyone checking whether rule 1 had been honoured would
    have found an empty answer and had to guess.

    THE SCOPE RULE. Present-state documents only (PRESENT_STATE_DOCS), and
    repo-relative paths only.

    WHAT IT WILL NOT LOOK AT, and every rule here is here because measuring said
    so, on 2026-09-09, over this repository:
      no slash        `build_deploy.py` and `.glb` are shorthand and file
                      extensions, not paths. Requiring a slash took the first
                      measurement from 316 candidates down to 41.
      unknown root    `Freelancer_DUR/MAX/MIS` and `wheelFL/FR/BL/BR` are prose
                      that happens to contain slashes. A repo-relative path whose
                      FIRST SEGMENT is not in the repo is not a path. 41 -> 21.
      globs, ellipses `data-layer/exports/...` names a shape, not a file.
      the exemptions  NAMED_THING_EXEMPT_PREFIXES, each with its reason above.

    Rule 17 applies: existence is tested by exact path and never by looking for
    something nearby with a similar name. A path is there, or it is reported.
    """
    findings: list[Finding] = []
    docs = _present_state_documents(repo_root)
    if not docs:
        return [Finding(
            "named_thing_exists", None, "LIMITATION",
            "none of the present-state documents exist, so nothing was examined. "
            "Reported as NOT PERFORMED.")]

    candidates = 0
    for doc in docs:
        rel_doc = _rel(repo_root, doc)
        text = _doc_text(doc)
        if text is None:
            findings.append(Finding(
                "named_thing_exists", rel_doc, "LIMITATION",
                "could not be read, so the paths it names were not examined. Not "
                "reported as clean."))
            continue

        missing = []
        for token in sorted(set(_BACKTICKED.findall(text))):
            token = token.strip()
            if "/" not in token or "*" in token or "..." in token:
                continue
            if not _REPO_PATH_SHAPE.match(token):
                continue
            if token.startswith(("http", "www.")):
                continue
            if token.startswith(NAMED_THING_EXEMPT_PREFIXES):
                continue
            if not (repo_root / token.split("/")[0]).exists():
                continue
            candidates += 1
            if not (repo_root / token).exists():
                missing.append(token)

        if missing:
            findings.append(Finding(
                "named_thing_exists", rel_doc, "DEFECT",
                f"asserts a present state and names {len(missing)} repo-relative "
                f"path(s) that are not on disk: {missing}. A current document "
                f"pointing at something that is not there sends a reader nowhere, "
                f"and there is no error to tell them so."))

    if not findings:
        findings.append(Finding(
            "named_thing_exists", None, "PASS",
            f"{len(docs)} present-state document(s) examined, {candidates} "
            f"repo-relative path(s) named, every one of them on disk"))
    return findings


# --- 7. skill_mirror -----------------------------------------------------------

def _files_under(root: Path) -> dict[str, Path]:
    """Every file below root, keyed by its exact posix path relative to root."""
    return {str(p.relative_to(root)).replace("\\", "/"): p
            for p in sorted(root.rglob("*")) if p.is_file()}


def skill_mirror_check(repo_root: Path) -> list[Finding]:
    """.claude/skills/ holds something other than the bytes skills/ holds.

    THE RULING, Architecture 2026-09-12 and 2026-09-13: skills/ is the source of
    truth and .claude/skills/ is the loader's copy. A hand-kept mirror is the
    two-places defect this project paid for three times in one week, so the two
    are held byte-identical by this check - never by somebody remembering.

    WHAT IT IS NOT: a sync. It never writes either tree. If they differ, skills/
    is right and the mirror is wrong, and the check still only reports - a
    control that quietly re-copies is the same defect with a nicer face.

    THE SCOPE. Every file under a skill folder (skills/<name>/...) must be at the
    same path under .claude/skills/ with the same bytes, and every file under
    .claude/skills/ must be in skills/ likewise. Top-level files in skills/ (the
    README) are for people, not the loader, and need no counterpart.

    Rule 17: paths are compared as exact strings from enumerating both trees, so
    SKILL.md and skill.md are two different files here even on a disk that would
    open either name. Bytes are compared whole.

    It stays valid if a junction ever replaces the copy: the two trees are then
    one tree and it passes trivially. Whether skills/ is tracked in git does not
    matter - it compares what is on this disk, and git never sees .claude/.
    """
    name = "skill_mirror"
    source = repo_root / "skills"
    mirror = repo_root / ".claude" / "skills"
    if not source.is_dir():
        return [Finding(name, "skills/", "LIMITATION",
                        "skills/ is not on disk, so there is no source to compare. "
                        "Reported as NOT PERFORMED.")]
    if not mirror.is_dir():
        return [Finding(name, ".claude/skills/", "LIMITATION",
                        ".claude/skills/ is not on this machine (.claude/ is "
                        "gitignored, so a fresh clone has none). Nothing to "
                        "compare. Reported as NOT PERFORMED.")]

    src_all = _files_under(source)
    src = {rel: p for rel, p in src_all.items() if "/" in rel}
    mir = _files_under(mirror)
    findings: list[Finding] = []
    for rel in sorted(set(src) - set(mir)):
        findings.append(Finding(
            name, f"skills/{rel}", "DEFECT",
            f"skills/{rel} has no copy at .claude/skills/{rel}, so the loader "
            f"cannot see it. Nothing was copied."))
    for rel in sorted(set(mir) - set(src_all)):
        findings.append(Finding(
            name, f".claude/skills/{rel}", "DEFECT",
            f".claude/skills/{rel} has no source at skills/{rel}, so the loader "
            f"runs a file the record does not hold. Nothing was removed."))
    for rel in sorted(set(mir) & set(src_all)):
        try:
            a, b = src_all[rel].read_bytes(), mir[rel].read_bytes()
        except OSError as e:
            findings.append(Finding(
                name, f"skills/{rel}", "LIMITATION",
                f"could not read one side ({e}), so it was not compared. Not "
                f"reported as identical."))
            continue
        if a != b:
            at = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y),
                      min(len(a), len(b)))
            findings.append(Finding(
                name, f"skills/{rel}", "DEFECT",
                f"skills/{rel} ({len(a)} bytes) and .claude/skills/{rel} "
                f"({len(b)} bytes) differ, first at byte {at}. skills/ is the "
                f"source of truth; nothing was changed."))

    if not findings:
        findings.append(Finding(
            name, None, "PASS",
            f"{len(src)} skill file(s) compared, byte-identical in skills/ and "
            f".claude/skills/ both ways"))
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
    # The six document checks, ordered 2026-09-08. Auditor layer only -
    # nothing in the deploy sweep calls these, so they cost the sweep nothing.
    ("state_document_agreement", state_document_agreement_check),
    ("finding_resolution_marker", finding_resolution_marker_check),
    ("derived_number_freshness", derived_number_freshness_check),
    ("published_patch_currency", published_patch_currency_check),
    ("sweep_runtime_drift", sweep_runtime_drift_check),
    ("named_thing_exists", named_thing_exists_check),
    # The seventh, ordered 2026-09-13: skills/ and .claude/skills/ byte-identical.
    ("skill_mirror", skill_mirror_check),
]
