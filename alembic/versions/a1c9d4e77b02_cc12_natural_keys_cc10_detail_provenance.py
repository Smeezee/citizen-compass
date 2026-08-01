"""CC-12 natural keys and CC-10 detail-table provenance

CC-12
  - components.class_name -> NOT NULL. It was nullable while sitting under
    uq_components_class_name, and Postgres permits unlimited NULLs in a unique
    constraint, so the constraint allowed unlimited duplicate rows on the very
    field importers upsert by. Nothing in the pipeline was idempotent.
  - ships gains uq_ships_name_manufacturer_id. It had no unique constraint at
    all, so running an importer twice produced duplicate ships.

CC-10
  - The five detail tables (weapon_details, missile_details,
    missile_rack_details, gimbal_mount_details, turret_details) gain provenance
    columns: created_at, updated_at, verification_source, confidence and
    last_verified_patch, plus a confidence CHECK constraint.

    These are the tables that receive promoted stats, so verification performed
    on them was being lost the moment it was written.

    confidence is NOT NULL DEFAULT 'unverified'. Existing rows therefore become
    'unverified', which will show on the site. That is intended and was approved
    knowingly: those rows genuinely are unverified and the site currently
    implies otherwise. Do not soften this to a friendlier default - it would
    reintroduce the exact false confidence CC-10 exists to remove.

    NOTE: these tables key on component_id. VerifiableMixin was NOT used,
    because its own `id` column would land alongside component_id and produce a
    composite primary key ['component_id', 'id'] - which create_all() accepts
    silently. A ProvenanceMixin without `id` is used instead.

Revision ID: a1c9d4e77b02
Revises: 219446ebce6a
Create Date: 2026-08-01
"""
import sqlalchemy as sa
from alembic import op

revision = "a1c9d4e77b02"
down_revision = "219446ebce6a"
branch_labels = None
depends_on = None

DETAIL_TABLES = (
    "weapon_details",
    "missile_details",
    "missile_rack_details",
    "gimbal_mount_details",
    "turret_details",
)

CONFIDENCE_LEVELS = ("unverified", "low", "medium", "high", "verified")


def upgrade() -> None:
    # ---------------- CC-12 ----------------
    # Guard rather than assume. If data violating either constraint has appeared
    # since this migration was written, fail loudly here instead of letting
    # Postgres emit a less specific error - and never silently "clean" it.
    conn = op.get_bind()

    bad_null = conn.execute(
        sa.text("SELECT count(*) FROM components WHERE class_name IS NULL")
    ).scalar()
    if bad_null:
        raise RuntimeError(
            f"{bad_null} components row(s) have class_name IS NULL. "
            "Resolve the data deliberately before migrating - this migration "
            "will not invent values to make the constraint fit."
        )

    dup_cn = conn.execute(
        sa.text(
            "SELECT count(*) FROM (SELECT class_name FROM components "
            "WHERE class_name IS NOT NULL GROUP BY class_name HAVING count(*) > 1) d"
        )
    ).scalar()
    if dup_cn:
        raise RuntimeError(f"{dup_cn} duplicate components.class_name value(s) present.")

    dup_ship = conn.execute(
        sa.text(
            "SELECT count(*) FROM (SELECT name, manufacturer_id FROM ships "
            "GROUP BY name, manufacturer_id HAVING count(*) > 1) d"
        )
    ).scalar()
    if dup_ship:
        raise RuntimeError(f"{dup_ship} duplicate ships(name, manufacturer_id) pair(s) present.")

    op.alter_column(
        "components", "class_name",
        existing_type=sa.String(length=150),
        nullable=False,
    )
    op.create_unique_constraint(
        "uq_ships_name_manufacturer_id", "ships", ["name", "manufacturer_id"]
    )

    # ---------------- CC-10 ----------------
    for table in DETAIL_TABLES:
        op.add_column(
            table,
            sa.Column(
                "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
            ),
        )
        op.add_column(
            table,
            sa.Column(
                "updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
            ),
        )
        op.add_column(table, sa.Column("verification_source", sa.String(length=255), nullable=True))
        op.add_column(
            table,
            sa.Column(
                "confidence", sa.String(length=20),
                server_default="unverified", nullable=False,
            ),
        )
        op.add_column(table, sa.Column("last_verified_patch", sa.Integer(), nullable=True))
        op.create_foreign_key(
            f"fk_{table}_last_verified_patch_patches",
            table, "patches", ["last_verified_patch"], ["id"],
        )
        op.create_check_constraint(
            f"ck_{table}_confidence_valid",
            table,
            sa.text("confidence IN %s" % (CONFIDENCE_LEVELS,)),
        )


def downgrade() -> None:
    """Real downgrade, not a stub. Reverses every change above in inverse order.

    Dropping the CC-10 columns discards whatever provenance had been recorded on
    detail rows - that is inherent to reversing the change, not an oversight.
    """
    # ---------------- CC-10 ----------------
    for table in DETAIL_TABLES:
        op.drop_constraint(f"ck_{table}_confidence_valid", table, type_="check")
        op.drop_constraint(f"fk_{table}_last_verified_patch_patches", table, type_="foreignkey")
        op.drop_column(table, "last_verified_patch")
        op.drop_column(table, "confidence")
        op.drop_column(table, "verification_source")
        op.drop_column(table, "updated_at")
        op.drop_column(table, "created_at")

    # ---------------- CC-12 ----------------
    op.drop_constraint("uq_ships_name_manufacturer_id", "ships", type_="unique")
    op.alter_column(
        "components", "class_name",
        existing_type=sa.String(length=150),
        nullable=True,
    )
