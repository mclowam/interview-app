"""turn_number not null unique

Revision ID: c3a1b8d4e6f0
Revises: 61160fe68ae6
Create Date: 2026-08-25 19:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c3a1b8d4e6f0"
down_revision: Union[str, Sequence[str], None] = "61160fe68ae6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE turns AS t
        SET turn_number = sub.rn
        FROM (
            SELECT id,
                   ROW_NUMBER() OVER (
                       PARTITION BY interview_id
                       ORDER BY created_at, id
                   ) AS rn
            FROM turns
        ) AS sub
        WHERE t.id = sub.id
        """
    )
    op.alter_column(
        "turns",
        "turn_number",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.create_unique_constraint(
        "uq_turns_interview_id_turn_number",
        "turns",
        ["interview_id", "turn_number"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_turns_interview_id_turn_number",
        "turns",
        type_="unique",
    )
    op.alter_column(
        "turns",
        "turn_number",
        existing_type=sa.Integer(),
        nullable=True,
    )
