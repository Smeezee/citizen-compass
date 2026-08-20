from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.database import DATABASE_URL_VARS, DatabaseUnconfigured, database_status

from app.routers import (
    dealers,
    manufacturers,
    missiles,
    ships,
    shop,
    turrets,
    weapons,
)

app = FastAPI(title="Citizen Compass")

# CORS, added 2026-08-19 with the shop API (E1).
#
# WHY IT IS NEEDED NOW AND WAS NOT BEFORE: the site is served from Netlify and
# the API from Railway - different origins. Nothing had fetched across that
# boundary until find.html stopped using invented data and started calling
# /api/v1/shop. Without this the browser blocks every request and the page
# shows its "we can't reach the price data" state while the API is perfectly
# healthy - a failure that looks like an outage and is not one.
#
# Read-only endpoints, so GET and OPTIONS only. No credentials: this API has
# no auth and no cookies, and allow_credentials with a wildcard origin is
# rejected by browsers anyway. Deliberately not "*" for methods - a wildcard
# there would advertise POST/DELETE on an API that serves neither.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?|https://.*\.netlify\.app|https://citizencompass\.[a-z]+",
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(ships.router)
app.include_router(manufacturers.router)
app.include_router(dealers.router)
app.include_router(weapons.router)
app.include_router(missiles.router)
app.include_router(turrets.router)
app.include_router(shop.router)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


# G1: a database-backed route with no URL configured answers 503 and says why,
# rather than 500-ing on an unhandled KeyError - or, before this item, never
# getting as far as answering at all.
#
# get_db() is a dependency, so this handler is what every one of those routes
# inherits without any of them being edited. The reason string is the same one
# /health reports, so the two cannot drift into telling different stories.
@app.exception_handler(DatabaseUnconfigured)
def database_unconfigured_handler(request: Request, exc: DatabaseUnconfigured):
    return JSONResponse(
        status_code=503,
        content={
            "detail": str(exc),
            "database": "unconfigured",
            "checked": list(DATABASE_URL_VARS),
        },
    )


@app.get("/health")
def health():
    """Three answers, never two.

      ok           - a URL was found AND SELECT 1 came back.
      unconfigured - neither environment variable is set. Names both.
      unreachable  - a URL was found and the database did not answer.

    The last two are both "degraded" but they are different faults with
    different fixes, so they never collapse into one string.

    HTTP 200 even when degraded, deliberately. A non-200 here is what platform
    health checks restart on, and a restart loop is how a diagnosable degraded
    boot turns back into the uniform 502 this endpoint exists to replace. The
    status is in the body, where something can read it. Reverses in one line if
    that trade turns out to be wrong.
    """
    return database_status()
