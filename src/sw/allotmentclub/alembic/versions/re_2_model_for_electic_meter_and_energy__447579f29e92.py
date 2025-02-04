"""re #2: Model for electic meter and energy value.

Revision ID: 447579f29e92
Revises: 51143cacbf85
Create Date: 2014-12-19 20:58:40.738035

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "447579f29e92"
down_revision = "51143cacbf85"


def upgrade():
    op.execute("INSERT into allotment (number, member_id) VALUES (311, 138);")
    op.execute("INSERT into allotment (number, member_id) VALUES (222, 104);")
    op.execute("INSERT into allotment (number, member_id) VALUES (249, 129);")
    op.execute("INSERT into allotment (number, member_id) VALUES (316, 175);")
    op.execute("INSERT into allotment (number, member_id) VALUES (232, 173);")
    op.execute("INSERT into allotment (number, member_id) VALUES (334, 177);")
    op.create_table(
        "electricmeter",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("allotment_id", sa.Integer(), nullable=False),
        sa.Column("number", sa.String(), nullable=True),
        sa.Column("electric_power", sa.Boolean(), nullable=True),
        sa.Column("disconnected", sa.Boolean(), nullable=True),
        sa.Column("replaced_by_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["allotment_id"],
            ["allotment.id"],
        ),
        sa.ForeignKeyConstraint(
            ["replaced_by_id"],
            ["electricmeter.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "energyvalue",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("electric_meter_id", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("value", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["electric_meter_id"], ["electricmeter.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("energyvalue")
    op.drop_table("electricmeter")
