"""Add protocol attachments and commitments.

Revision ID: 51143cacbf85
Revises: 571eb56a2b04
Create Date: 2014-12-17 11:31:54.057025

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '51143cacbf85'
down_revision = '571eb56a2b04'


def upgrade():
    op.create_table(
        'protocolcommitment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('protocol_id', sa.Integer(), nullable=False),
        sa.Column('who', sa.String(length=254), nullable=True),
        sa.Column('what', sa.String(length=254), nullable=True),
        sa.Column('when', sa.String(length=254), nullable=True),
        sa.ForeignKeyConstraint(['protocol_id'], [u'protocol.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'protocolattachment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('protocol_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('mimetype', sa.String(length=30), nullable=True),
        sa.Column('size', sa.String(length=20), nullable=True),
        sa.Column('data', sa.LargeBinary(length=10485760), nullable=True),
        sa.ForeignKeyConstraint(['protocol_id'], [u'protocol.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('protocolattachment')
    op.drop_table('protocolcommitment')
