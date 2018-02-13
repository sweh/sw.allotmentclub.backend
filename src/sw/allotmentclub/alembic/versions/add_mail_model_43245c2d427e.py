"""Add mail model.

Revision ID: 43245c2d427e
Revises: 20588bf7b8a7
Create Date: 2015-11-16 09:43:01.683171

"""

# revision identifiers, used by Alembic.
from alembic import op
import sqlalchemy as sa

revision = '43245c2d427e'
down_revision = '20588bf7b8a7'


def upgrade():
    op.create_table(
        'message',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('member_id', sa.Integer(), nullable=True),
        sa.Column('subject', sa.String(length=255), nullable=True),
        sa.Column('body', sa.Text(), nullable=True),
        sa.Column('sent', sa.Date(), nullable=True),
        sa.Column('accounting_year', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['member_id'], ['member.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('message')
