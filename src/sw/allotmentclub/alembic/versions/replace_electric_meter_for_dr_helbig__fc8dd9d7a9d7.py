"""Replace electric meter for Dr. Helbig (Zählerwechsel)

Revision ID: fc8dd9d7a9d7
Revises: 9af3776b0ea9
Create Date: 2019-11-11 07:47:38.501928

"""
from alembic import op
import risclog.sqlalchemy

# revision identifiers, used by Alembic.
revision = 'fc8dd9d7a9d7'
down_revision = '9af3776b0ea9'

OLD_NUMBER = '364754'
OLD_VALUE = 7730
NEW_NUMBER = '0014E698'
NEW_VALUE = 0
YEAR = 2018


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
