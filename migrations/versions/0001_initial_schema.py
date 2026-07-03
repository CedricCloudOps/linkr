"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-01-01 00:00:00.000000
"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "links",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=16), nullable=False),
        sa.Column("target_url", sa.String(length=2048), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_links_code", "links", ["code"], unique=True)

    op.create_table(
        "clicks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "link_id",
            sa.Integer(),
            sa.ForeignKey("links.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "ts",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("referrer", sa.String(length=2048), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
    )
    op.create_index("ix_clicks_link_id", "clicks", ["link_id"])
    op.create_index("ix_clicks_ts", "clicks", ["ts"])


def downgrade() -> None:
    op.drop_index("ix_clicks_ts", table_name="clicks")
    op.drop_index("ix_clicks_link_id", table_name="clicks")
    op.drop_table("clicks")
    op.drop_index("ix_links_code", table_name="links")
    op.drop_table("links")
