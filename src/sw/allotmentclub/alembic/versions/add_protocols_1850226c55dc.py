"""Add protocols

Revision ID: 1850226c55dc
Revises: 48019c236591
Create Date: 2014-12-08 18:52:13.291970

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1850226c55dc"
down_revision = "48019c236591"


def upgrade():
    op.create_table(
        "protocol",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=254), nullable=True),
        sa.Column("location", sa.String(length=254), nullable=True),
        sa.Column("attendees", sa.String(length=254), nullable=True),
        sa.Column("day", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("protocol")
