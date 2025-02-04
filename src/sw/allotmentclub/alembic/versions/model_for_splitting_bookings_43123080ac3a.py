"""Model for splitting bookings.

Revision ID: 43123080ac3a
Revises: 568f7817789f
Create Date: 2015-03-11 10:12:44.584094

"""

# revision identifiers, used by Alembic.
import sqlalchemy as sa
from alembic import op

revision = "43123080ac3a"
down_revision = "568f7817789f"


def upgrade():
    op.add_column(
        "booking",
        sa.Column(
            "is_splitted", sa.Boolean(), nullable=False, server_default="False"
        ),
    )
    op.add_column(
        "booking", sa.Column("splitted_from_id", sa.Integer(), nullable=True)
    )


def downgrade():
    op.drop_column("booking", "splitted_from_id")
    op.drop_column("booking", "is_splitted")
