"""Replace electric meter for Steinmüller (Zählerwechsel)

Revision ID: 897a3181401e
Revises: 9f65f923772f
Create Date: 2020-08-24 07:29:55.519846

"""
from alembic import op
import risclog.sqlalchemy

# revision identifiers, used by Alembic.
revision = '897a3181401e'
down_revision = '9f65f923772f'

OLD_NUMBER = '42418392'
OLD_VALUE = 28610
NEW_NUMBER = '30499547'
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
