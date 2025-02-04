"""Add reference to booking to SEPASammler.

Revision ID: 4d63c477b58f
Revises: 388a201feabf
Create Date: 2015-04-07 10:44:29.267471

"""

# revision identifiers, used by Alembic.
import sqlalchemy as sa
from alembic import op

revision = "4d63c477b58f"
down_revision = "388a201feabf"


def upgrade():
    op.add_column(
        "sepasammler", sa.Column("booking_day", sa.Date(), nullable=True)
    )
    op.add_column(
        "sepasammler",
        sa.Column("accounting_year", sa.Integer(), nullable=True),
    )
    op.execute("""DELETE FROM booking WHERE purpose like 'Lastschrift%';""")
    op.execute("""UPDATE sepasammler SET
                  accounting_year = 2015, booking_day = '2015-03-31';""")


def downgrade():
    op.drop_column("sepasammler", "splitted_from_id")
