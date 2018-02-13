"""Add leaving year to members.

Revision ID: 55a653c1d5a0
Revises: 30de960848fa
Create Date: 2015-11-06 14:11:22.301052

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '55a653c1d5a0'
down_revision = u'30de960848fa'


def upgrade():
    op.add_column(
        'member',
        sa.Column('leaving_year', sa.Integer(), nullable=True))
    op.execute("""UPDATE member SET leaving_year = 2014 WHERE id = 190;""")
    op.execute("""UPDATE member SET leaving_year = 2015 WHERE id in (
    142, 146, 128, 132, 86, 176);""")


def downgrade():
    op.drop_column('member', 'leaving_year')
