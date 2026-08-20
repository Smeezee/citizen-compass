import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# G1 (2026-08-19): a missing database URL must not take the whole app down.
#
# This line used to be:
#
#     DATABASE_URL = os.environ.get("DATABASE_URL") or os.environ["RAILWAY_DATABASE_URL"]
#
# With neither variable set that is a KeyError AT IMPORT. uvicorn never binds,
# so every route 502s - including /health, the one route whose entire job is to
# tell you what is wrong. The outage and the diagnostic fail together, which is
# how an evening gets spent guessing.
#
# Note which fault this covers. An UNREACHABLE url is lazy: create_engine does
# not connect, so the app boots fine and fails per query. An ABSENT url is
# eager: it kills the process. The two are different faults and the previous
# test only ever simulated the harmless one.
#
# So: absent is survivable, and it reads differently from unreachable, which
# reads differently from healthy. See database_status().
DATABASE_URL_VARS = ("DATABASE_URL", "RAILWAY_DATABASE_URL")


class DatabaseUnconfigured(RuntimeError):
    """Raised when a database-backed path is reached with no URL configured.

    app/main.py turns this into a 503 carrying the same reason string that
    /health reports, so the answer is identical wherever you happen to knock.
    """


def _read_database_url():
    for name in DATABASE_URL_VARS:
        value = os.environ.get(name)
        if value:
            return name, value
    return None, None


DATABASE_URL_SOURCE, DATABASE_URL = _read_database_url()

UNCONFIGURED_REASON = (
    "No database URL is configured. Looked for "
    + " and ".join(DATABASE_URL_VARS)
    + "; neither is set in this environment."
)


def _redact(message):
    """Keep the database password out of anything we hand back over HTTP.

    Driver errors name the host, port and user, which is exactly what you want
    when diagnosing. They are not supposed to carry the password - but /health
    is public and unauthenticated, so this does not run on "supposed to".
    """
    text_out = str(message)
    if DATABASE_URL and "@" in DATABASE_URL and "://" in DATABASE_URL:
        credentials = DATABASE_URL.split("://", 1)[1].rsplit("@", 1)[0]
        if ":" in credentials:
            secret = credentials.split(":", 1)[1]
            if secret:
                text_out = text_out.replace(secret, "***")
    return text_out[:500]


def _connect_args(url):
    # psycopg2 only. A bad host must fail in seconds: without this, connecting
    # blocks long enough that the platform proxy times out first and turns an
    # unreachable database back into the uniform 502 this item exists to remove.
    if url.startswith("postgres"):
        return {"connect_timeout": 5}
    return {}


if DATABASE_URL:
    engine = create_engine(DATABASE_URL, connect_args=_connect_args(DATABASE_URL))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:

    class _UnconfiguredSessionFactory:
        """Stands in for sessionmaker when no URL was found.

        Deliberately not None. `SessionLocal = None` fails with "NoneType is
        not callable", which tells the reader nothing about the actual fault.
        This names both variables that were checked.
        """

        def __call__(self, *args, **kwargs):
            raise DatabaseUnconfigured(UNCONFIGURED_REASON)

    engine = None
    SessionLocal = _UnconfiguredSessionFactory()


# G2: one line at startup saying which variable supplied the URL, or that none
# did. Once, at import. Not a heartbeat, not per request.
#
# Written to stderr rather than through logging on purpose: at import time the
# root logger usually has no handlers, so an INFO record goes nowhere and a
# startup diagnostic that can be silently swallowed is the exact failure this
# item exists to remove. stderr rather than stdout so scripts that emit parseable
# output on stdout stay clean. Platform log collectors capture both.
def _startup_line():
    if DATABASE_URL_SOURCE:
        return "citizen-compass: database URL supplied by %s" % DATABASE_URL_SOURCE
    return "citizen-compass: %s Running DEGRADED - database-backed routes will 503." % (
        UNCONFIGURED_REASON,
    )


print(_startup_line(), file=sys.stderr, flush=True)


if engine is not None:
    # Preservation, installed at the engine so nothing downstream has to remember.
    #
    # Citizen Compass never deletes a preserved row: an entity absent from a patch
    # is MARKED absent, not dropped. Wiring this into each importer would work right
    # up until somebody wrote a new one, so it binds here instead - every consumer of
    # this engine inherits it, including code that does not know the rule exists.
    #
    # It blocks row removal (DELETE / TRUNCATE / session.delete) on the preserved
    # tables only. DDL is untouched, so alembic migrations and the e2e harness's
    # throwaway database are unaffected - both proven in
    # checks/_verify_never_delete_guard.py.
    from app.preservation import install_never_delete_guard  # noqa: E402

    install_never_delete_guard(engine)


class Base(DeclarativeBase):
    pass


def database_status():
    """What /health reports. Three distinct answers, never collapsed into two.

    Rule 12: a health check that does not touch the database is a check that
    cannot fail. This one issues SELECT 1 and reports what came back, so
    "unreachable" is something observed rather than something assumed from the
    presence of a string in an environment variable.
    """
    if engine is None:
        return {
            "status": "degraded",
            "database": "unconfigured",
            "checked": list(DATABASE_URL_VARS),
            "reason": UNCONFIGURED_REASON,
        }
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001 - any driver failure is unreachable
        return {
            "status": "degraded",
            "database": "unreachable",
            "database_url_source": DATABASE_URL_SOURCE,
            "reason": "%s: %s" % (type(exc).__name__, _redact(exc)),
        }
    return {
        "status": "ok",
        "database": "ok",
        "database_url_source": DATABASE_URL_SOURCE,
    }


def get_db():
    if engine is None:
        raise DatabaseUnconfigured(UNCONFIGURED_REASON)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
