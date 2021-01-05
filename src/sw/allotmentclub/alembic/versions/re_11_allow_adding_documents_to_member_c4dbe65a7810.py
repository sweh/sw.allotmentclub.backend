"""re #11: Allow adding documents to member

Revision ID: c4dbe65a7810
Revises: 3efd1e093b36
Create Date: 2021-01-05 11:23:35.604257

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'c4dbe65a7810'
down_revision = '3efd1e093b36'


def upgrade():
    op.create_table(
        'memberattachment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('member_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('mimetype', sa.String(length=30), nullable=True),
        sa.Column('size', sa.String(length=20), nullable=True),
        sa.Column('data', sa.LargeBinary(length=10485760), nullable=True),
        sa.ForeignKeyConstraint(['member_id'], ['member.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('memberattachment')
