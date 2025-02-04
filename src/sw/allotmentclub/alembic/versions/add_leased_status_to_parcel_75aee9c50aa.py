"""Add leased status to parcel.

Revision ID: 75aee9c50aa
Revises: 1654373c7899
Create Date: 2015-03-29 17:48:45.181684

"""

# revision identifiers, used by Alembic.
import sqlalchemy as sa
from alembic import op

revision = "75aee9c50aa"
down_revision = "1654373c7899"


def upgrade():
    op.add_column(
        "parcel",
        sa.Column(
            "leased", sa.Boolean(), nullable=False, server_default="False"
        ),
    )
    op.execute(
        """UPDATE parcel SET leased = true WHERE number in
           (70, 74, 109, 148, 111, 89, 160, 135, 136, 84, 103, 133, 138,
            165, 100, 99, 121, 122);"""
    )


def downgrade():
    op.drop_column("parcel", "leased")
