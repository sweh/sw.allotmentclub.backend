"""Add attachments to parcels

Revision ID: 9af3776b0ea9
Revises: ecca91384800
Create Date: 2019-11-05 08:28:17.231686

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '9af3776b0ea9'
down_revision = 'ecca91384800'


def upgrade():
    op.create_table(
        'parcelattachment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('parcel_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('mimetype', sa.String(length=100), nullable=True),
        sa.Column('size', sa.String(length=20), nullable=True),
        sa.Column('data', sa.LargeBinary(length=10485760), nullable=True),
        sa.ForeignKeyConstraint(['parcel_id'], ['parcel.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('parcelattachment')
