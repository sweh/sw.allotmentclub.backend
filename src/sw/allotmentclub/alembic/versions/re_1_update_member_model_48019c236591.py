"""re #1: Update Member model.

Revision ID: 48019c236591
Revises: 46276fff5bc2
Create Date: 2014-12-02 19:03:49.975576

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '48019c236591'
down_revision = '46276fff5bc2'


def upgrade():
    op.create_table(
        'allotment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('number', sa.Integer(), nullable=False),
        sa.Column('member_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['member_id'], [u'member.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'parcel',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('number', sa.Integer(), nullable=False),
        sa.Column('allotment_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['allotment_id'], [u'allotment.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.add_column(
        u'member',
        sa.Column('appellation', sa.String(length=20), nullable=True))
    op.add_column(
        u'member',
        sa.Column('city', sa.String(length=50), nullable=True))
    op.add_column(
        u'member',
        sa.Column('country', sa.String(length=50), nullable=True))
    op.add_column(
        u'member',
        sa.Column('firstname', sa.String(length=50), nullable=True))
    op.add_column(
        u'member',
        sa.Column('lastname', sa.String(length=50), nullable=True))
    op.add_column(
        u'member', sa.Column('mobile', sa.String(length=50), nullable=True))
    op.add_column(
        u'member', sa.Column('phone', sa.String(length=50), nullable=True))
    op.add_column(
        u'member', sa.Column('street', sa.String(length=100), nullable=True))
    op.add_column(
        u'member', sa.Column('title', sa.String(length=20), nullable=True))
    op.add_column(
        u'member', sa.Column('zip', sa.String(length=6), nullable=True))
    op.drop_column(u'member', 'ort')
    op.drop_column(u'member', 'zaehlernummer')
    op.drop_column(u'member', 'plz')
    op.drop_column(u'member', 'anrede')
    op.drop_column(u'member', 'nachname')
    op.drop_column(u'member', 'haus_nr')
    op.drop_column(u'member', 'strasse')
    op.drop_column(u'member', 'vorname')


def downgrade():
    op.add_column(
        u'member', sa.Column('vorname', sa.VARCHAR(length=50), nullable=True))
    op.add_column(
        u'member', sa.Column('strasse', sa.VARCHAR(length=100), nullable=True))
    op.add_column(
        u'member', sa.Column('haus_nr', sa.VARCHAR(length=7), nullable=True))
    op.add_column(
        u'member', sa.Column('nachname', sa.VARCHAR(length=50), nullable=True))
    op.add_column(
        u'member', sa.Column('anrede', sa.VARCHAR(length=20), nullable=True))
    op.add_column(
        u'member', sa.Column('plz', sa.VARCHAR(length=6), nullable=True))
    op.add_column(
        u'member',
        sa.Column('zaehlernummer', sa.VARCHAR(length=50), nullable=True))
    op.add_column(
        u'member', sa.Column('ort', sa.VARCHAR(length=50), nullable=True))
    op.drop_column(u'member', 'zip')
    op.drop_column(u'member', 'title')
    op.drop_column(u'member', 'street')
    op.drop_column(u'member', 'phone')
    op.drop_column(u'member', 'mobile')
    op.drop_column(u'member', 'lastname')
    op.drop_column(u'member', 'firstname')
    op.drop_column(u'member', 'country')
    op.drop_column(u'member', 'city')
    op.drop_column(u'member', 'appellation')
    op.drop_table('parcel')
    op.drop_table('allotment')
