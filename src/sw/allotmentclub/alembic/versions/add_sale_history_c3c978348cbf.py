"""Add sale history

Revision ID: c3c978348cbf
Revises: cc8ba97635c1
Create Date: 2016-02-03 21:14:16.233171

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c3c978348cbf"
down_revision = "cc8ba97635c1"


def upgrade():
    op.create_table(
        "salehistory",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("seller_id", sa.Integer(), nullable=False),
        sa.Column("buyer_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("salehistory")
