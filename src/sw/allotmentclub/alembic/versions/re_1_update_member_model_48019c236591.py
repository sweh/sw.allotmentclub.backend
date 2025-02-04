"""re #1: Update Member model.

Revision ID: 48019c236591
Revises: 46276fff5bc2
Create Date: 2014-12-02 19:03:49.975576

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "48019c236591"
down_revision = "46276fff5bc2"


def upgrade():
    op.create_table(
        "allotment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("member_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["member_id"],
            ["member.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "parcel",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("allotment_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["allotment_id"],
            ["allotment.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column(
        "member", sa.Column("appellation", sa.String(length=20), nullable=True)
    )
    op.add_column(
        "member", sa.Column("city", sa.String(length=50), nullable=True)
    )
    op.add_column(
        "member", sa.Column("country", sa.String(length=50), nullable=True)
    )
    op.add_column(
        "member", sa.Column("firstname", sa.String(length=50), nullable=True)
    )
    op.add_column(
        "member", sa.Column("lastname", sa.String(length=50), nullable=True)
    )
    op.add_column(
        "member", sa.Column("mobile", sa.String(length=50), nullable=True)
    )
    op.add_column(
        "member", sa.Column("phone", sa.String(length=50), nullable=True)
    )
    op.add_column(
        "member", sa.Column("street", sa.String(length=100), nullable=True)
    )
    op.add_column(
        "member", sa.Column("title", sa.String(length=20), nullable=True)
    )
    op.add_column(
        "member", sa.Column("zip", sa.String(length=6), nullable=True)
    )
    op.drop_column("member", "ort")
    op.drop_column("member", "zaehlernummer")
    op.drop_column("member", "plz")
    op.drop_column("member", "anrede")
    op.drop_column("member", "nachname")
    op.drop_column("member", "haus_nr")
    op.drop_column("member", "strasse")
    op.drop_column("member", "vorname")


def downgrade():
    op.add_column(
        "member", sa.Column("vorname", sa.VARCHAR(length=50), nullable=True)
    )
    op.add_column(
        "member", sa.Column("strasse", sa.VARCHAR(length=100), nullable=True)
    )
    op.add_column(
        "member", sa.Column("haus_nr", sa.VARCHAR(length=7), nullable=True)
    )
    op.add_column(
        "member", sa.Column("nachname", sa.VARCHAR(length=50), nullable=True)
    )
    op.add_column(
        "member", sa.Column("anrede", sa.VARCHAR(length=20), nullable=True)
    )
    op.add_column(
        "member", sa.Column("plz", sa.VARCHAR(length=6), nullable=True)
    )
    op.add_column(
        "member",
        sa.Column("zaehlernummer", sa.VARCHAR(length=50), nullable=True),
    )
    op.add_column(
        "member", sa.Column("ort", sa.VARCHAR(length=50), nullable=True)
    )
    op.drop_column("member", "zip")
    op.drop_column("member", "title")
    op.drop_column("member", "street")
    op.drop_column("member", "phone")
    op.drop_column("member", "mobile")
    op.drop_column("member", "lastname")
    op.drop_column("member", "firstname")
    op.drop_column("member", "country")
    op.drop_column("member", "city")
    op.drop_column("member", "appellation")
    op.drop_table("parcel")
    op.drop_table("allotment")
