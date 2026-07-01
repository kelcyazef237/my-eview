"""Add zone_transfer vector (id=28) to domain_governance; redistribute points.

domain_age 30->15, domain_expiration 35->30, dnssec_adoption 25->20, zone_transfer 25 (new).
Category total stays 90. Total scored stays 1000.
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d4e5f6a7b8c9"
down_revision = "c3d4e5f6a7b8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Redistribute existing vector budgets
    op.execute("UPDATE vectors SET points_budget = 15 WHERE key = 'domain_age'")
    op.execute("UPDATE vectors SET points_budget = 30 WHERE key = 'domain_expiration'")
    op.execute("UPDATE vectors SET points_budget = 20 WHERE key = 'dnssec_adoption'")

    # Insert new zone_transfer vector, but only if it isn't already present.
    # `app.reference_data.VECTOR_ROWS` was updated to include id=28, so on
    # fresh databases migration 0002 already seeds it; on existing databases
    # 0002 doesn't run (it was already applied) and 0004 needs to add it.
    # Either way, we must not violate vectors_pkey if a prior partial run
    # left the row behind.
    bind = op.get_bind()
    exists = bind.execute(
        sa.text("SELECT 1 FROM vectors WHERE id = 28")
    ).first()
    if exists is None:
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
        op.bulk_insert(vectors, [
            {
                "id": 28,
                "category_id": 2,
                "key": "zone_transfer",
                "name": "Zone Transfer (AXFR) Exposure",
                "data_source": "DNS AXFR",
                "collection_method": "dnspython",
                "points_budget": 25,
                "sort_order": 4,
            },
        ])


def downgrade() -> None:
    op.execute("DELETE FROM vectors WHERE key = 'zone_transfer'")
    op.execute("UPDATE vectors SET points_budget = 25 WHERE key = 'dnssec_adoption'")
    op.execute("UPDATE vectors SET points_budget = 35 WHERE key = 'domain_expiration'")
    op.execute("UPDATE vectors SET points_budget = 30 WHERE key = 'domain_age'")