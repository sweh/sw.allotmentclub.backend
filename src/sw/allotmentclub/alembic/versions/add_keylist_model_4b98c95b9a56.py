"""Add keylist model.

Revision ID: 4b98c95b9a56
Revises: 1842f7373dcd
Create Date: 2016-07-06 20:22:33.558515

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '4b98c95b9a56'
down_revision = '1842f7373dcd'


def upgrade():
    op.create_table(
        'keylist',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('subject', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'key',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('keylist_id', sa.Integer(), nullable=False),
        sa.Column('serial', sa.String(), nullable=True),
        sa.Column('member_id', sa.Integer(), nullable=True),
        sa.Column('rent', sa.DateTime(), nullable=True),
        sa.Column('note', sa.String(), nullable=True),
        sa.Column('lost', sa.Boolean(), nullable=True, server_default='False'),
        sa.ForeignKeyConstraint(['keylist_id'], [u'keylist.id'], ),
        sa.ForeignKeyConstraint(['member_id'], [u'member.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.drop_constraint(u'key_keylist_id_fkey', 'key', type_='foreignkey')
    op.create_foreign_key(None, 'key', 'keylist', ['keylist_id'], ['id'],
                          ondelete=u'cascade')


def downgrade():
    op.drop_table('key')
    op.drop_table('keylist')
