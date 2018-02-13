"""Prepare message hierachy.

Revision ID: fd9f9588878d
Revises: ff18c87afd8e
Create Date: 2017-06-07 14:34:34.902567

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'fd9f9588878d'
down_revision = 'ff18c87afd8e'


def upgrade():
    op.add_column('message',
                  sa.Column('in_reply_to_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        None, 'message', 'message', ['in_reply_to_id'], ['id'])


def downgrade():
    op.drop_constraint(None, 'message', type_='foreignkey')
    op.drop_column('message', 'in_reply_to_id')
