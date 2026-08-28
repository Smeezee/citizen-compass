"""
Phase D acceptance: the shop API, verified against a RUNNING SERVER.

RULE16: INDEPENDENT - it starts the real application and makes real HTTP requests
to it, then judges the responses against expectations written here. The
file says in its own second paragraph why it refuses the easier route: a
TestClient exercises the same handlers but proves neither that the app
starts nor that the router is mounted. Nothing is imported from the code
under test - the only channel is the wire.

§D says "verified against the running API, not against the code", and that
distinction is the whole point of this file. A FastAPI TestClient would be
easier and would exercise the same handlers, but it would not prove that the
app starts, that the router is actually mounted in app/main.py, or that a
response serialises over the wire. Every one of those has been the real
failure at some point on some project.

So this starts a real uvicorn on a spare port, waits for /health, and makes
real HTTP requests. It stops the server afterwards.

THE CONTROL §D ASKS FOR
-----------------------
"a uuid that does not exist returns a clean 404, not a 500 and not an empty
200." All three wrong answers are checked for by name, because they fail
differently and only one of them is obvious:

    500  the handler crashed - loud, at least
    200  with an empty list - THE DANGEROUS ONE. It says "this item exists and
         nobody sells it" when the truth is "there is no such item". §3.6
         makes "nobody sells this" a real, displayable answer, which is
         exactly what makes confusing the two so costly here.
    404  correct

Run: venv/Scripts/python.exe checks/_verify_shop_api.py
"""

import json
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

passed, failed = 0, []


def record(ok, label, detail=""):
    global passed
    if ok:
        passed += 1
        print(f"  ok   {label}")
    else:
        failed.append(f"{label} {detail}".strip())
        print(f"  FAIL {label} {detail}")


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def get(base, path):
    """(status, parsed body). Never raises for an HTTP error status - the
    status IS the thing under test."""
    try:
        with urllib.request.urlopen(base + path, timeout=30) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8")
        try:
            return exc.code, json.loads(raw)
        except json.JSONDecodeError:
            return exc.code, raw
    except Exception as exc:  # noqa: BLE001
        return None, f"{type(exc).__name__}: {exc}"


def main():
    port = free_port()
    base = f"http://127.0.0.1:{port}"
    print(f"--- starting a real uvicorn on port {port} ---")
    server = subprocess.Popen(
        [str(REPO_ROOT / "venv" / "Scripts" / "python.exe"), "-m", "uvicorn",
         "app.main:app", "--port", str(port), "--log-level", "warning"],
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )

    try:
        for _ in range(60):
            status, _body = get(base, "/health")
            if status == 200:
                break
            time.sleep(0.5)
        else:
            print("  FAIL the server never became healthy")
            out = server.stdout.read().decode("utf-8", "replace")[-2000:]
            print(out)
            return 1
        record(True, "the app starts and /health answers 200")

        # ---------------- D1 ----------------------------------------------
        print("\n--- D1: list + filter + detail ---")
        status, body = get(base, "/api/v1/shop/categories?limit=5")
        record(status == 200 and set(body) == {"items", "total", "limit", "offset"},
               f"categories returns the locked Page envelope (HTTP {status})",
               f"keys were {sorted(body) if isinstance(body, dict) else body}")
        record(body.get("total") == 100,
               f"and reports all 100 categories as total (got {body.get('total')})")
        record(len(body.get("items", [])) == 5,
               "while returning only the 5 asked for")

        status, body = get(base, "/api/v1/shop/categories?limit=99999")
        record(status == 200 and body.get("limit") == 200,
               f"an over-large limit is CLAMPED and the response says so "
               f"(limit={body.get('limit')})",
               "the response echoed the requested limit, so a caller cannot "
               "tell it was clamped")

        status, body = get(base, "/api/v1/shop/terminals?star_system=Stanton&limit=1")
        record(status == 200 and body.get("total") == 509,
               f"terminals filter by star system (Stanton total="
               f"{body.get('total')}, expected 509)")
        record(bool(body["items"][0].get("resolved_path")),
               f"and each carries a readable location: "
               f"{body['items'][0].get('resolved_path')!r}")
        record("None" not in str(body["items"][0].get("resolved_path")),
               "with no 'None' segment in it")

        status, body = get(base, "/api/v1/shop/terminals/1")
        record(status == 200 and body.get("uex_id") == 1, "terminal detail by uex_id")

        # ---------------- D2 ----------------------------------------------
        print("\n--- D2: item -> every terminal selling it ---")
        status, body = get(base, "/api/v1/shop/items/item:1/prices")
        record(status == 200 and body["item"]["name"] == "Omnisky III Cannon",
               "an item resolves by prefixed uex_id")
        record(body["price_count"] > 0 and body["sold_anywhere"] is True,
               f"and carries {body.get('price_count')} price rows")
        row = body["prices"][0]
        record("price_buy" in row and "price_sell" in row,
               "buy and sell are SEPARATE fields (E3 / §3.1)")
        record(not any(k in row for k in ("price", "price_avg", "average")),
               "and there is no combined or averaged price field anywhere",
               f"row keys: {sorted(row)}")
        record(row.get("location") and "None" not in str(row["location"]),
               f"each price row carries a resolved location: {row.get('location')!r}")
        record(bool(row.get("snapshot_key")),
               f"and its snapshot: {row.get('snapshot_key')}")

        status, body = get(base, "/api/v1/shop/items/dec0f5dc-68c1-4058-b60d-a7a9911a8e73/prices")
        record(status == 200 and body["item"]["name"] == "CR-60",
               "an item resolves by an unambiguous uuid")

        # ---------------- D2 CONTROL --------------------------------------
        print("\n--- D2 CONTROL: the three ways this could go wrong ---")
        status, body = get(base, "/api/v1/shop/items/00000000-0000-0000-0000-000000000000/prices")
        record(status == 404, f"a uuid that does not exist returns 404 (got {status})")
        record(status != 500, "and NOT a 500")
        record(not (status == 200 and body.get("price_count") == 0),
               "and NOT an empty 200, which would say 'this exists and nobody "
               "sells it' about a thing that does not exist")
        record(isinstance(body, dict) and "detail" in body,
               "the 404 body explains itself rather than being bare")

        status, body = get(base, "/api/v1/shop/items/not-a-uuid-at-all/prices")
        record(status == 404, f"garbage identifier returns 404, not 500 (got {status})")

        status, body = get(base, "/api/v1/shop/items/7bd374e9-9d2f-4659-94cf-840e79d23b34/prices")
        record(status == 409,
               f"a uuid worn by TEN items returns 409, not a silent pick "
               f"(got {status})")
        candidates = (body.get("detail") or {}).get("candidates") \
            if isinstance(body.get("detail"), dict) else None
        record(candidates and len(candidates) == 10,
               f"and lists all {len(candidates) if candidates else 0} candidates "
               f"so the caller can re-ask")

        status, body = get(base, "/api/v1/shop/items/1/prices")
        record(status == 409,
               "a bare uex_id that exists as BOTH an item and a commodity "
               "returns 409 rather than guessing which was meant")

        # ---------------- D3 ----------------------------------------------
        print("\n--- D3: terminal -> what it sells ---")
        status, body = get(base, "/api/v1/shop/terminals/111/inventory?limit=3")
        record(status == 200 and body["total"] > 0,
               f"a terminal lists its stock ({body.get('total')} rows)")
        record(len(body["items"]) == 3, "paginated to the requested size")
        record(all("price_buy" in i and "price_sell" in i for i in body["items"]),
               "every row keeps buy and sell separate")

        status, body = get(base, "/api/v1/shop/terminals/99999999/inventory")
        record(status == 404,
               f"an unknown terminal returns 404, not an empty 200 (got {status})")

        # ---------------- D4 ----------------------------------------------
        print("\n--- D4: search ---")
        status, body = get(base, "/api/v1/shop/search?q=Omnisky")
        record(status == 200 and body["total"] > 0,
               f"name substring search finds {body.get('total')} items")
        first = body["items"][0]
        record("price_buy_min" in first and "price_buy_max" in first,
               "results carry a price RANGE, not an average")
        record(not any("avg" in k for k in first),
               "and no averaged field is exposed anywhere")

        status, body = get(base, "/api/v1/shop/search?category=Guns&limit=1")
        record(status == 200 and body["total"] > 0,
               f"category filter works ({body.get('total')} in Guns)")

        status, body = get(base, "/api/v1/shop/search?min_price=1000&max_price=2000&limit=1")
        record(status == 200, f"price range filter works (HTTP {status})")

        status, body = get(base, "/api/v1/shop/search?min_price=9000&max_price=10")
        record(status == 422,
               f"min above max is REFUSED with 422 rather than returning an "
               f"empty list that looks like 'nothing is priced in that range' "
               f"(got {status})")

        # ---------------- the honest empty state (E-control, checked here) --
        print("\n--- a search matching nothing must be an honest empty ---")
        status, body = get(base, "/api/v1/shop/search?q=zzzz_no_such_item_zzzz")
        record(status == 200, f"matching nothing is a 200, not an error (got {status})")
        record(body.get("items") == [] and body.get("total") == 0,
               f"with an explicitly empty list and total 0 "
               f"(items={body.get('items')}, total={body.get('total')})")

    finally:
        server.terminate()
        try:
            server.wait(timeout=15)
        except subprocess.TimeoutExpired:
            server.kill()
        print("\n--- server stopped ---")

    print("=" * 62)
    if failed:
        print(f"FAILED {len(failed)} of {passed + len(failed)}:")
        for x in failed:
            print("  -", x)
        return 1
    print(f"All {passed} assertions passed against a real HTTP server.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
