"""Change back backref to backpopulates and change names backpopuation

Revision ID: 158a52fbe4a7
Revises: 83f918ec405e
Create Date: 2024-06-09 22:37:07.850069

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '158a52fbe4a7'
down_revision: Union[str, None] = '83f918ec405e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###