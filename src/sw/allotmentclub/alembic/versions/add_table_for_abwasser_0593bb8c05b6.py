"""Add table for Abwasser.

Revision ID: 0593bb8c05b6
Revises: 9dadb9f9561f
Create Date: 2016-07-03 17:00:35.532851

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0593bb8c05b6'
down_revision = '9dadb9f9561f'


def upgrade():
    op.create_table(
        'abwasser',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('parcel_id', sa.Integer(), nullable=False),
        sa.Column('value', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['parcel_id'], [u'parcel.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.execute(
        "INSERT into abwasser (parcel_id, value) VALUES (85, 600000);")
    op.execute(
        "INSERT into abwasser (parcel_id, value) VALUES (86, 600000);")
    op.execute(
        "INSERT into abwasser (parcel_id, value) VALUES (116, 600000);")
    op.execute(
        "INSERT into abwasser (parcel_id, value) VALUES (153, 600000);")
    op.execute(
        "INSERT into abwasser (parcel_id, value) VALUES (119, 600000);")
    op.execute(
        "INSERT into abwasser (parcel_id, value) VALUES (120, 600000);")
    op.execute(
        "INSERT into abwasser (parcel_id, value) VALUES (177, 600000);")
    op.execute(
        "INSERT into abwasser (parcel_id, value) VALUES (175, 600000);")
    op.execute(
        "INSERT into abwasser (parcel_id, value) VALUES (128, 600000);")
    op.execute(
        "INSERT into abwasser (parcel_id, value) VALUES (159, 600000);")
    op.execute(
        "INSERT into abwasser (parcel_id, value) VALUES (134, 600000);")
    op.execute(
        "INSERT into abwasser (parcel_id, value) VALUES (165, 600000);")
    op.execute(
        "INSERT into abwasser (parcel_id, value) VALUES (147, 600000);")
    op.execute(
        "INSERT into abwasser (parcel_id, value) VALUES (172, 300000);")
    op.execute(
        "INSERT into abwasser (parcel_id, value) VALUES (174, 300000);")
    op.execute(
        "INSERT into abwasser (parcel_id, value) VALUES (99, 600000);")


def downgrade():
    op.drop_table('abwasser')
