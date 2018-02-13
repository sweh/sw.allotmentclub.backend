"""Add printed timestamp to mail.

Revision ID: 433297b9762
Revises: 38a169e80b6e
Create Date: 2015-11-17 07:13:52.623564

"""

# revision identifiers, used by Alembic.
from alembic import op
import sqlalchemy as sa

revision = '433297b9762'
down_revision = '38a169e80b6e'


def upgrade():
    op.add_column('message',
                  sa.Column('printed', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('message', 'printed')
