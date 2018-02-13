"""Save calculation of energy values in database.

Revision ID: 186285f37c74
Revises: 2cb8d240d5ac
Create Date: 2015-03-03 10:04:37.845978

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '186285f37c74'
down_revision = '2cb8d240d5ac'


def upgrade():
    op.add_column('energyvalue',
                  sa.Column('advance_pay', sa.Integer(), nullable=True))
    op.add_column('energyvalue',
                  sa.Column('fee', sa.Integer(), nullable=True))
    op.add_column('energyvalue',
                  sa.Column('price', sa.Integer(), nullable=True))
    op.add_column('energyvalue',
                  sa.Column('usage', sa.Integer(), nullable=True))
    op.add_column('energyvalue',
                  sa.Column('whole_price', sa.Integer(), nullable=True))
    op.add_column('energyvalue',
                  sa.Column('discounted', sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column('energyvalue', 'whole_price')
    op.drop_column('energyvalue', 'usage')
    op.drop_column('energyvalue', 'price')
    op.drop_column('energyvalue', 'fee')
    op.drop_column('energyvalue', 'advance_pay')
    op.drop_column('energyvalue', 'discounted')
