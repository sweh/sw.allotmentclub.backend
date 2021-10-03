"""Replace electric meter for Verein (Zählerwechsel)

Revision ID: ad2b49f5d70a
Revises: d0bfe38ddce2
Create Date: 2021-10-03 09:40:38.096547

"""
from alembic import op
import risclog.sqlalchemy

# revision identifiers, used by Alembic.
revision = 'ad2b49f5d70a'
down_revision = 'd0bfe38ddce2'

OLD_NUMBER = '409120'
OLD_VALUE = 5386
NEW_NUMBER = '6002'
NEW_VALUE = 0
YEAR = 2021


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
