"""Add new bookingkinds.

Revision ID: 126c6a200c9f
Revises: 32b7b30817d6
Create Date: 2015-11-18 13:04:39.964719

"""

from __future__ import unicode_literals

from alembic import op

# revision identifiers, used by Alembic.
revision = "126c6a200c9f"
down_revision = "32b7b30817d6"


def upgrade():
    op.execute("""INSERT into bookingkind (title, shorttitle) VALUES
                  ('Grundbesitzabgabe', 'GRUN')""")
    op.execute("""INSERT into bookingkind (title, shorttitle) VALUES
                  ('Versicherungen', 'VERS')""")
    op.execute("""INSERT into bookingkind (title, shorttitle) VALUES
                  ('Verwaltung', 'VERW')""")
    op.execute("""INSERT into bookingkind (title, shorttitle) VALUES
                  ('Aufwandsentschädigungen', 'AUFW')""")
    op.execute("""INSERT into bookingkind (title, shorttitle) VALUES
                  ('Instandhaltung', 'INST')""")
    op.execute("""INSERT into bookingkind (title, shorttitle) VALUES
                  ('Energieanbieter', 'ENAN')""")
    op.execute("""INSERT into bookingkind (title, shorttitle) VALUES
                  ('Müll', 'MÜLL')""")
    op.execute("""INSERT into bookingkind (title, shorttitle) VALUES
                  ('Vereinsfest', 'VEFE')""")
    op.execute("""INSERT into bookingkind (title, shorttitle) VALUES
                  ('Pacht', 'PACH')""")


def downgrade():
    pass
