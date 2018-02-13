"""Add depot

Revision ID: 46276fff5bc2
Revises: 3ed04edde04e
Create Date: 2014-11-24 15:45:42.950371

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '46276fff5bc2'
down_revision = '3ed04edde04e'


def upgrade():
    op.create_table(
        'depot',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('size', sa.String(length=20), nullable=True),
        sa.Column('mimetype', sa.String(length=30), nullable=True),
        sa.Column('data', sa.LargeBinary(length=10485760), nullable=True),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], [u'user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('depot')
