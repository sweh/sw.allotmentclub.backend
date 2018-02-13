"""Add banking account model.

Revision ID: 28e32b8a26f4
Revises: 24a3f3740664
Create Date: 2015-03-10 13:03:39.397736

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '28e32b8a26f4'
down_revision = '24a3f3740664'


def upgrade():
    op.create_table(
        'bankingaccount',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('number', sa.String(length=10)),
        sa.Column('name', sa.String(length=30), nullable=True),
        sa.Column('last_import', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'booking',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('banking_account_id', sa.Integer(), nullable=False),
        sa.Column('booking_day', sa.Date(), nullable=True),
        sa.Column('booking_text', sa.String(), nullable=True),
        sa.Column('purpose', sa.String(), nullable=True),
        sa.Column('recipient', sa.String(), nullable=True),
        sa.Column('iban', sa.String(length=25), nullable=True),
        sa.Column('bic', sa.String(length=15), nullable=True),
        sa.Column('value', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint([
            'banking_account_id'], [u'bankingaccount.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.execute("""INSERT into bankingaccount (number, name)
                  VALUES ('3440000167', 'Vereinskonto');""")


def downgrade():
    op.drop_table('booking')
    op.drop_table('bankingaccount')
