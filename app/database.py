import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

DATABASE_URL = os.environ.get("DATABASE_URL") or os.environ["RAILWAY_DATABASE_URL"]

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
