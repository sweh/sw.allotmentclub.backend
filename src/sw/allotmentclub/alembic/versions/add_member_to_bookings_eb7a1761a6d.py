"""Add member to bookings.

Revision ID: eb7a1761a6d
Revises: 28e32b8a26f4
Create Date: 2015-03-10 16:38:06.335776

"""

# revision identifiers, used by Alembic.
from alembic import op
import sqlalchemy as sa

revision = 'eb7a1761a6d'
down_revision = '28e32b8a26f4'


def upgrade():
    op.add_column(
        'booking', sa.Column('member_id', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('booking', 'member_id')
