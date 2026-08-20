"""
Schema ownership checker: every table claimed by exactly one authority.

WHY THIS EXISTS
---------------
On 2026-08-02 `alembic revision --autogenerate` would have emitted a migration
dropping four tables and six indexes - 3,751 rows, including the findings the
checker layer had just spent a night producing. The cause was not a bug in
alembic. It was that three different things create tables in this database and
alembic only knew about one of them:

  alembic                  -> the application's domain tables
  schema-init/main.go      -> pipeline_check_results, pipeline_findings,
                              pipeline_check_runs
  registry-builder/main.go -> ship_registry

A table alembic has never heard of looks, to autogenerate, exactly like a table
that should not exist.

That instance is now fixed - ship_registry is declared in app/models.py and the
three pipeline_* tables are named in alembic/env.py's EXCLUDED_TABLES. This
checker closes the CLASS. It catches the next person who adds a table to
schema-init and forgets, which is precisely how this one happened.

THE RULE
--------
Every table in the database is claimed by exactly one authority:

  declared in app/models.py        -> alembic owns it
  named in env.py EXCLUDED_TABLES  -> another authority owns it, deliberately

  claimed by NEITHER -> DEFECT. An unregistered table. Autogenerate will
                        propose dropping it, and the proposal will look
                        ordinary.
  claimed by BOTH    -> DEFECT. Ambiguous ownership - the exclusion says
                        "someone else owns this" while the model says "alembic
                        owns this". One of them is wrong.

FINDINGS ONLY. This checker reads catalogs and source; it modifies nothing.
"""
import re
from pathlib import Path

from checks.framework import Finding

# alembic's own bookkeeping table. Created and managed by alembic itself, never
# declared in models and never excluded - it is neither, legitimately.
ALEMBIC_INTERNAL = {"alembic_version"}


def _declared_tables() -> set:
    """Tables alembic owns, i.e. present in the SQLAlchemy metadata."""
    from app.database import Base
    from app import models  # noqa: F401  - import registers the models

    return set(Base.metadata.tables.keys())


def _excluded_tables(repo_root: Path) -> set:
    """Tables explicitly handed to another authority in alembic/env.py.

    Parsed from source rather than imported, because importing env.py runs
    alembic's configuration machinery and needs a live connection. A checker
    that requires the thing it is checking to be healthy is not much of a
    checker.
    """
    env = repo_root / "alembic" / "env.py"
    if not env.is_file():
        return set()
    text = env.read_text(encoding="utf-8")
    m = re.search(r"EXCLUDED_TABLES\s*=\s*\{(.*?)\}", text, re.S)
    if not m:
        return set()
    return set(re.findall(r"[\"']([A-Za-z_][A-Za-z0-9_]*)[\"']", m.group(1)))


def _live_tables(session) -> set:
    from sqlalchemy import text

    rows = session.execute(text(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'public' AND table_type = 'BASE TABLE'"
    )).all()
    return {r[0] for r in rows}


def schema_ownership_check(session, repo_root: Path) -> list:
    """Assert every live table is claimed by exactly one authority."""
    if session is None:
        return [Finding("schema_ownership", None, "LIMITATION",
                        "no database session available - ownership not checked")]

    try:
        live = _live_tables(session)
    except Exception as e:
        return [Finding("schema_ownership", None, "WARNING",
                        f"could not list tables: {type(e).__name__}: {e}")]

    declared = _declared_tables()
    excluded = _excluded_tables(repo_root)

    findings = []

    unclaimed = sorted(live - declared - excluded - ALEMBIC_INTERNAL)
    for name in unclaimed:
        findings.append(Finding(
            "schema_ownership", name, "DEFECT",
            f"table '{name}' exists in the database but is claimed by no authority: "
            f"not declared in app/models.py and not named in alembic/env.py "
            f"EXCLUDED_TABLES. `alembic revision --autogenerate` will propose "
            f"dropping it, and that proposal will look like ordinary work. "
            f"Declare it or name it as externally owned."))

    both = sorted((live & declared) & excluded)
    for name in both:
        findings.append(Finding(
            "schema_ownership", name, "DEFECT",
            f"table '{name}' is claimed by BOTH authorities: it is declared in "
            f"app/models.py and also named in alembic/env.py EXCLUDED_TABLES. "
            f"Ambiguous ownership - the exclusion says another authority owns "
            f"the DDL while the model says alembic does. Remove one claim."))

    # Excluded but absent: not dangerous, but it means the boundary names
    # something that is not there - usually a rename nobody finished.
    stale = sorted(excluded - live)
    for name in stale:
        findings.append(Finding(
            "schema_ownership", name, "WARNING",
            f"'{name}' is named in alembic/env.py EXCLUDED_TABLES but no such "
            f"table exists. Either it was renamed or dropped and the exclusion "
            f"was not updated."))

    # PASS is keyed on the absence of DEFECTS, not the absence of all findings.
    # The stale-exclusion WARNING above is separate information: it says the
    # boundary names something that is not there, which is worth knowing but
    # does not mean the ownership invariant is broken. Suppressing the PASS
    # because a warning exists would leave a run that verified the invariant
    # looking identical to a run that never checked - which is the exact
    # failure this whole layer exists to catch.
    if not any(f.result == "DEFECT" for f in findings):
        findings.append(Finding(
            "schema_ownership", None, "PASS",
            f"all {len(live)} tables claimed by exactly one authority "
            f"({len(live & declared)} declared in models.py, "
            f"{len(live & excluded)} externally owned, "
            f"{len(live & ALEMBIC_INTERNAL)} alembic-internal)"))

    return findings




# ---------------------------------------------------------------------------
# H7. EVERY MAPPED TABLE IS CLASSIFIED - PRESERVED OR EPHEMERAL, EXACTLY ONE.
#
# app/preservation.py protects by default as of 2026-08-20, so an unclassified
# table is already safe. This checker exists because SAFE BECAUSE NOBODY LOOKED
# and SAFE BECAUSE SOMEBODY DECIDED are different states, and only one of them
# is a decision.
#
# The failure it closes is the one that had already happened: nine tables built
# in a single week were outside the old allowlist, 26,657 price rows and 2,195
# hardpoint slots were unguarded, and nothing anywhere said so. Under the
# inversion those tables are protected - but if the classification is allowed
# to fall behind the models again, the next genuinely ephemeral table gets the
# wrong default silently, which is the same class of defect pointing the other
# way.
#
# FINDINGS ONLY. It reads two frozensets and the SQLAlchemy metadata.
# ---------------------------------------------------------------------------


def preservation_classification_check(session, repo_root: Path) -> list:
    """Assert every mapped table is classified in exactly one list."""
    try:
        from app.preservation import classification_problems
    except Exception as e:                       # pragma: no cover - reported
        return [Finding("preservation_classification", None, "WARNING",
                        f"could not import app.preservation: "
                        f"{type(e).__name__}: {e}")]

    try:
        problems = classification_problems()
    except Exception as e:                       # pragma: no cover - reported
        return [Finding("preservation_classification", None, "WARNING",
                        f"classification could not be computed: "
                        f"{type(e).__name__}: {e}")]

    findings = [
        Finding("preservation_classification", _subject_of(text), "DEFECT", text)
        for text in problems
    ]

    if not findings:
        from app.preservation import EPHEMERAL_TABLES, PRESERVED_TABLES
        findings.append(Finding(
            "preservation_classification", None, "PASS",
            f"every mapped table is classified: {len(PRESERVED_TABLES)} "
            f"preserved, {len(EPHEMERAL_TABLES)} ephemeral. Protection is the "
            f"default, so anything unclassified would be guarded anyway - this "
            f"says somebody decided, rather than that nobody looked."))
    return findings


def _subject_of(problem: str):
    """The table name a problem line is about, so a finding has a subject.

    The problem strings are built by app.preservation.classification_problems
    and all of them open with a quoted table name.
    """
    m = re.search(r"'([A-Za-z_][A-Za-z0-9_]*)'", problem)
    return m.group(1) if m else None


CHECKERS = [
    ("schema_ownership", schema_ownership_check),
    ("preservation_classification", preservation_classification_check),
]
