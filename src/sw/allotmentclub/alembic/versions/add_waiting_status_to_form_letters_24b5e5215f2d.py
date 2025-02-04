"""Add waiting status to form letters.

Revision ID: 24b5e5215f2d
Revises: 179b760ddcda
Create Date: 2015-01-04 14:01:42.561563

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "24b5e5215f2d"
down_revision = "179b760ddcda"

OLD_STATUS = ("In Bearbeitung", "Fehler", "Fertig gestellt")
NEW_STATUS = ("Wartet",) + OLD_STATUS


def upgrade():
    op.drop_column("formletter", "status")
    sa.Enum(name="form_letter_status").drop(op.get_bind(), checkfirst=False)
    sa.Enum(*NEW_STATUS, name="form_letter_status").create(
        op.get_bind(), checkfirst=False
    )
    op.add_column(
        "formletter",
        sa.Column(
            "status",
            sa.Enum(*NEW_STATUS, name="form_letter_status"),
            nullable=False,
        ),
    )


def downgrade():
    op.drop_column("formletter", "status")
    sa.Enum(name="form_letter_status").drop(op.get_bind(), checkfirst=False)
    sa.Enum(*OLD_STATUS, name="form_letter_status").create(
        op.get_bind(), checkfirst=False
    )
    op.add_column(
        "formletter",
        sa.Column(
            "status",
            sa.Enum(*OLD_STATUS, name="form_letter_status"),
            nullable=False,
        ),
    )
