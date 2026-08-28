"""turn text columns

Revision ID: d4b2c9e5f701
Revises: c3a1b8d4e6f0
Create Date: 2026-08-25 19:10:30.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d4b2c9e5f701"
down_revision: Union[str, Sequence[str], None] = "c3a1b8d4e6f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "turns",
        "question",
        existing_type=sa.String(length=500),
        type_=sa.Text(),
        existing_nullable=False,
    )
    op.alter_column(
        "turns",
        "answer",
        existing_type=sa.String(length=500),
        type_=sa.Text(),
        existing_nullable=True,
    )
    op.alter_column(
        "turns",
        "feedback",
        existing_type=sa.String(length=500),
        type_=sa.Text(),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "turns",
        "feedback",
        existing_type=sa.Text(),
        type_=sa.String(length=500),
        existing_nullable=True,
    )
    op.alter_column(
        "turns",
        "answer",
        existing_type=sa.Text(),
        type_=sa.String(length=500),
        existing_nullable=True,
    )
    op.alter_column(
        "turns",
        "question",
        existing_type=sa.Text(),
        type_=sa.String(length=500),
        existing_nullable=False,
    )
