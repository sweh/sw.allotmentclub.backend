"""Add deleted flag to external recipients

Revision ID: 7e15fdd9747a
Revises: 2952c5487114
Create Date: 2021-01-11 07:01:46.325174

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "7e15fdd9747a"
down_revision = "2952c5487114"


def upgrade():
    op.add_column(
        "externalrecipient", sa.Column("deleted", sa.Boolean(), nullable=True)
    )


def downgrade():
    op.drop_column("externalrecipient", "deleted")
