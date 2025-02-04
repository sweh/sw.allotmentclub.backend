"""Add position and signature to users.

Revision ID: 2fd64f1e524c
Revises: 24b5e5215f2d
Create Date: 2015-01-04 15:20:53.561304

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "2fd64f1e524c"
down_revision = "24b5e5215f2d"


def upgrade():
    op.add_column(
        "user", sa.Column("position", sa.String(length=50), nullable=True)
    )
    op.add_column(
        "user",
        sa.Column("signature", sa.LargeBinary(length=10485760), nullable=True),
    )
    op.execute("""UPDATE public.user SET
                  position = 'Schatzmeister',
                  anrede = 'Frau',
                  vorname = 'Susann',
                  nachname = 'Tillack',
                  ort = 'Berlin'
                  WHERE username = 'st';""")
    op.execute("""UPDATE public.user SET
                  position = 'Vorsitzender',
                  anrede = 'Herr',
                  vorname = 'Gerd',
                  nachname = 'Mittag',
                  ort = 'Bad Dürrenberg'
                  WHERE username = 'gm';""")
    op.execute("""UPDATE public.user SET
                  position = 'Stellvertreter',
                  anrede = 'Frau',
                  vorname = 'Annette',
                  nachname = 'Rösler',
                  ort = 'Bad Dürrenberg'
                  WHERE username = 'ar';""")
    op.execute("""UPDATE public.user SET
                  position = 'Schriftführer',
                  anrede = 'Herr',
                  vorname = 'Sebastian',
                  nachname = 'Wehrmann',
                  ort = 'Halle (Saale)'
                  WHERE username = 'sw';""")


def downgrade():
    op.drop_column("user", "signature")
    op.drop_column("user", "position")
