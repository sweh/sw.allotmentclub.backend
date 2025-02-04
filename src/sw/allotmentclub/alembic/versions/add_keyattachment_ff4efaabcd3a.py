"""add keyattachment

Revision ID: ff4efaabcd3a
Revises: 9da4a1cc4bf1
Create Date: 2024-07-05 07:41:57.044859

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "ff4efaabcd3a"
down_revision = "9da4a1cc4bf1"


def upgrade():
    op.create_table(
        "keyattachment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("key_id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(length=100), nullable=True),
        sa.Column("mimetype", sa.String(length=30), nullable=True),
        sa.Column("size", sa.String(length=20), nullable=True),
        sa.Column("data", sa.LargeBinary(length=10485760), nullable=True),
        sa.ForeignKeyConstraint(["key_id"], ["key.id"], ondelete="cascade"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("keyattachment")
