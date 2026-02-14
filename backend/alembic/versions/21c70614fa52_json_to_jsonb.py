"""json_to_jsonb

Revision ID: 21c70614fa52
Revises: f1f8bd8c64bf
Create Date: 2026-02-13
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "21c70614fa52"
down_revision: Union[str, None] = "f1f8bd8c64bf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # signals table
    op.alter_column(
        "signals", "related_projects",
        type_=postgresql.JSONB(),
        existing_type=sa.JSON(),
        postgresql_using="related_projects::jsonb",
    )
    op.alter_column(
        "signals", "tags",
        type_=postgresql.JSONB(),
        existing_type=sa.JSON(),
        postgresql_using="tags::jsonb",
    )

    # narratives table
    op.alter_column(
        "narratives", "tags",
        type_=postgresql.JSONB(),
        existing_type=sa.JSON(),
        postgresql_using="tags::jsonb",
    )
    op.alter_column(
        "narratives", "key_evidence",
        type_=postgresql.JSONB(),
        existing_type=sa.JSON(),
        postgresql_using="key_evidence::jsonb",
    )
    op.alter_column(
        "narratives", "supporting_source_names",
        type_=postgresql.JSONB(),
        existing_type=sa.JSON(),
        postgresql_using="supporting_source_names::jsonb",
    )

    # ideas table
    op.alter_column(
        "ideas", "supporting_signals",
        type_=postgresql.JSONB(),
        existing_type=sa.JSON(),
        postgresql_using="supporting_signals::jsonb",
    )


def downgrade() -> None:
    op.alter_column("ideas", "supporting_signals", type_=sa.JSON(), existing_type=postgresql.JSONB())
    op.alter_column("narratives", "supporting_source_names", type_=sa.JSON(), existing_type=postgresql.JSONB())
    op.alter_column("narratives", "key_evidence", type_=sa.JSON(), existing_type=postgresql.JSONB())
    op.alter_column("narratives", "tags", type_=sa.JSON(), existing_type=postgresql.JSONB())
    op.alter_column("signals", "tags", type_=sa.JSON(), existing_type=postgresql.JSONB())
    op.alter_column("signals", "related_projects", type_=sa.JSON(), existing_type=postgresql.JSONB())
