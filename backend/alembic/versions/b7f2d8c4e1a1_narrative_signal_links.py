"""Add narrative_signal_links table for traceability.

Revision ID: b7f2d8c4e1a1
Revises: a3b7c9d1e2f4
Create Date: 2026-02-15
"""

from alembic import op
import sqlalchemy as sa

revision = "b7f2d8c4e1a1"
down_revision = "a3b7c9d1e2f4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "narrative_signal_links",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("narrative_id", sa.Integer(), nullable=False),
        sa.Column("signal_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["narrative_id"], ["narratives.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["signal_id"], ["signals.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("narrative_id", "signal_id", name="uq_narrative_signal"),
    )
    op.create_index(
        "ix_narrative_signal_links_narrative_id",
        "narrative_signal_links",
        ["narrative_id"],
    )
    op.create_index(
        "ix_narrative_signal_links_signal_id",
        "narrative_signal_links",
        ["signal_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_narrative_signal_links_signal_id", table_name="narrative_signal_links")
    op.drop_index("ix_narrative_signal_links_narrative_id", table_name="narrative_signal_links")
    op.drop_table("narrative_signal_links")

