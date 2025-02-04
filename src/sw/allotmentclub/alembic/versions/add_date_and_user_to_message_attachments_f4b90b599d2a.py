"""Add date and user to message attachments

Revision ID: f4b90b599d2a
Revises: 5baeb56d1864
Create Date: 2019-01-30 11:38:21.775451

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f4b90b599d2a"
down_revision = "5baeb56d1864"


def upgrade():
    op.add_column(
        "attachment",
        sa.Column(
            "date",
            sa.DateTime(),
            nullable=True,
            server_default=sa.text("now()"),
        ),
    )
    op.add_column(
        "attachment", sa.Column("user_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        "attachment_user_fkey", "attachment", "user", ["user_id"], ["id"]
    )
    op.execute("UPDATE attachment SET date = null;")


def downgrade():
    op.drop_constraint(
        "attachment_user_fkey", "attachment", type_="foreignkey"
    )
    op.drop_column("attachment", "user_id")
    op.drop_column("attachment", "date")
