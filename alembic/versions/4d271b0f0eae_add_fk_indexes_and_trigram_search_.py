"""add fk indexes and trigram search indexes

Revision ID: 4d271b0f0eae
Revises: 8f37bb885052
Create Date: 2026-07-24 14:48:08.576134

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d271b0f0eae'
down_revision: Union[str, Sequence[str], None] = '8f37bb885052'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

BTREE_INDEXES = [
    ("ix_ship_dealer_listings_ship_id", "ship_dealer_listings", "ship_id"),
    ("ix_ship_dealer_listings_dealer_id", "ship_dealer_listings", "dealer_id"),
    ("ix_ships_manufacturer_id", "ships", "manufacturer_id"),
    ("ix_pledge_links_ship_id", "pledge_links", "ship_id"),
]

TRGM_INDEXES = ["ix_ships_name_trgm", "ix_ships_role_trgm"]

ALL_INDEXES = [name for name, _, _ in BTREE_INDEXES] + TRGM_INDEXES


def upgrade() -> None:
    """Upgrade schema."""
    for index_name, table_name, column_name in BTREE_INDEXES:
        op.create_index(index_name, table_name, [column_name])

    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute(
        "CREATE INDEX ix_ships_name_trgm ON ships USING GIN (name gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX ix_ships_role_trgm ON ships USING GIN (role gin_trgm_ops)"
    )

    _verify_indexes_exist()


def _verify_indexes_exist() -> None:
    conn = op.get_bind()
    existing = {
        row[0]
        for row in conn.execute(
            sa.text("SELECT indexname FROM pg_indexes WHERE schemaname = 'public'")
        )
    }
    missing = [name for name in ALL_INDEXES if name not in existing]
    if missing:
        raise RuntimeError(
            f"Migration verification failed — missing indexes after creation: {missing}"
        )


def downgrade() -> None:
    """Downgrade schema."""
    for index_name in TRGM_INDEXES:
        op.execute(f"DROP INDEX IF EXISTS {index_name}")
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")

    for index_name, table_name, _ in BTREE_INDEXES:
        op.drop_index(index_name, table_name=table_name)
