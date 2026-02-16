"""init

Revision ID: b711b0e90a2d
Revises: 
Create Date: 2026-02-08 11:37:13.135046

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b711b0e90a2d'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "contact_messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("phone", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("topic", sa.String(length=50), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),

        sa.Column("preferred_contact", sa.String(length=20), nullable=False, server_default="viber"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("(CURRENT_TIMESTAMP)")),

        sa.Column("status", sa.String(length=20), nullable=False, server_default="new"),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.text("0")),

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("author_name", sa.String(length=80), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),

        sa.Column("rating", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("sentiment", sa.String(length=20), nullable=True),

        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("is_featured", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("(CURRENT_TIMESTAMP)")),

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "service_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("duration_min", sa.Integer(), nullable=True),
        sa.Column("price_uah", sa.Integer(), nullable=True),

        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("(CURRENT_TIMESTAMP)")),

        sa.PrimaryKeyConstraint("id"),
    )

    with op.batch_alter_table("service_items", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_service_items_type"), ["type"], unique=False)
