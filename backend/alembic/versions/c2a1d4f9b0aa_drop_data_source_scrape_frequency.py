"""Drop unused data_sources.scrape_frequency column.

Revision ID: c2a1d4f9b0aa
Revises: b7f2d8c4e1a1
Create Date: 2026-02-15
"""

from alembic import op
import sqlalchemy as sa

revision = "c2a1d4f9b0aa"
down_revision = "b7f2d8c4e1a1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Column is informational only and unused by scheduler/logic.
    with op.batch_alter_table("data_sources") as batch:
        batch.drop_column("scrape_frequency")


def downgrade() -> None:
    with op.batch_alter_table("data_sources") as batch:
        batch.add_column(
            sa.Column("scrape_frequency", sa.String(50), nullable=False, server_default="daily")
        )

