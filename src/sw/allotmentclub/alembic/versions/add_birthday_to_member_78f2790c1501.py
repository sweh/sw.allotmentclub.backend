"""Add birthday to member.

Revision ID: 78f2790c1501
Revises: 3b50f99a2e2f
Create Date: 2017-02-07 09:42:06.154891

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "78f2790c1501"
down_revision = "3b50f99a2e2f"


def upgrade():
    op.add_column("member", sa.Column("birthday", sa.Date(), nullable=True))


def downgrade():
    op.drop_column("member", "birthday")
