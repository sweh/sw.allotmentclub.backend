"""Add content for form letters.

Revision ID: 3c0b1fc7eeed
Revises: 12459e1b365d
Create Date: 2015-01-26 14:24:43.103348

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '3c0b1fc7eeed'
down_revision = '12459e1b365d'


def upgrade():
    op.add_column('formletter', sa.Column('content', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('formletter', 'content')
