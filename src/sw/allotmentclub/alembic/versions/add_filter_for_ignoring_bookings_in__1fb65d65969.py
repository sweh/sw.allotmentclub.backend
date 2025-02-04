"""Add filter for ignoring bookings in reporting.

Revision ID: 1fb65d65969
Revises: 433297b9762
Create Date: 2015-11-17 15:04:58.595746

"""

# revision identifiers, used by Alembic.
import sqlalchemy as sa
from alembic import op

revision = "1fb65d65969"
down_revision = "433297b9762"


def upgrade():
    op.add_column(
        "booking",
        sa.Column(
            "ignore_in_reporting",
            sa.Boolean(),
            server_default="False",
            nullable=False,
        ),
    )
    op.add_column(
        "sepasammler",
        sa.Column(
            "ignore_in_reporting",
            sa.Boolean(),
            server_default="False",
            nullable=False,
        ),
    )
    op.execute("""UPDATE booking SET ignore_in_reporting = True
                  WHERE id in (102, 586, 516, 598, 591, 963, 431, 1001, 998,
                  999, 1000, 1027);""")
    op.execute("""UPDATE sepasammler SET ignore_in_reporting = True
                  WHERE id in (40, 266, 322, 320, 354, 324);""")


def downgrade():
    op.drop_column("booking", "ignore_in_reporting")
    op.drop_column("sepasammler", "ignore_in_reporting")
