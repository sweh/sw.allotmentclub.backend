"""Add bulletin model.

Revision ID: 4377c6148413
Revises: 3f6271158ce3
Create Date: 2015-02-24 10:29:35.004730

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4377c6148413"
down_revision = "3f6271158ce3"


def upgrade():
    op.create_table(
        "bulletin",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("subject", sa.String(), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("mimetype", sa.String(length=30), nullable=True),
        sa.Column("size", sa.String(length=20), nullable=True),
        sa.Column("data", sa.LargeBinary(length=10485760), nullable=True),
        sa.Column("date", sa.DateTime(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("bulletin")
