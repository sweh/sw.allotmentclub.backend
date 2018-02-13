"""Add accounting year for protocols.

Revision ID: 20588bf7b8a7
Revises: 55a653c1d5a0
Create Date: 2015-11-09 08:42:09.370420

"""

# revision identifiers, used by Alembic.
from alembic import op
import sqlalchemy as sa

revision = '20588bf7b8a7'
down_revision = '55a653c1d5a0'


def upgrade():
    op.add_column('protocol',
                  sa.Column('accounting_year', sa.Integer(), nullable=True))
    op.execute("""UPDATE protocol set accounting_year = 2014
                  WHERE day::text like '2014%';""")
    op.execute("""UPDATE protocol set accounting_year = 2015
                  WHERE day::text like '2015%';""")
    op.execute("""UPDATE protocol set accounting_year = 2016
                  WHERE day::text like '2016%';""")


def downgrade():
    op.drop_column('protocol', 'accounting_year')
