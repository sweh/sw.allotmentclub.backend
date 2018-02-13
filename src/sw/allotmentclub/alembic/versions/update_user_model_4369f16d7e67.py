"""Update user model.

Revision ID: 4369f16d7e67
Revises: 43245c2d427e
Create Date: 2015-11-16 10:43:23.539911

"""

# revision identifiers, used by Alembic.
from alembic import op
import sqlalchemy as sa

revision = '4369f16d7e67'
down_revision = '43245c2d427e'


def upgrade():
    op.add_column(
        'message',
        sa.Column('user_id', sa.Integer(), nullable=False, server_default='2'))


def downgrade():
    op.drop_column('message', 'user_id')
