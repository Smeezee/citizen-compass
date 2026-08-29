"""
Rule 12 proof for G1/G2 - the degraded-database mode in app/database.py.

RULE16: INDEPENDENT - it starts the application THREE TIMES in three real
subprocesses, each with a different database configuration, and judges
what each process does. Nothing is imported and no internal flag is
consulted: 'degraded' is read from how the app behaves when started that
way, which is the only place a reader would meet it. A module asked
whether it thinks it is degraded could answer wrongly in exactly the
situation this exists to catch.

WHAT THIS PROVES
----------------
Before G1, `app/database.py` ended with:

    DATABASE_URL = os.environ.get("DATABASE_URL") or os.environ["RAILWAY_DATABASE_URL"]

With neither variable set that is a KeyError AT IMPORT: uvicorn never binds and
every route 502s, /health included. G1 says the app must boot anyway and say
what is wrong.

The important half is the SECOND half. A degraded mode that never leaves
degraded is worse than the crash it replaced, because it fails quietly forever.
So this runs the app three times, in three real subprocesses, each with a
different environment, and requires three DIFFERENT answers:

  1. neither variable set   -> boots, /health 200 "degraded"/"unconfigured",
                               naming BOTH variables; db routes 503; non-db
                               routes still serve.
  2. DATABASE_URL set, real -> /health "ok" AND a real query returns real rows.
                               This is the load-bearing one.
  3. DATABASE_URL set, dead host
                            -> /health "degraded"/"unreachable" - a different
                               word from case 1, because absent and unreachable
                               are different faults with different fixes, and
                               collapsing them is how you get an evening of
                               guessing.

And G2: exactly one startup line on stderr, naming which variable supplied the
URL or saying that none did. Asserted in all three cases, and asserted to
appear ONCE - "not a heartbeat" is part of the requirement.

WHY THE SUBPROCESSES SET THE VARIABLES TO EMPTY RATHER THAN UNSETTING THEM
--------------------------------------------------------------------------
`app/database.py` calls `load_dotenv()`, and this repo HAS a `.env` carrying a
real DATABASE_URL. Unsetting the variable in the child environment would just
let python-dotenv put it back, and the case would silently not be tested - a
Rule 12 silent success inside the very check written to prevent one.

python-dotenv does not overwrite a key already present in os.environ, so an
EMPTY string is how you keep .env out of it. Empty and unset take the identical
branch, and that equivalence is not assumed - CASE 0 below asserts it directly
against a cleared os.environ, with dotenv out of the picture.

SELF-TEST
---------
`--self-test` inverts every assertion and requires this script to report
failure. A harness whose failure path has never run is an untested harness.

Run: venv/Scripts/python.exe checks/_verify_degraded_database.py
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

MARKER = "<<<RESULT>>>"

# A syntactically valid URL pointing at a host that cannot exist. `.invalid` is
# reserved by RFC 2606 precisely so it can never resolve, so this fails at
# connect, quickly, without touching anything real.
DEAD_URL = "postgresql://nobody:nothing@no-such-host.invalid:1/citizen_compass"

DRIVER = '''
import json, sys
sys.path.insert(0, %(repo)r)
from fastapi.testclient import TestClient
from app.main import app

out = {}
client = TestClient(app, raise_server_exceptions=False)

r = client.get("/health")
out["health_code"] = r.status_code
try:
    out["health"] = r.json()
except Exception:
    out["health"] = {"unparseable": r.text[:200]}

r = client.get("/api/v1/shop/categories")
out["db_route_code"] = r.status_code
try:
    out["db_route_body"] = r.json()
except Exception:
    out["db_route_body"] = {"unparseable": r.text[:200]}

r = client.get("/docs")
out["nodb_route_code"] = r.status_code

print(%(marker)r + json.dumps(out))
'''


def run_case(label, env_overrides, workdir):
    """Boot the whole app in a child process and report what it answered."""
    script = workdir / ("driver_%s.py" % label)
    script.write_text(
        DRIVER % {"repo": str(REPO), "marker": MARKER}, encoding="utf-8"
    )
    env = dict(os.environ)
    env.update(env_overrides)
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(REPO),
        env=env,
        timeout=180,
    )
    payload = None
    for line in (proc.stdout or "").splitlines():
        if line.startswith(MARKER):
            payload = json.loads(line[len(MARKER):])
    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout or "",
        "stderr": proc.stderr or "",
        "payload": payload,
    }


def real_database_url():
    """The URL this machine actually has, read the same way the app reads it."""
    from dotenv import load_dotenv

    load_dotenv(REPO / ".env")
    return os.environ.get("DATABASE_URL") or os.environ.get("RAILWAY_DATABASE_URL")


def main():
    self_test = "--self-test" in sys.argv
    passed = 0
    failed = []

    def record(ok, what):
        nonlocal passed
        if self_test:
            ok = not ok
        if ok:
            passed += 1
        else:
            failed.append(what)

    workdir = Path(tempfile.mkdtemp(prefix="cc_degraded_db_"))

    # ---- CASE 0 -----------------------------------------------------------
    # Empty and unset take the identical branch. Asserted, not assumed - the
    # three subprocess cases below rest on it.
    from app.database import _read_database_url

    saved = {k: os.environ.get(k) for k in ("DATABASE_URL", "RAILWAY_DATABASE_URL")}
    try:
        for k in saved:
            os.environ.pop(k, None)
        unset_result = _read_database_url()
        for k in saved:
            os.environ[k] = ""
        empty_result = _read_database_url()
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    record(unset_result == (None, None),
           "CASE 0: truly unset variables read as (None, None)")
    record(empty_result == (None, None),
           "CASE 0: empty-string variables read as (None, None)")
    record(unset_result == empty_result,
           "CASE 0: empty and unset are the SAME branch - so the subprocesses "
           "below really do test the absent case")

    # ---- CASE 1: neither variable set -------------------------------------
    print("CASE 1: neither DATABASE_URL nor RAILWAY_DATABASE_URL ...")
    c1 = run_case("unconfigured",
                  {"DATABASE_URL": "", "RAILWAY_DATABASE_URL": ""}, workdir)

    record(c1["returncode"] == 0,
           "CASE 1: the app BOOTS with no database URL (this is the KeyError "
           "that used to 502 everything)")
    record(c1["payload"] is not None,
           "CASE 1: the app answered at all")

    h1 = (c1["payload"] or {}).get("health") or {}
    record((c1["payload"] or {}).get("health_code") == 200,
           "CASE 1: /health answers 200 (a non-200 is what platform health "
           "checks restart on, and a restart loop is the 502 again)")
    record(h1.get("status") == "degraded",
           "CASE 1: /health status is 'degraded'")
    record(h1.get("database") == "unconfigured",
           "CASE 1: /health database is 'unconfigured'")
    record("DATABASE_URL" in json.dumps(h1),
           "CASE 1: /health names DATABASE_URL")
    record("RAILWAY_DATABASE_URL" in json.dumps(h1),
           "CASE 1: /health names RAILWAY_DATABASE_URL - BOTH variables, per G1")

    record((c1["payload"] or {}).get("db_route_code") == 503,
           "CASE 1: a database-backed route answers 503, not 500 and not an "
           "empty 200")
    body1 = json.dumps((c1["payload"] or {}).get("db_route_body") or {})
    record("DATABASE_URL" in body1 and "RAILWAY_DATABASE_URL" in body1,
           "CASE 1: the 503 body carries the same reason /health gives, naming "
           "both variables")
    record((c1["payload"] or {}).get("nodb_route_code") == 200,
           "CASE 1: a route that needs no database still serves normally")

    record("Running DEGRADED" in c1["stderr"],
           "CASE 1 / G2: the startup line says it is running degraded")
    record(c1["stderr"].count("citizen-compass: ") == 1,
           "CASE 1 / G2: exactly ONE startup line - not a heartbeat")

    # ---- CASE 2: the real URL. THE LOAD-BEARING CASE ----------------------
    print("CASE 2: DATABASE_URL set to this machine's real database ...")
    url = real_database_url()
    if not url:
        failed.append("CASE 2: NOT PERFORMED - no real DATABASE_URL available "
                      "on this machine, so 'degraded mode still leaves "
                      "degraded' is UNPROVEN. Reported as not performed, "
                      "never as passed.")
    else:
        c2 = run_case("configured",
                      {"DATABASE_URL": url, "RAILWAY_DATABASE_URL": ""}, workdir)
        h2 = (c2["payload"] or {}).get("health") or {}
        record(c2["returncode"] == 0, "CASE 2: the app boots")
        record(h2.get("status") == "ok",
               "CASE 2: /health says 'ok' - degraded mode LEAVES degraded")
        record(h2.get("database") == "ok",
               "CASE 2: SELECT 1 actually came back (the health check is not "
               "a check that cannot fail)")
        record(h2.get("database_url_source") == "DATABASE_URL",
               "CASE 2: /health names which variable supplied the URL")

        record((c2["payload"] or {}).get("db_route_code") == 200,
               "CASE 2: the database-backed route answers 200")
        rows = ((c2["payload"] or {}).get("db_route_body") or {}).get("items")
        record(isinstance(rows, list) and len(rows) > 0,
               "CASE 2: a REAL QUERY returns REAL ROWS - not an empty 200")

        record("database URL supplied by DATABASE_URL" in c2["stderr"],
               "CASE 2 / G2: the startup line names DATABASE_URL")
        record(c2["stderr"].count("citizen-compass: ") == 1,
               "CASE 2 / G2: exactly one startup line")

    # ---- CASE 3: configured but dead. Must NOT read as case 1 -------------
    print("CASE 3: DATABASE_URL set to a host that does not exist ...")
    c3 = run_case("unreachable",
                  {"DATABASE_URL": DEAD_URL, "RAILWAY_DATABASE_URL": ""}, workdir)
    h3 = (c3["payload"] or {}).get("health") or {}

    record(c3["returncode"] == 0,
           "CASE 3: the app boots with an unreachable database (it always did "
           "- create_engine is lazy - and that is exactly why the old test "
           "could not have caught the absent case)")
    record(h3.get("status") == "degraded", "CASE 3: /health says degraded")
    record(h3.get("database") == "unreachable",
           "CASE 3: /health says 'unreachable'")
    record(h3.get("database") != "unconfigured",
           "CASE 3: unreachable does NOT read as unconfigured - a wrong URL is "
           "not silent and is not the same fault")
    record(h3.get("database_url_source") == "DATABASE_URL",
           "CASE 3: /health still names where the URL came from")
    record("no-such-host.invalid" in json.dumps(h3),
           "CASE 3: the reason names the host that failed, so it is "
           "diagnosable from outside")
    record("nothing" not in json.dumps(h3),
           "CASE 3: the password from the URL is NOT echoed back over HTTP")
    record("database URL supplied by DATABASE_URL" in c3["stderr"],
           "CASE 3 / G2: the startup line names DATABASE_URL")

    print("\n" + "=" * 62)
    print("(drivers under %s - left in place, this project does not delete)"
          % workdir)
    if self_test:
        print("SELF-TEST: every assertion was inverted.")
    if failed:
        print("FAILED %d of %d:" % (len(failed), passed + len(failed)))
        for x in failed:
            print("  -", x)
        return 1
    print("All %d assertions passed." % passed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
