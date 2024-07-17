"""Add chats to Session

Revision ID: 7c9d3c13e582
Revises: f14d52888288
Create Date: 2024-07-01 20:52:02.186945

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7c9d3c13e582"
down_revision: Union[str, None] = "f14d52888288"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("sessions", sa.Column("chats", sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("sessions", "chats")
    # ### end Alembic commands ###
