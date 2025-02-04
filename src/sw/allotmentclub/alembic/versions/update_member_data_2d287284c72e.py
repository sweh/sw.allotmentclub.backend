"""Update member data.

Revision ID: 2d287284c72e
Revises: 50035156da61
Create Date: 2015-09-14 10:34:10.825636

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "2d287284c72e"
down_revision = "50035156da61"


def upgrade():
    op.add_column(
        "energyvalue", sa.Column("to_pay", sa.Integer(), nullable=True)
    )
    op.execute("UPDATE energyvalue SET to_pay = 0")
    op.execute("""
        INSERT into electricmeter
               (id, allotment_id, number, electric_power, disconnected)
            VALUES
               (124, 197, 0, False, False)""")
    op.execute("""
        INSERT into energyvalue (electric_meter_id, year, value, member_id,
               advance_pay, fee, price, usage, whole_price, discounted, to_pay)
            VALUES (124, 2014, 0, 188, 0, 0, 0, 0, 0, true, 0)""")
    op.execute("""
        INSERT into bookingkind
               (title, year, value_per_member, banking_account_id)
            VALUES ('Mitgliedsbeitrag', 2016, 750000, 4)""")
    op.execute("""
        INSERT into bookingkind (title, year, banking_account_id)
            VALUES ('Energieabschlag I', 2016, 4)""")
    op.execute("""
        INSERT into bookingkind (title, year, banking_account_id)
            VALUES ('Energieabschlag II', 2016, 4)""")
    op.execute("""
        INSERT into bookingkind (title, year, banking_account_id)
            VALUES ('Energieabrechnung', 2016, 4)""")
    op.execute("DELETE FROM booking WHERE id in (404, 405, 406, 407)")
    op.execute(
        "UPDATE member SET email = 'boehme.wsf@online.de' WHERE id = 126"
    )
    op.execute("""
        UPDATE energyprice
            SET price = 2786,
                normal_fee = 67000,
                power_fee = 201100
            WHERE year = 2015""")


def downgrade():
    op.drop_column("energyvalue", "to_pay")
