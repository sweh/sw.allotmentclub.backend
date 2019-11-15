"""Change parcel attachments to parcel map

Revision ID: 98db6b34d1a3
Revises: fc8dd9d7a9d7
Create Date: 2019-11-15 07:38:48.934387

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '98db6b34d1a3'
down_revision = 'fc8dd9d7a9d7'


def upgrade():
    op.drop_table('parcelattachment')
    op.add_column(
        'parcel',
        sa.Column(
            'map_data',
            sa.LargeBinary(length=10485760),
            nullable=True
        )
    )
    op.add_column(
        'parcel',
        sa.Column('map_mimetype', sa.String(length=100), nullable=True)
    )
    op.add_column(
        'parcel',
        sa.Column('map_size', sa.String(length=20), nullable=True)
    )


def downgrade():
    op.drop_column('parcel', 'map_size')
    op.drop_column('parcel', 'map_mimetype')
    op.drop_column('parcel', 'map_data')
    op.create_table(
        'parcelattachment',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column(
            'organization_id', sa.INTEGER(), autoincrement=False,
            nullable=False
        ),
        sa.Column(
            'parcel_id', sa.INTEGER(), autoincrement=False, nullable=False
        ),
        sa.Column(
            'name', sa.VARCHAR(length=100), autoincrement=False, nullable=True
        ),
        sa.Column(
            'mimetype', sa.VARCHAR(length=100), autoincrement=False,
            nullable=True
        ),
        sa.Column(
            'size', sa.VARCHAR(length=20), autoincrement=False, nullable=True
        ),
        sa.Column(
            'data', postgresql.BYTEA(), autoincrement=False, nullable=True
        ),
        sa.ForeignKeyConstraint(
            ['parcel_id'],
            ['parcel.id'],
            name='parcelattachment_parcel_id_fkey'
        ),
        sa.PrimaryKeyConstraint('id', name='parcelattachment_pkey')
    )
