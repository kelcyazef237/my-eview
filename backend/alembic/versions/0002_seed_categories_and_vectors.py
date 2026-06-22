"""Seed fixed categories and vectors."""

import sqlalchemy as sa
from alembic import op

from app.reference_data import CATEGORY_ROWS, VECTOR_ROWS

# revision identifiers, used by Alembic.
revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    categories = sa.table(
        "categories",
        sa.column("id", sa.Integer),
        sa.column("key", sa.String),
        sa.column("name", sa.String),
        sa.column("points_total", sa.Integer),
        sa.column("scored", sa.Boolean),
        sa.column("parent_group", sa.String),
        sa.column("sort_order", sa.Integer),
    )

    op.bulk_insert(categories, CATEGORY_ROWS)

    vectors = sa.table(
        "vectors",
        sa.column("id", sa.Integer),
        sa.column("category_id", sa.Integer),
        sa.column("key", sa.String),
        sa.column("name", sa.String),
        sa.column("data_source", sa.String),
        sa.column("collection_method", sa.String),
        sa.column("points_budget", sa.Integer),
        sa.column("sort_order", sa.Integer),
    )

    op.bulk_insert(vectors, VECTOR_ROWS)


def downgrade() -> None:
    op.execute("TRUNCATE TABLE vectors CASCADE")
    op.execute("TRUNCATE TABLE categories CASCADE")
