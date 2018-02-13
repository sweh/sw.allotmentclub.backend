# encoding=utf8
"""Add payer name to direct debit.

Revision ID: cfc9142d7e69
Revises: c3c978348cbf
Create Date: 2016-02-15 07:52:19.049448

"""
from __future__ import unicode_literals
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'cfc9142d7e69'
down_revision = 'c3c978348cbf'


def upgrade():
    op.add_column(
        'member',
        sa.Column('direct_debit_account_holder',
                  sa.String(length=100), nullable=True))
    op.execute(
        """UPDATE member SET
            firstname = 'Thomas',
            lastname = 'Sonntag',
            street = 'Auenwinkel 2',
            zip = '06237',
            city = 'Leuna/OT Maßlau',
            email = 'tschloeffel@freenet.de',
            direct_debit_account_holder = 'Schlöffel, Heinz'
     WHERE id = 109;""")


def downgrade():
    op.execute(
        """UPDATE member SET
            firstname = 'Heinz',
            lastname = 'Schlöffel',
            street = 'Auenwinkel 7',
            zip = '06237',
            city = 'Leuna',
            email = 'heinz.schloeffel@freenet.de'
     WHERE id = 109;""")
    op.drop_column('member', 'direct_debit_account_holder')
