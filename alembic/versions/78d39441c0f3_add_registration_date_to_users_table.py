"""Add registration_date to users table

Revision ID: 78d39441c0f3
Revises: 0b7fd0ac237e
Create Date: 2024-06-26 16:50:39.571134

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '78d39441c0f3'
down_revision: Union[str, None] = '0b7fd0ac237e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('registr_date', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('reg_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_column('users', 'registr_date')
    # ### end Alembic commands ###
