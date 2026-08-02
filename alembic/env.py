import os
import sys
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

from app.database import Base  # noqa: E402
from app import models  # noqa: E402,F401

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# ---------------------------------------------------------------------------
# Tables owned by another authority, deliberately invisible to autogenerate.
#
# THE HAZARD THIS CLOSES (2026-08-02): these tables exist in the database but
# in no SQLAlchemy model, so `alembic revision --autogenerate` proposed
# `remove_table` for all three. Applying that migration would have dropped the
# findings the checker layer had just spent a night producing. Autogenerate
# output looks like ordinary work; nothing in it announces the loss.
#
# WHY EXCLUSION RATHER THAN DECLARATION, for these three specifically:
# they are the checker subsystem's operational telemetry, not application
# domain data. `schema-init/main.go` owns their DDL. They are written only by
# checks/findings_store.py and checks/framework.py, read by nothing in app/,
# and their schema moves with the checker layer rather than with the app.
#
# This is the "one writer per artifact" rule applied to schema. Two authorities
# over one table is the same defect as two watchers on one handoff file or two
# scheduled tasks on one target - both of which this project has already been
# bitten by. Naming the boundary is applying that rule, not evading it.
#
# NAMED EXPLICITLY, never pattern-matched. A prefix rule like "pipeline_*"
# would silently adopt the next table someone adds, which is precisely the
# failure being closed. A new table belongs in models.py OR in this list, as a
# deliberate act - and checks/schema_checks.py enforces exactly that, reporting
# any table claimed by neither or by both.
#
# ship_registry is NOT here on purpose: it is domain data, it is what
# registry_sync compares the database against, and it is now declared in
# app/models.py.
EXCLUDED_TABLES = {
    "pipeline_check_results",
    "pipeline_findings",
    "pipeline_check_runs",
}


def include_object(object, name, type_, reflected, compare_to):
    """Hide externally-owned tables from autogenerate.

    Returning False for a table means autogenerate neither creates nor drops
    it. It does not stop a hand-written migration touching it - that is a
    different control, and checks/schema_checks.py is where it lives.
    """
    if type_ == "table" and name in EXCLUDED_TABLES:
        return False
    if type_ == "index" and getattr(object, "table", None) is not None:
        if object.table.name in EXCLUDED_TABLES:
            return False
    return True
# ---------------------------------------------------------------------------


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        include_object=include_object,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
