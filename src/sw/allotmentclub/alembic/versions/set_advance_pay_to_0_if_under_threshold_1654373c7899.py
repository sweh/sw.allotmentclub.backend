"""Set advance pay to 0 if under threshold.

Revision ID: 1654373c7899
Revises: 51aecbad82b3
Create Date: 2015-03-27 08:15:43.051506

"""

# revision identifiers, used by Alembic.
from alembic import op

revision = '1654373c7899'
down_revision = u'51aecbad82b3'


def upgrade():
    op.execute("""UPDATE energyvalue SET advance_pay = 0 WHERE year = 2014
                  and advance_pay < 100000;""")
    op.execute("""UPDATE booking SET value = 0 WHERE
                  purpose = 'Energieabschlag I' and value > -100000;""")
    op.execute("""UPDATE booking SET value = 0 WHERE
                  purpose = 'Energieabschlag II' and value > -100000;""")


def downgrade():
    pass
