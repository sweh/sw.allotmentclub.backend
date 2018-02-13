"""Add direct debit date.

Revision ID: 411ca2f55194
Revises: 2b1aa8adb13b
Create Date: 2015-03-30 09:28:12.197684

"""

# revision identifiers, used by Alembic.
from alembic import op
import sqlalchemy as sa

revision = '411ca2f55194'
down_revision = '2b1aa8adb13b'


def upgrade():
    op.add_column('member',
                  sa.Column('direct_debit_date', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('member', 'direct_debit_date')
