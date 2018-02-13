# encoding=utf-8
"""Add accounting year to bookings.

Revision ID: 51aecbad82b3
Revises: 43123080ac3a
Create Date: 2015-03-11 16:27:13.098704

"""

# revision identifiers, used by Alembic.
from __future__ import unicode_literals
from alembic import op
import sqlalchemy as sa

revision = '51aecbad82b3'
down_revision = '43123080ac3a'


def upgrade():
    op.add_column(
        'booking',
        sa.Column('accounting_year', sa.Integer(), nullable=True))
    op.execute(
        "UPDATE booking SET accounting_year = EXTRACT(YEAR FROM booking_day);")
    op.execute(
        """INSERT into bankingaccount (number, name)
           VALUES ('1', 'Mitgliedsbeiträge')""")
    op.execute(
        """INSERT into bankingaccount (number, name)
           VALUES ('2', 'Fehlende Arbeitseinsätze')""")
    op.execute(
        """INSERT into bankingaccount (number, name)
           VALUES ('3', 'Abschläge Energie')""")


def downgrade():
    op.drop_column('booking', 'accounting_year')
    op.execute("DELETE FROM bankingaccount WHERE id != 1")
