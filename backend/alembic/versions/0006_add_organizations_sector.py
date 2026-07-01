"""Add sector column to organizations.

The Organization SQLAlchemy model declared `sector` but no migration ever
created the column. Local databases created before the model change are
missing it, which causes any SELECT against the table to fail. Fresh
databases (post-change) get the column from 0001's `create_all` snapshot.

This migration is idempotent: it adds the column only if it is missing,
so it is safe to run on both states.
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f6a7b8c9d0e1"
down_revision = "e5f6a7b8c9d0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {c["name"] for c in inspector.get_columns("organizations")}
    if "sector" not in columns:
        op.add_column("organizations", sa.Column("sector", sa.String(128), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {c["name"] for c in inspector.get_columns("organizations")}
    if "sector" in columns:
        op.drop_column("organizations", "sector")
