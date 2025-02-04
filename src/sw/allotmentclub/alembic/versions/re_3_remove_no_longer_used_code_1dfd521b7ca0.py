"""re #3: Remove no longer used code.

Revision ID: 1dfd521b7ca0
Revises: d1ccee162c46
Create Date: 2016-07-26 12:45:07.547110

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1dfd521b7ca0"
down_revision = "d1ccee162c46"


def upgrade():
    op.drop_column("user", "read_only")
    op.drop_column("user", "is_revision")
    op.drop_column("user", "can_modify")


def downgrade():
    op.add_column(
        "user",
        sa.Column(
            "can_modify",
            sa.BOOLEAN(),
            server_default=sa.text("false"),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        "user",
        sa.Column(
            "is_revision",
            sa.BOOLEAN(),
            server_default=sa.text("false"),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        "user",
        sa.Column(
            "read_only",
            sa.BOOLEAN(),
            server_default=sa.text("false"),
            autoincrement=False,
            nullable=False,
        ),
    )
