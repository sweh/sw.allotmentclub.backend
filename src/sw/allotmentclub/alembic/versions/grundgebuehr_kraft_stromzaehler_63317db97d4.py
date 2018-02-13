"""Grundgebuehr (Kraft-)Stromzaehler.

Revision ID: 63317db97d4
Revises: 444966e3e7d6
Create Date: 2014-12-25 08:20:45.348586

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '63317db97d4'
down_revision = '444966e3e7d6'


def upgrade():
    op.add_column(
        'energyprice',
        sa.Column('normal_fee', sa.Integer(), nullable=True))
    op.add_column(
        'energyprice',
        sa.Column('power_fee', sa.Integer(), nullable=True))
    op.execute("""UPDATE energyprice SET price = 3020, normal_fee = 81700,
                  power_fee = 243300 WHERE year = 2014;""")


def downgrade():
    op.drop_column('energyprice', 'power_fee')
    op.drop_column('energyprice', 'normal_fee')
