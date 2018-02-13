"""Add model for Arbeitseinsaetze.

Revision ID: 3ed04edde04e
Revises: 29f31fb4aa
Create Date: 2014-11-10 18:34:35.335596

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '3ed04edde04e'
down_revision = '29f31fb4aa'


def upgrade():
    op.create_table(
        'assignment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('purpose', sa.String(length=254), nullable=True),
        sa.Column('responsible_id', sa.Integer(), nullable=True),
        sa.Column('day', sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(['responsible_id'], [u'member.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'assignmentattendee',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('assignment_id', sa.Integer(), nullable=False),
        sa.Column('member_id', sa.Integer(), nullable=False),
        sa.Column('hours', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['assignment_id'], [u'assignment.id'], ),
        sa.ForeignKeyConstraint(['member_id'], [u'member.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('assignmentattendee')
    op.drop_table('assignment')
