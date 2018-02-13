"""Add iban and bic to member.

Revision ID: 2b1aa8adb13b
Revises: 75aee9c50aa
Create Date: 2015-03-29 19:00:05.393216

"""

# revision identifiers, used by Alembic.
from alembic import op
import sqlalchemy as sa

revision = '2b1aa8adb13b'
down_revision = '75aee9c50aa'


def upgrade():
    op.add_column('member',
                  sa.Column('bic', sa.String(length=11), nullable=True))
    op.add_column('member',
                  sa.Column('iban', sa.String(length=34), nullable=True))


def downgrade():
    op.drop_column('member', 'iban')
    op.drop_column('member', 'bic')
