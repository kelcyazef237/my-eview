"""Add username, full_name, registration_status to users; make email nullable; add partial unique index on lower(username).

Supports the registration + admin-approval workflow and login-by-username.
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c3d4e5f6a7b8"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("username", sa.String(64), nullable=True))
    op.add_column("users", sa.Column("full_name", sa.String(255), nullable=True))
    op.add_column(
        "users",
        sa.Column("registration_status", sa.String(32), nullable=False, server_default="active"),
    )
    op.alter_column("users", "email", existing_type=sa.String(255), nullable=True)
    op.create_index(
        "ix_users_username_lower",
        "users",
        [sa.text("lower(username)")],
        unique=True,
        postgresql_where=sa.text("username IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("ix_users_username_lower", table_name="users")
    op.alter_column("users", "email", existing_type=sa.String(255), nullable=False)
    op.drop_column("users", "registration_status")
    op.drop_column("users", "full_name")
    op.drop_column("users", "username")