"""Add analysis_status tracking columns and unique constraint.

Replaces the boolean is_analyzed with a proper state machine:
  pending → processing → completed / failed / skipped

Also adds a unique constraint on (content_hash, data_source_id)
to prevent duplicate content at the DB level.

Revision ID: a3b7c9d1e2f4
Revises: 21c70614fa52
Create Date: 2026-02-14
"""
from alembic import op
import sqlalchemy as sa

revision = "a3b7c9d1e2f4"
down_revision = "21c70614fa52"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns
    op.add_column(
        "scraped_content",
        sa.Column("analysis_status", sa.String(20), nullable=False, server_default="pending"),
    )
    op.add_column(
        "scraped_content",
        sa.Column("analysis_attempts", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "scraped_content",
        sa.Column("analyzed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "scraped_content",
        sa.Column("analysis_error", sa.Text(), nullable=True),
    )

    # Migrate existing data: is_analyzed=True → 'completed', False → 'pending'
    op.execute(
        "UPDATE scraped_content SET analysis_status = 'completed' WHERE is_analyzed = true"
    )
    op.execute(
        "UPDATE scraped_content SET analysis_status = 'pending' WHERE is_analyzed = false"
    )

    # Drop old column
    op.drop_column("scraped_content", "is_analyzed")

    # Add index on analysis_status for fast lookups
    op.create_index(
        "ix_scraped_content_analysis_status",
        "scraped_content",
        ["analysis_status"],
    )

    # Add unique constraint to prevent duplicate content per source
    # First drop the existing non-unique index if it exists, then create unique constraint
    op.create_unique_constraint(
        "uq_content_hash_source",
        "scraped_content",
        ["content_hash", "data_source_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_content_hash_source", "scraped_content", type_="unique")
    op.drop_index("ix_scraped_content_analysis_status", table_name="scraped_content")
    op.add_column(
        "scraped_content",
        sa.Column("is_analyzed", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.execute(
        "UPDATE scraped_content SET is_analyzed = true WHERE analysis_status IN ('completed', 'skipped')"
    )
    op.drop_column("scraped_content", "analysis_error")
    op.drop_column("scraped_content", "analyzed_at")
    op.drop_column("scraped_content", "analysis_attempts")
    op.drop_column("scraped_content", "analysis_status")
