"""Add formbrief depot.

Revision ID: 2535014c8ab8
Revises: 5154afa1d7d6
Create Date: 2015-01-03 14:38:20.323173

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "2535014c8ab8"
down_revision = "5154afa1d7d6"


def upgrade():
    op.create_table(
        "formletter",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "kind",
            sa.Enum(
                "Standard",
                "Abrechnung Energie",
                "Abschl\xe4ge Energie",
                "Einladung Mitgliederversammlung",
                name="form_letter_kind",
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "In Bearbeitung",
                "Fehler",
                "Fertig gestellt",
                name="form_letter_status",
            ),
            nullable=False,
        ),
        sa.Column("mimetype", sa.String(length=30), nullable=True),
        sa.Column("size", sa.String(length=20), nullable=True),
        sa.Column("data", sa.LargeBinary(length=10485760), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("formletter")
