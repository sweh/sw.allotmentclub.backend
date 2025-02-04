"""Add new groups

Revision ID: 4ac1a4b79213
Revises: 1850226c55dc
Create Date: 2014-12-16 20:58:41.652962

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4ac1a4b79213"
down_revision = "1850226c55dc"


def upgrade():
    op.add_column(
        "user",
        sa.Column(
            "can_modify", sa.Boolean(), server_default="false", nullable=False
        ),
    )
    op.add_column(
        "user",
        sa.Column(
            "read_only", sa.Boolean(), server_default="false", nullable=False
        ),
    )
    op.drop_column("user", "may_grant")


def downgrade():
    op.add_column(
        "user",
        sa.Column(
            "may_grant", sa.BOOLEAN(), server_default="false", nullable=False
        ),
    )
    op.drop_column("user", "read_only")
    op.drop_column("user", "can_modify")
