"""re #2: Add change of ElectricMeter 14996103.

Revision ID: 444966e3e7d6
Revises: 56e61da4fed1
Create Date: 2014-12-21 17:10:21.186765

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "444966e3e7d6"
down_revision = "56e61da4fed1"


def upgrade():
    op.add_column(
        "energyvalue", sa.Column("member_id", sa.Integer(), nullable=True)
    )


def downgrade():
    op.drop_column("energyvalue", "member_id")
