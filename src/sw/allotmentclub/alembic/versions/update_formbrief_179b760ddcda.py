"""Update formbrief

Revision ID: 179b760ddcda
Revises: 2535014c8ab8
Create Date: 2015-01-03 14:47:15.191085

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '179b760ddcda'
down_revision = '2535014c8ab8'


def upgrade():
    op.add_column('formletter',
                  sa.Column('date', sa.DateTime(), nullable=False))
    op.add_column('formletter',
                  sa.Column('user_id', sa.Integer(), nullable=False))


def downgrade():
    op.drop_column('formletter', 'user_id')
    op.drop_column('formletter', 'date')
