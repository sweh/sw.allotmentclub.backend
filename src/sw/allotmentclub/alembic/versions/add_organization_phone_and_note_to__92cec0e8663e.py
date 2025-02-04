"""Add organization, phone and note to members/externalrecipients

Revision ID: 92cec0e8663e
Revises: e2cfe9da21cf
Create Date: 2020-10-22 08:11:26.996989

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "92cec0e8663e"
down_revision = "e2cfe9da21cf"


def upgrade():
    op.add_column(
        "externalrecipient",
        sa.Column("organization", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "externalrecipient",
        sa.Column("phone", sa.String(length=50), nullable=True),
    )
    op.add_column("member", sa.Column("note", sa.Text(), nullable=True))
    op.add_column(
        "member",
        sa.Column("organization", sa.String(length=100), nullable=True),
    )


def downgrade():
    op.drop_column("member", "organization")
    op.drop_column("member", "note")
    op.drop_column("externalrecipient", "phone")
    op.drop_column("externalrecipient", "organization")
