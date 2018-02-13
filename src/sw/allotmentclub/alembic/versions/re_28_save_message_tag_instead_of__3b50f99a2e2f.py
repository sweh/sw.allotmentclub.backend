"""re #28: Save message tag instead of Message-ID.

Revision ID: 3b50f99a2e2f
Revises: ff1bb01af7fa
Create Date: 2016-11-23 09:24:49.794794

"""
# revision identifiers, used by Alembic.
from alembic import op
import sqlalchemy as sa

revision = '3b50f99a2e2f'
down_revision = 'ff1bb01af7fa'


def upgrade():
    op.add_column('sentmessageinfo',
                  sa.Column('tag', sa.String(length=100), nullable=True))
    op.drop_column('sentmessageinfo', 'msg_id')


def downgrade():
    op.add_column('sentmessageinfo',
                  sa.Column('msg_id', sa.VARCHAR(length=100),
                            autoincrement=False, nullable=True))
    op.drop_column('sentmessageinfo', 'tag')
