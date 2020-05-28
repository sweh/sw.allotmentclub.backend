"""Replace electric meter for Annette (Zählerwechsel)

Revision ID: 9f65f923772f
Revises: e47f78fad78f
Create Date: 2020-05-28 07:02:37.097031

"""
from alembic import op
import risclog.sqlalchemy

# revision identifiers, used by Alembic.
revision = '9f65f923772f'
down_revision = 'e47f78fad78f'

OLD_NUMBER = '20235176'
OLD_VALUE = 40788
NEW_NUMBER = 'OE-WE-519'
NEW_VALUE = 0
YEAR = 2020


def upgrade():
    from sw.allotmentclub import ElectricMeter
    import transaction

    db = risclog.sqlalchemy.db.get_database()
    db._engines['portal'] = dict(
        engine=op.get_bind().engine,
        alembic_location="sw.allotmentclub:portal",
    )

    old = (ElectricMeter.query()
           .filter(ElectricMeter.number == OLD_NUMBER)
           .one())
    old.replace(old_value=OLD_VALUE, new_number=NEW_NUMBER,
                new_value=NEW_VALUE)
    transaction.commit()


def downgrade():
    from sw.allotmentclub import ElectricMeter
    import transaction

    db = risclog.sqlalchemy.db.get_database()
    db._engines['portal'] = dict(
        engine=op.get_bind().engine,
        alembic_location="sw.allotmentclub:portal",
    )

    to_delete = (ElectricMeter.query()
                 .filter(ElectricMeter.number == NEW_NUMBER)
                 .one())
    to_delete.get_value(YEAR).delete()
    to_delete.delete()

    old = (ElectricMeter.query()
           .filter(ElectricMeter.number == OLD_NUMBER)
           .one())
    old.get_value(YEAR-1).delete()
    transaction.commit()
