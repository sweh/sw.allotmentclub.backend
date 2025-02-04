"""Some missing changes to database.

Revision ID: 88942e83a048
Revises: b01e97903b78
Create Date: 2017-05-23 16:16:28.941009

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "88942e83a048"
down_revision = "b01e97903b78"


def upgrade():
    op.drop_column("energyprice", "advance_pay")
    op.drop_column("energyprice", "charge")


def downgrade():
    op.add_column(
        "energyprice",
        sa.Column("charge", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "energyprice",
        sa.Column(
            "advance_pay", sa.INTEGER(), autoincrement=False, nullable=True
        ),
    )
