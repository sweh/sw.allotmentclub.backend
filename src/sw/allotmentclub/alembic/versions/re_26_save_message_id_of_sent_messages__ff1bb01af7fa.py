"""re #26: Save message id of sent messages in DB.

Revision ID: ff1bb01af7fa
Revises: 708df911eb9e
Create Date: 2016-11-22 14:40:51.080650

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "ff1bb01af7fa"
down_revision = "708df911eb9e"


def upgrade():
    op.create_table(
        "sentmessageinfo",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("message_id", sa.Integer(), nullable=False),
        sa.Column("msg_id", sa.String(length=100), nullable=True),
        sa.Column("address", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(
            ["message_id"],
            ["message.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("sentmessageinfo")
