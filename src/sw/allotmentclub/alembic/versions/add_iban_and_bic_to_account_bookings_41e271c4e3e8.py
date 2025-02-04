"""Add iban and bic to account bookings.

Revision ID: 41e271c4e3e8
Revises: 411ca2f55194
Create Date: 2015-03-30 18:59:16.733989

"""

# revision identifiers, used by Alembic.
import sqlalchemy as sa
from alembic import op

revision = "41e271c4e3e8"
down_revision = "411ca2f55194"


def upgrade():
    op.add_column(
        "booking", sa.Column("bic", sa.String(length=11), nullable=True)
    )
    op.add_column(
        "booking", sa.Column("iban", sa.String(length=34), nullable=True)
    )
    op.drop_column("booking", "account_number")


def downgrade():
    op.add_column(
        "booking",
        sa.Column("account_number", sa.VARCHAR(length=56), nullable=True),
    )
    op.drop_column("booking", "iban")
    op.drop_column("booking", "bic")
