"""Add new data to members.

Revision ID: 4d42c583ac73
Revises: None
Create Date: 2014-10-27 13:32:02.315587

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '4d42c583ac73'
down_revision = None


def upgrade():
    op.add_column(
        'member', sa.Column('haus_nr', sa.String(length=7), nullable=True))
    op.add_column(
        'member', sa.Column('ort', sa.String(length=50), nullable=True))
    op.add_column(
        'member', sa.Column('plz', sa.String(length=6), nullable=True))
    op.add_column(
        'member', sa.Column('strasse', sa.String(length=100), nullable=True))
    op.add_column(
        'member',
        sa.Column('zaehlernummer', sa.String(length=50), nullable=True))
    op.drop_column('member', 'titel')
    op.create_unique_constraint(None, 'member', ['haus_nr'])
    op.create_unique_constraint(None, 'member', ['zaehlernummer'])


def downgrade():
    op.drop_constraint(None, 'member')
    op.drop_constraint(None, 'member')
    op.add_column(
        'member', sa.Column('titel', sa.VARCHAR(length=20), nullable=True))
    op.drop_column('member', 'zaehlernummer')
    op.drop_column('member', 'strasse')
    op.drop_column('member', 'plz')
    op.drop_column('member', 'ort')
    op.drop_column('member', 'haus_nr')
