"""re #21: Add tap_water information

Revision ID: 708df911eb9e
Revises: f86ea5808406
Create Date: 2016-07-31 12:32:27.573230

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "708df911eb9e"
down_revision = "f86ea5808406"


def upgrade():
    op.add_column(
        "parcel",
        sa.Column(
            "tap_water", sa.Boolean(), nullable=False, server_default="False"
        ),
    )
    op.execute(
        """UPDATE parcel SET tap_water = true WHERE number in
           (SELECT p.number
            FROM parcel as p JOIN allotment al on p.allotment_id = al.id
            WHERE al.number in (
                104, 106, 108, 110, 112, 114, 120, 122, 126, 130, 138, 205,
                210, 211, 214, 217, 219, 220, 237, 239, 241, 247, 261, 307,
                311, 312, 314, 310, 401, 403, 409, 414, 417, 424, 128, 209,
                229, 235, 252, 253, 309, 315, 335, 337, 411, 415, 321, 330,
                333, 329, 320, 339));"""
    )
    op.execute(
        """INSERT into accessauthority (viewname, user_id, organization_id)
           VALUES ('member_list_leased', 4, 1)"""
    )
    op.execute(
        """INSERT into accessauthority (viewname, user_id, organization_id)
           VALUES ('member_list_leased', 2, 1)"""
    )
    op.execute(
        """INSERT into accessauthority (viewname, user_id, organization_id)
           VALUES ('member_list_tap_water', 4, 1)"""
    )
    op.execute(
        """INSERT into accessauthority (viewname, user_id, organization_id)
        VALUES ('member_list_tap_water', 2, 1)"""
    )


def downgrade():
    op.drop_column("parcel", "tap_water")
