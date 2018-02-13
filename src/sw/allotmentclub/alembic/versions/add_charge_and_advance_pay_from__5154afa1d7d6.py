"""Add charge and advance pay from electricity facroty.

Revision ID: 5154afa1d7d6
Revises: 63317db97d4
Create Date: 2014-12-25 08:59:45.936941

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '5154afa1d7d6'
down_revision = '63317db97d4'


def upgrade():
    op.add_column(
        'energyprice',
        sa.Column('advance_pay', sa.Integer(), nullable=True))
    op.add_column(
        'energyprice',
        sa.Column('charge', sa.Integer(), nullable=True))
    op.execute("UPDATE energyprice SET charge = 122910900 WHERE year = 2014;")
    op.execute(
        "INSERT into energyprice (year, advance_pay) VALUES (2015, 10500000);")


def downgrade():
    op.drop_column('energyprice', 'charge')
    op.drop_column('energyprice', 'advance_pay')
