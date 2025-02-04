"""Add comment and estimate value to electic meter

Revision ID: 7136a99f680d
Revises: 95c83e9e7d18
Create Date: 2016-06-26 15:08:42.149634

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "7136a99f680d"
down_revision = "95c83e9e7d18"


def upgrade():
    op.add_column(
        "electricmeter", sa.Column("comment", sa.String(), nullable=True)
    )
    op.add_column(
        "energyvalue",
        sa.Column(
            "estimated_value",
            sa.Boolean(),
            nullable=True,
            server_default="false",
        ),
    )
    op.execute("""UPDATE electricmeter SET comment = 'Wasserpumpe' WHERE id
               in (40, 49, 62, 67, 89)""")
    op.execute("UPDATE electricmeter SET comment = 'Satanlage' WHERE id = 17")
    op.execute("""UPDATE electricmeter SET number = '424690' WHERE id = 62""")
    op.execute("UPDATE electricmeter SET number = '31458149' WHERE id = 61")
    for id in (
        11,
        12,
        13,
        19,
        22,
        23,
        28,
        35,
        114,
        115,
        54,
        57,
        60,
        63,
        66,
        72,
    ):
        op.execute(
            """UPDATE energyvalue SET estimated_value = true WHERE
                   electric_meter_id = %s and year = 2015"""
            % id
        )


def downgrade():
    op.drop_column("energyvalue", "estimated_value")
    op.drop_column("electricmeter", "comment")
