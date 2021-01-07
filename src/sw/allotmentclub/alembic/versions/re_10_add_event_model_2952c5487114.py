"""re #10: Add event model

Revision ID: 2952c5487114
Revises: c4dbe65a7810
Create Date: 2021-01-06 12:51:42.034633

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2952c5487114'
down_revision = 'c4dbe65a7810'


def upgrade():
    op.create_table(
        'event',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('start', sa.DateTime(), nullable=True),
        sa.Column('end', sa.DateTime(), nullable=True),
        sa.Column('allday', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('event')
