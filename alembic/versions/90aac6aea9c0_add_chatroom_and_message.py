"""Add Chatroom and message

Revision ID: 90aac6aea9c0
Revises:
Create Date: 2025-02-10 11:04:32.793376

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "90aac6aea9c0"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "chatroom",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("thread_id", sa.String(255), nullable=False),
        sa.Column("user_id", sa.String(255), nullable=False),
    )
    op.create_table(
        "message",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "chatroom_id", sa.Integer, sa.ForeignKey("chatroom.id"), nullable=False
        ),
        sa.Column("user_id", sa.String(255), nullable=False),
        sa.Column("role", sa.String(255), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
    )


def downgrade() -> None:
    pass
