"""Add registration_date to users table after migration

Revision ID: b2393c1ab693
Revises: 78d39441c0f3
Create Date: 2024-06-27 09:19:14.300418

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b2393c1ab693'
down_revision: Union[str, None] = '78d39441c0f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('registration_date', sa.DateTime(), nullable=True))
    op.drop_column('users', 'registr_date')
    op.drop_column('users', 'reg_date')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('reg_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('users', sa.Column('registr_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_column('users', 'registration_date')
    # ### end Alembic commands ###
