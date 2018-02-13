"""Allow formletters without address field.

Revision ID: 12459e1b365d
Revises: 38a1521607b5
Create Date: 2015-01-26 13:34:52.203956

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '12459e1b365d'
down_revision = '38a1521607b5'


def upgrade():
    op.add_column(
        'formletter', sa.Column('with_address', sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column('formletter', 'with_address')
