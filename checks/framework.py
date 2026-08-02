"""
Shared framework for the pluggable checker system.

Per docs/ARCHITECTURE_DECISIONS.md section 4 (LOCKED): "many small
independent checkers... writes findings to the already-built
pipeline_check_results table... Findings-only - validation tools never
automatically modify data." This module is the shared plumbing every
checker uses; individual checkers live in checks/*.py, each exporting a
list of (name, function) pairs via CHECKERS.

pipeline_check_results schema (created by schema-init, see
schema-init/main.go): id, check_name, subject, result, details,
source_process, checked_at.

`result` uses the same four-value vocabulary as audit_ship_components.py,
for one consistent taxonomy across every checker in the project:
  DEFECT      - a confirmed real problem.
  WARNING     - worth a human looking at, not confirmed either way.
  LIMITATION  - a known, expected gap (missing data, environment
                constraint) - not a bug.
  PASS        - checked, found nothing wrong.

Environment note (2026-07-30): this session cannot reach the real
Postgres database from any available tool (confirmed via a direct TCP
test - see LATEST_HANDOFF.md), so `write_findings` degrades gracefully:
if no db connection is available, findings are appended to
logs/pipeline_check_results_fallback.jsonl instead of being lost. Run
`python checks_flush_fallback.py` once real DB access exists to bulk-load
the queued findings into the real table.
"""

import datetime
import json
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FALLBACK_LOG = REPO_ROOT / "logs" / "pipeline_check_results_fallback.jsonl"

RESULTS = ("DEFECT", "WARNING", "LIMITATION", "PASS")


@dataclass
class Finding:
    check_name: str
    subject: str | None
    result: str
    details: str

    def __post_init__(self):
        assert self.result in RESULTS, f"invalid result {self.result!r} for check {self.check_name}"


def write_findings(findings: list[Finding], source_process: str, db_conn=None) -> None:
    """Persist findings to pipeline_check_results if a DB connection is
    given, otherwise queue them to a local fallback log. Never modifies
    any other data - this function only ever INSERTs into the results
    table or appends to a log file."""
    if db_conn is not None:
        with db_conn.cursor() as cur:
            for f in findings:
                cur.execute(
                    "INSERT INTO pipeline_check_results "
                    "(check_name, subject, result, details, source_process, checked_at) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    (f.check_name, f.subject, f.result, f.details, source_process, datetime.datetime.now()),
                )
        db_conn.commit()
        return

    FALLBACK_LOG.parent.mkdir(exist_ok=True)
    with open(FALLBACK_LOG, "a", encoding="utf-8") as fh:
        for f in findings:
            fh.write(
                json.dumps(
                    {
                        "check_name": f.check_name,
                        "subject": f.subject,
                        "result": f.result,
                        "details": f.details,
                        "source_process": source_process,
                        "checked_at": datetime.datetime.now().isoformat(),
                    }
                )
                + "\n"
            )


def summarize(findings: list[Finding]) -> str:
    counts = {r: 0 for r in RESULTS}
    for f in findings:
        counts[f.result] += 1
    lines = [f"{sum(counts.values())} findings: " + "  ".join(f"{k}={v}" for k, v in counts.items())]
    for result in ("DEFECT", "WARNING", "LIMITATION", "PASS"):
        items = [f for f in findings if f.result == result]
        if not items:
            continue
        lines.append(f"\n--- {result} ({len(items)}) ---")
        for f in items:
            lines.append(f"[{f.check_name}] {f.subject or ''}: {f.details}")
    return "\n".join(lines)
