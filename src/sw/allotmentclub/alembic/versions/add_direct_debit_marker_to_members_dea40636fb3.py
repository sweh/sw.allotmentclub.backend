"""Add direct debit marker to members.

Revision ID: dea40636fb3
Revises: 1c44d30192ea
Create Date: 2015-01-29 09:55:08.515004

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "dea40636fb3"
down_revision = "1c44d30192ea"


def upgrade():
    op.add_column(
        "member", sa.Column("direct_debit", sa.Boolean(), nullable=True)
    )
    op.execute("""UPDATE member set direct_debit = true;""")
    op.execute(
        """UPDATE member set direct_debit = false WHERE id in (
            73, 86, 87, 104, 105, 113, 118, 103, 122, 123, 132, 133, 142, 144,
            145, 147, 150, 151, 156, 163, 164, 177, 179);"""
    )


def downgrade():
    op.drop_column("member", "direct_debit")
