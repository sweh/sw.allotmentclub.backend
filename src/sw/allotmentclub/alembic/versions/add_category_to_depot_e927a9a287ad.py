"""Add category to depot.

Revision ID: e927a9a287ad
Revises: 7e0a65cb279f
Create Date: 2023-03-22 12:42:43.316748

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e927a9a287ad'
down_revision = '7e0a65cb279f'


def upgrade():
    op.add_column('depot', sa.Column('category', sa.String(length=100),
                                     nullable=True))


def downgrade():
    op.drop_column('depot', 'category')
