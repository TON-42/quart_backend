"""Update BIGINT last one

Revision ID: e6ffb480e843
Revises: ed2b23ed3aaa
Create Date: 2024-06-10 12:14:01.518020

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e6ffb480e843"
down_revision: Union[str, None] = "ed2b23ed3aaa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### manually added commands to alter columns ###
    op.execute("ALTER TABLE agreed_users ALTER COLUMN chat_id TYPE BIGINT;")
    op.execute("ALTER TABLE agreed_users ALTER COLUMN user_id TYPE BIGINT;")
    op.execute("ALTER TABLE agreed_users_chats ALTER COLUMN chat_id TYPE BIGINT;")
    op.execute("ALTER TABLE agreed_users_chats ALTER COLUMN user_id TYPE BIGINT;")
    op.execute("ALTER TABLE chats ALTER COLUMN id TYPE BIGINT;")
    op.execute("ALTER TABLE chats ALTER COLUMN lead_id TYPE BIGINT;")
    op.execute("ALTER TABLE chats ALTER COLUMN words TYPE BIGINT;")
    op.execute("ALTER TABLE users ALTER COLUMN id TYPE BIGINT;")
    op.execute("ALTER TABLE users ALTER COLUMN words TYPE BIGINT;")
    op.execute("ALTER TABLE users_chats ALTER COLUMN chat_id TYPE BIGINT;")
    op.execute("ALTER TABLE users_chats ALTER COLUMN user_id TYPE BIGINT;")
    # ### end manually added commands ###


def downgrade() -> None:
    # ### manually added commands to revert changes ###
    op.execute("ALTER TABLE agreed_users ALTER COLUMN chat_id TYPE INTEGER;")
    op.execute("ALTER TABLE agreed_users ALTER COLUMN user_id TYPE INTEGER;")
    op.execute("ALTER TABLE agreed_users_chats ALTER COLUMN chat_id TYPE INTEGER;")
    op.execute("ALTER TABLE agreed_users_chats ALTER COLUMN user_id TYPE INTEGER;")
    op.execute("ALTER TABLE chats ALTER COLUMN id TYPE INTEGER;")
    op.execute("ALTER TABLE chats ALTER COLUMN lead_id TYPE INTEGER;")
    op.execute("ALTER TABLE chats ALTER COLUMN words TYPE INTEGER;")
    op.execute("ALTER TABLE users ALTER COLUMN id TYPE INTEGER;")
    op.execute("ALTER TABLE users ALTER COLUMN words TYPE INTEGER;")
    op.execute("ALTER TABLE users_chats ALTER COLUMN chat_id TYPE INTEGER;")
    op.execute("ALTER TABLE users_chats ALTER COLUMN user_id TYPE INTEGER;")
    # ### end manually added commands ###
