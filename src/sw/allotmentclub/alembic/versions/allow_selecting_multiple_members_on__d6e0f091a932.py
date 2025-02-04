"""Allow selecting multiple members on messages.

Revision ID: d6e0f091a932
Revises: 5b929a47d6ae
Create Date: 2016-04-21 08:49:21.445319

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d6e0f091a932"
down_revision = "5b929a47d6ae"


def upgrade():
    op.create_table(
        "members_messages",
        sa.Column("member_id", sa.Integer(), nullable=True),
        sa.Column("message_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["member_id"],
            ["member.id"],
        ),
        sa.ForeignKeyConstraint(
            ["message_id"],
            ["message.id"],
        ),
    )
    op.execute(
        """INSERT into members_messages (message_id, member_id)
             (SELECT id, member_id FROM message WHERE member_id is not null);
        """
    )
    op.drop_constraint("message_member_id_fkey", "message", type_="foreignkey")
    op.drop_column("message", "member_id")


def downgrade():
    op.add_column(
        "message",
        sa.Column(
            "member_id", sa.INTEGER(), autoincrement=False, nullable=True
        ),
    )
    op.create_foreign_key(
        "message_member_id_fkey", "message", "member", ["member_id"], ["id"]
    )
    op.execute("""UPDATE message SET member_id = (
                      SELECT member_id FROM members_messages
                          WHERE message_id = message.id);""")
    op.drop_table("members_messages")
