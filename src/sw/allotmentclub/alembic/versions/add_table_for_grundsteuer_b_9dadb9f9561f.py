"""Add table for Grundsteuer B.

Revision ID: 9dadb9f9561f
Revises: b7de0b4c2bb6
Create Date: 2016-07-03 16:41:55.773497

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "9dadb9f9561f"
down_revision = "b7de0b4c2bb6"


def upgrade():
    op.create_table(
        "grundsteuerb",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("parcel_id", sa.Integer(), nullable=False),
        sa.Column("value", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["parcel_id"],
            ["parcel.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute(
        "INSERT into grundsteuerb (parcel_id, value) VALUES (175, 39800);"
    )
    op.execute(
        "INSERT into grundsteuerb (parcel_id, value) VALUES (172, 39800);"
    )
    op.execute(
        "INSERT into grundsteuerb (parcel_id, value) VALUES (147, 39800);"
    )
    op.execute(
        "INSERT into grundsteuerb (parcel_id, value) VALUES (128, 39800);"
    )
    op.execute(
        "INSERT into grundsteuerb (parcel_id, value) VALUES (119, 39800);"
    )
    op.execute(
        "INSERT into grundsteuerb (parcel_id, value) VALUES (86, 39800);"
    )
    op.execute(
        "INSERT into grundsteuerb (parcel_id, value) VALUES (87, 79600);"
    )
    op.execute(
        "INSERT into grundsteuerb (parcel_id, value) VALUES (85, 59700);"
    )
    op.execute(
        "INSERT into grundsteuerb (parcel_id, value) VALUES (177, 59700);"
    )


def downgrade():
    op.drop_table("grundsteuerb")
