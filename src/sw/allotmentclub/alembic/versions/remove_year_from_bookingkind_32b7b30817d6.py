# encoding=utf8
"""Remove year from BookingKind.

Revision ID: 32b7b30817d6
Revises: 1fb65d65969
Create Date: 2015-11-18 07:30:07.933913

"""

# revision identifiers, used by Alembic.
from __future__ import unicode_literals
from alembic import op
import sqlalchemy as sa

revision = '32b7b30817d6'
down_revision = '1fb65d65969'


def upgrade():
    op.execute("""DELETE FROM bookingkind WHERE year = 2016;""")
    op.add_column(
        'bookingkind',
        sa.Column('shorttitle', sa.String(length=10), nullable=True))
    op.alter_column('bookingkind', 'title', type_=sa.String(length=50))
    op.drop_column('bookingkind', 'year')
    op.drop_column('bookingkind', 'value_per_member')
    op.execute("""UPDATE bookingkind SET shorttitle = 'NGA'
                  WHERE title = 'Fehl.Arb.Std';""")
    op.execute("""UPDATE bookingkind SET title = 'Nicht geleistete
      Arbeitsstunden' WHERE shorttitle = 'NGA';""")
    op.execute("""UPDATE bookingkind SET shorttitle = 'MGB'
                  WHERE title = 'Mitgliedsbeitrag';""")
    op.execute("""UPDATE bookingkind SET shorttitle = 'EA1'
                  WHERE title = 'Energieabschlag I';""")
    op.execute("""UPDATE bookingkind SET shorttitle = 'EA2'
                  WHERE title = 'Energieabschlag II';""")
    op.execute("""UPDATE bookingkind SET shorttitle = 'EAR'
                  WHERE title = 'Energieabrechnung';""")
    op.execute("""UPDATE bookingkind SET shorttitle = 'GSB'
                  WHERE title = 'Grundsteuer B';""")
    op.execute("""UPDATE bookingkind SET shorttitle = 'ABW'
                  WHERE title = 'Abwasser';""")
    op.execute("""UPDATE bookingkind SET shorttitle = 'AUF'
                  WHERE title = 'Aufnahmegebühr';""")
    op.execute("""UPDATE booking SET kind_id = 1 WHERE id = 953;""")
    op.execute("""UPDATE booking SET kind_id = 2 WHERE id = 954;""")


def downgrade():
    op.add_column(
        'bookingkind',
        sa.Column('year', sa.INTEGER(), nullable=True))
    op.add_column(
        'bookingkind',
        sa.Column('value_per_member', sa.INTEGER(), nullable=True))
    op.drop_column('bookingkind', 'shorttitle')
