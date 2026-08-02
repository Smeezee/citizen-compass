"""
Checkers that need only the filesystem + git - no database, no network.
Deliberately stdlib-only (no psycopg2/sqlalchemy/requests imports) so
these can run anywhere Python 3 exists, including environments with no
network access and no project venv (this is exactly how they were first
run for real - see LATEST_HANDOFF.md 2026-07-30).

Each function takes `repo_root: Path` and returns list[Finding].
"""

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
    """Same limitation as scheduled_task_health_check - no Windows process
    list visibility from this environment."""
    return [
        Finding(
            "duplicate_process",
            "inbox_watcher.exe",
            "LIMITATION",
            "cannot enumerate Windows processes from this environment - run 'tasklist | findstr inbox_watcher' "
            "or Task Manager manually, or from a context with real Windows access.",
        )
    ]


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

CHECKERS = [
    ("naming_convention_typo", naming_convention_typo_check),
    ("placeholder_null_density", placeholder_null_density_check),
    ("broken_asset_references", broken_asset_references_check),
    ("orphaned_test_fixture", orphaned_test_fixture_check),
    ("missing_or_corrupt_3d_model", missing_or_corrupt_3d_model_check),
    ("missing_encoding", missing_encoding_check),
    ("log_growth", log_growth_check),
    ("backup_freshness", backup_freshness_check),
    ("scheduled_task_health", scheduled_task_health_check),
    ("duplicate_process", duplicate_process_check),
    ("secrets_in_repo", secrets_in_repo_check),
    ("large_binary_in_git", large_binary_in_git_check),
    ("fan_kit_compliance", fan_kit_compliance_check),
    ("broken_internal_link", broken_internal_link_check),
]
