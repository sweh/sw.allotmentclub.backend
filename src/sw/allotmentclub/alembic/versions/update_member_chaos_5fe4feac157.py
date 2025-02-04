"""Update member chaos

Revision ID: 5fe4feac157
Revises: 17b7b9cfd7e8
Create Date: 2015-04-01 12:41:15.669249

"""

# revision identifiers, used by Alembic.
from alembic import op

revision = "5fe4feac157"
down_revision = "17b7b9cfd7e8"


def upgrade():
    op.execute("""UPDATE allotment SET member_id = 186 WHERE id = 118;""")
    op.execute("""UPDATE allotment SET member_id = 109 WHERE id = 128;""")
    op.execute("""UPDATE booking SET member_id = 186 WHERE id = 251;""")
    op.execute("""UPDATE booking SET member_id = 186 WHERE id = 250;""")
    op.execute("""UPDATE booking SET member_id = 186 WHERE id = 102;""")
    op.execute("""UPDATE member SET iban = null, bic = null,
                  direct_debit_date = null, direct_debit = false
                  WHERE id = 109;""")
    op.execute("""UPDATE energyvalue SET member_id = 186 WHERE id = 77;""")
    op.execute("""UPDATE energyvalue SET member_id = 186 WHERE id = 78;""")
    op.execute("""UPDATE energyvalue SET member_id = 186 WHERE id = 79;""")
    op.execute("""UPDATE energyvalue SET member_id = 186 WHERE id = 80;""")
    op.execute("""UPDATE energyvalue SET member_id = 109 WHERE id = 101;""")
    op.execute("""UPDATE energyvalue SET member_id = 109 WHERE id = 102;""")
    op.execute("""UPDATE member SET iban = 'DE68800636480801753000',
                  bic = 'GENODEF1NMB', direct_debit_date = '2015-03-30',
                  direct_debit = true WHERE lastname = 'Maxis';""")


def downgrade():
    pass
