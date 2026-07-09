"""Add ai_result + ai_generated_at to scores for persisted AI reports."""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "b8c9d0e1f2a3"
down_revision = "a7b8c9d0e1f2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("scores", sa.Column("ai_result", sa.dialects.postgresql.JSONB(), nullable=True))
    op.add_column("scores", sa.Column("ai_generated_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("scores", "ai_generated_at")
    op.drop_column("scores", "ai_result")