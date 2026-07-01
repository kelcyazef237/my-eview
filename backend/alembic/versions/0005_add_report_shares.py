"""Add report_shares table for short shareable report links."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = "e5f6a7b8c9d0"
down_revision = "d4e5f6a7b8c9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Idempotent: a prior partial run may have already created report_shares
    # (and the unique index). Detect that and skip those steps so the migration
    # can complete and stamp alembic_version.
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "report_shares" not in existing_tables:
        op.create_table(
            "report_shares",
            sa.Column("id", UUID(as_uuid=True), primary_key=True),
            sa.Column("code", sa.String(16), nullable=False, unique=True),
            sa.Column("scan_run_id", UUID(as_uuid=True), sa.ForeignKey("scan_runs.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("org_id", UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("revoked", sa.Boolean, nullable=False, server_default=sa.false()),
        )

    existing_indexes = {idx["name"] for idx in inspector.get_indexes("report_shares")}
    if "ix_report_shares_code" not in existing_indexes:
        op.create_index("ix_report_shares_code", "report_shares", ["code"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_report_shares_code", table_name="report_shares")
    op.drop_table("report_shares")