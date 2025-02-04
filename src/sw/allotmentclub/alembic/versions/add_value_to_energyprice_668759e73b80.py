"""Add value to energyprice.

Revision ID: 668759e73b80
Revises: 46adf5114de1
Create Date: 2017-08-22 13:34:08.196691

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "668759e73b80"
down_revision = "46adf5114de1"


def upgrade():
    for column in (
        "value",
        "bill",
        "usage_hauptzaehler",
        "usage_members",
        "leakage_current",
    ):
        op.add_column(
            "energyprice", sa.Column(column, sa.Integer(), nullable=True)
        )
    op.execute("""
        UPDATE energyprice
            SET value = 1489550,
                bill = 114392300
            WHERE year = 2016""")


def downgrade():
    op.drop_column("energyprice", "value")
