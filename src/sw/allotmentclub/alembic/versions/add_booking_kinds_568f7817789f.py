"""Add booking kinds.

Revision ID: 568f7817789f
Revises: 1039814b69e3
Create Date: 2015-03-11 09:32:08.578225

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '568f7817789f'
down_revision = '1039814b69e3'


def upgrade():
    op.create_table(
        'bookingkind',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=20), nullable=False),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('value_per_member', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.add_column(
        u'booking', sa.Column('kind_id', sa.Integer(), nullable=True))
    op.execute("""INSERT into bookingkind (title, year, value_per_member)
                  VALUES ('Mitgliedsbeitrag', 2015, 600000);""")
    op.execute("""INSERT into bookingkind (title, year, value_per_member)
                  VALUES ('Fehl.Arb.Std', 2015, 50);""")
    op.execute("""INSERT into bookingkind (title, year)
                  VALUES ('Energieabschlag I', 2015);""")
    op.execute("""INSERT into bookingkind (title, year)
                  VALUES ('Energieabschlag II', 2015);""")
    op.execute("""INSERT into bookingkind (title, year)
                  VALUES ('Energieabrechnung', 2015);""")


def downgrade():
    op.drop_column(u'booking', 'kind_id')
    op.drop_table('bookingkind')
