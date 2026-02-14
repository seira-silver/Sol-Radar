"""initial_schema

Revision ID: f1f8bd8c64bf
Revises:
Create Date: 2026-02-13 13:57:26.031850
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "f1f8bd8c64bf"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- data_sources ---
    op.create_table(
        "data_sources",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("url", sa.String(1024), nullable=False),
        sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("source_category", sa.String(100), nullable=False, server_default="general"),
        sa.Column("priority", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("scrape_frequency", sa.String(50), nullable=False, server_default="daily"),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("last_scraped_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("url"),
    )

    # --- scraped_content ---
    op.create_table(
        "scraped_content",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("data_source_id", sa.Integer(), nullable=False),
        sa.Column("source_url", sa.String(2048), nullable=False),
        sa.Column("title", sa.String(512), nullable=True),
        sa.Column("raw_content", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("scraped_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("is_analyzed", sa.Boolean(), server_default=sa.text("false")),
        sa.ForeignKeyConstraint(["data_source_id"], ["data_sources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_scraped_content_hash", "scraped_content", ["content_hash"])
    op.create_index(
        "ix_scraped_content_hash_source",
        "scraped_content",
        ["content_hash", "data_source_id"],
    )

    # --- signals ---
    op.create_table(
        "signals",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("scraped_content_id", sa.Integer(), nullable=False),
        sa.Column("signal_title", sa.String(512), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("signal_type", sa.String(50), nullable=False),
        sa.Column("novelty", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("evidence", sa.Text(), nullable=False),
        sa.Column("related_projects", postgresql.JSONB(), server_default="[]"),
        sa.Column("tags", postgresql.JSONB(), server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["scraped_content_id"], ["scraped_content.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # --- narratives ---
    op.create_table(
        "narratives",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("confidence", sa.String(20), nullable=False),
        sa.Column("confidence_reasoning", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("velocity_score", sa.Float(), server_default="0.0"),
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column("tags", postgresql.JSONB(), server_default="[]"),
        sa.Column("key_evidence", postgresql.JSONB(), server_default="[]"),
        sa.Column("supporting_source_names", postgresql.JSONB(), server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("last_detected_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_narratives_is_active", "narratives", ["is_active"])

    # --- ideas ---
    op.create_table(
        "ideas",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("narrative_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("problem", sa.Text(), nullable=False),
        sa.Column("solution", sa.Text(), nullable=False),
        sa.Column("why_solana", sa.Text(), nullable=False),
        sa.Column("scale_potential", sa.Text(), nullable=False),
        sa.Column("market_signals", sa.Text(), nullable=True),
        sa.Column("supporting_signals", postgresql.JSONB(), server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["narrative_id"], ["narratives.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # --- narrative_sources ---
    op.create_table(
        "narrative_sources",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("narrative_id", sa.Integer(), nullable=False),
        sa.Column("data_source_id", sa.Integer(), nullable=False),
        sa.Column("signal_count", sa.Integer(), server_default="0"),
        sa.ForeignKeyConstraint(["narrative_id"], ["narratives.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["data_source_id"], ["data_sources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("narrative_sources")
    op.drop_table("ideas")
    op.drop_index("ix_narratives_is_active", table_name="narratives")
    op.drop_table("narratives")
    op.drop_table("signals")
    op.drop_index("ix_scraped_content_hash_source", table_name="scraped_content")
    op.drop_index("ix_scraped_content_hash", table_name="scraped_content")
    op.drop_table("scraped_content")
    op.drop_table("data_sources")
