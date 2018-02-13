"""Add revision security flag for users.

Revision ID: 95c83e9e7d18
Revises: 2330cb148c04
Create Date: 2016-05-21 13:57:49.741449

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '95c83e9e7d18'
down_revision = '2330cb148c04'


def upgrade():
    op.add_column(
        'user',
        sa.Column('is_revision', sa.Boolean(),
                  server_default=sa.text(u'false'), nullable=False))


def downgrade():
    op.drop_column('user', 'is_revision')
