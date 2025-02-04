"""Add message attachment.

Revision ID: 38a169e80b6e
Revises: 4369f16d7e67
Create Date: 2015-11-16 11:38:16.714582

"""

# revision identifiers, used by Alembic.
import sqlalchemy as sa
from alembic import op

revision = "38a169e80b6e"
down_revision = "4369f16d7e67"


def upgrade():
    op.create_table(
        "attachment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("message_id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(length=100), nullable=True),
        sa.Column("mimetype", sa.String(length=30), nullable=True),
        sa.Column("size", sa.String(length=20), nullable=True),
        sa.Column("data", sa.LargeBinary(length=10485760), nullable=True),
        sa.ForeignKeyConstraint(
            ["message_id"],
            ["message.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("attachment")
