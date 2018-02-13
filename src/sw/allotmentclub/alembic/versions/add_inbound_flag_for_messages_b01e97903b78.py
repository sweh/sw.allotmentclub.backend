"""Add inbound flag for messages.

Revision ID: b01e97903b78
Revises: 78f2790c1501
Create Date: 2017-05-12 09:11:30.803425

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b01e97903b78'
down_revision = '78f2790c1501'


def upgrade():
    op.add_column('message',
                  sa.Column('inbound', sa.Boolean(), nullable=False,
                            server_default=sa.false()))


def downgrade():
    op.drop_column('message', 'inbound')
