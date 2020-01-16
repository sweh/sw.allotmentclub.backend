"""Add SEPA Sammelueberweisung

Revision ID: e47f78fad78f
Revises: 98db6b34d1a3
Create Date: 2020-01-16 08:01:46.509668

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e47f78fad78f'
down_revision = '98db6b34d1a3'


def upgrade():
    op.add_column(
        'sepasammler',
        sa.Column(
            'is_ueberweisung',
            sa.Boolean(),
            nullable=False,
            server_default='False',
        )
    )


def downgrade():
    op.drop_column('sepasammler', 'is_ueberweisung')
