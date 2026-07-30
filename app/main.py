from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routers import dealers, manufacturers, missiles, ships, turrets, weapons

app = FastAPI(title="Citizen Compass")

app.include_router(ships.router)
app.include_router(manufacturers.router)
app.include_router(dealers.router)
app.include_router(weapons.router)
app.include_router(missiles.router)
app.include_router(turrets.router)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}
