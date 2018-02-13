"""Delete due payments for members that have sold their allotment.

Revision ID: 45d928fd0cb7
Revises: cfc9142d7e69
Create Date: 2016-03-14 09:29:49.734108

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '45d928fd0cb7'
down_revision = u'cfc9142d7e69'


def upgrade():
    op.execute("""DELETE FROM booking
                  WHERE accounting_year = 2016 and member_id in (132, 128);""")
    op.execute("""UPDATE member SET bic = 'DRESDEFF800' WHERE id = 118;""")


def downgrade():
    pass
