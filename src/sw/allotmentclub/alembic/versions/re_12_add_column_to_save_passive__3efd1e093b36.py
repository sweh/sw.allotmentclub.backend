"""re #12: Add column to save passive allotment

Revision ID: 3efd1e093b36
Revises: 53f3d16657d3
Create Date: 2021-01-02 16:19:38.218669

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '3efd1e093b36'
down_revision = '53f3d16657d3'


def upgrade():
    op.add_column(
        'member',
        sa.Column('passive_allotment_id', sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        'passive_allotment_id_fkey', 'member', 'allotment',
        ['passive_allotment_id'], ['id']
    )


def downgrade():
    op.drop_constraint(
        'passive_allotment_id_fkey', 'member', type_='foreignkey'
    )
    op.drop_column('member', 'passive_allotment_id')
