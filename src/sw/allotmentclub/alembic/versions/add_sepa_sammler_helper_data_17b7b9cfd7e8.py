"""Add sepa sammler helper data.

Revision ID: 17b7b9cfd7e8
Revises: 41e271c4e3e8
Create Date: 2015-03-31 17:30:48.572311

"""

# revision identifiers, used by Alembic.
from alembic import op
import sqlalchemy as sa

revision = '17b7b9cfd7e8'
down_revision = '41e271c4e3e8'


def upgrade():
    op.create_table(
        'sepasammler',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('pmtinfid', sa.String(length=100), nullable=True),
        sa.Column('member_id', sa.Integer(), nullable=True),
        sa.Column('kind_id', sa.Integer(), nullable=True),
        sa.Column('value', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['kind_id'], [u'bookingkind.id'], ),
        sa.ForeignKeyConstraint(['member_id'], [u'member.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('sepasammler')
