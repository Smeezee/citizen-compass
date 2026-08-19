from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

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


@app.get("/health")
def health():
    return {"status": "ok"}
