"""Replace electric meter for Dr. Kern (Zählerwechsel)

Revision ID: ecca91384800
Revises: f4b90b599d2a
Create Date: 2019-07-29 07:57:40.515472

"""

import risclog.sqlalchemy
from alembic import op

# revision identifiers, used by Alembic.
revision = "ecca91384800"
down_revision = "f4b90b599d2a"

OLD_NUMBER = "32095620"
OLD_VALUE = 78250
NEW_NUMBER = "131590-M18"
NEW_VALUE = 0
YEAR = 2019


def upgrade():
    import transaction
    from sw.allotmentclub import ElectricMeter

    db = risclog.sqlalchemy.db.get_database()
    db._engines["portal"] = dict(
        engine=op.get_bind().engine,
        alembic_location="sw.allotmentclub:portal",
    )

    old = (
        ElectricMeter.query().filter(ElectricMeter.number == OLD_NUMBER).one()
    )
    old.replace(
        old_value=OLD_VALUE, new_number=NEW_NUMBER, new_value=NEW_VALUE
    )
    transaction.commit()


def downgrade():
    import transaction
    from sw.allotmentclub import ElectricMeter

    db = risclog.sqlalchemy.db.get_database()
    db._engines["portal"] = dict(
        engine=op.get_bind().engine,
        alembic_location="sw.allotmentclub:portal",
    )

    to_delete = (
        ElectricMeter.query().filter(ElectricMeter.number == NEW_NUMBER).one()
    )
    to_delete.get_value(YEAR).delete()
    to_delete.delete()

    old = (
        ElectricMeter.query().filter(ElectricMeter.number == OLD_NUMBER).one()
    )
    old.get_value(YEAR - 1).delete()
    transaction.commit()
