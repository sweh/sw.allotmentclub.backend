"""Add accounting_year to inbound messages.

Revision ID: ff18c87afd8e
Revises: 88942e83a048
Create Date: 2017-05-26 11:27:47.675422

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "ff18c87afd8e"
down_revision = "88942e83a048"


def upgrade():
    op.execute(
        """UPDATE message
           SET accounting_year = 2017
           WHERE inbound = true;"""
    )


def downgrade():
    pass
