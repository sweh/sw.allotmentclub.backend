"""Add subject to formletters.

Revision ID: 1c44d30192ea
Revises: 3c0b1fc7eeed
Create Date: 2015-01-26 15:37:25.999671

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '1c44d30192ea'
down_revision = '3c0b1fc7eeed'


def upgrade():
    op.add_column('formletter',
                  sa.Column('subject', sa.String(), nullable=True))


def downgrade():
    op.drop_column('formletter', 'subject')
