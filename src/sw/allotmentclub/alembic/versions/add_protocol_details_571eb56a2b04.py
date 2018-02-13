"""Add protocol details.

Revision ID: 571eb56a2b04
Revises: 4ac1a4b79213
Create Date: 2014-12-16 22:08:56.474723

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '571eb56a2b04'
down_revision = '4ac1a4b79213'


def upgrade():
    op.create_table(
        'protocoldetail',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('protocol_id', sa.Integer(), nullable=False),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('responsible', sa.String(length=2), nullable=True),
        sa.ForeignKeyConstraint(['protocol_id'], [u'protocol.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('protocoldetail')
