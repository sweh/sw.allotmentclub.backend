"""Hash IBAN and BIC.

Revision ID: 1039814b69e3
Revises: eb7a1761a6d
Create Date: 2015-03-10 18:58:08.261285

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '1039814b69e3'
down_revision = 'eb7a1761a6d'


def upgrade():
    op.add_column(
        'booking',
        sa.Column('account_number', sa.String(length=56), nullable=True))
    op.drop_column('booking', 'iban')
    op.drop_column('booking', 'bic')


def downgrade():
    op.add_column(
        'booking', sa.Column('bic', sa.VARCHAR(length=15), nullable=True))
    op.add_column(
        'booking', sa.Column('iban', sa.VARCHAR(length=25), nullable=True))
    op.drop_column('booking', 'account_number')
