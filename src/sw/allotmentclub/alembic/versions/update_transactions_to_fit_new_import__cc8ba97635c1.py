"""Update transactions to fit new import format.

Revision ID: cc8ba97635c1
Revises: 1755a035e42a
Create Date: 2016-02-02 14:16:40.837958

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "cc8ba97635c1"
down_revision = "1755a035e42a"


def upgrade():
    op.execute("""UPDATE booking SET purpose = 'Versicherungen.
        Unfallversicherung ZIS-289848871106233*Bungalow GemeinschaftDATUM
        16.12.2015, 19.39 UHR1.TAN 804995' WHERE id = 1206;""")
    op.execute("""UPDATE booking SET recipient = 'Gothaer Allgemeine Versiche',
        purpose = '83.661.577869 ABBUCHUNG AM 04.01.2016
        HAFTPFLICHT-VERSICHERUNG H' WHERE id = 1204;""")
    op.execute("""UPDATE booking SET purpose = '41-02-98011329 Gebaeude
        EUR 141,39 41-07-98011328Hausrat EUR 247,61' WHERE id = 1205;""")
    op.execute("""UPDATE booking SET purpose = 'ENTGELT SPKCARD MIT
        CHIPKARTE 5180073894SUSANN TILLACK' WHERE id = 1215""")


def downgrade():
    pass
