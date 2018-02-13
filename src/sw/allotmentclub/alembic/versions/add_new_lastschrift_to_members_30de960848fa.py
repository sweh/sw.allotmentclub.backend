# encoding=utf8
"""Add new lastschrift to members.

Revision ID: 30de960848fa
Revises: bbb62bf367a
Create Date: 2015-11-06 13:54:34.537556

"""

# revision identifiers, used by Alembic.
from __future__ import unicode_literals
from alembic import op

revision = '30de960848fa'
down_revision = u'bbb62bf367a'


def upgrade():
    op.execute("""UPDATE member SET mobile = '0152 28976145',
                                    phone = '034927 21997',
                                    direct_debit = true,
                                    city = 'Kemberg / OT Globig',
                                    bic = 'NOLADE21WBL',
                                    iban = 'DE46805501014623047542',
                                    direct_debit_date = '2015-10-22'
                                    WHERE id = 197;
                """)
    op.execute("""UPDATE member SET firstname = 'André',
                                    direct_debit = true,
                                    bic = 'DRESDEFF88',
                                    iban = 'DE57800800000812092400',
                                    direct_debit_date = '2015-10-27'
                                    WHERE id = 118;
                """)
    op.execute("""UPDATE electricmeter SET allotment_id = 159 WHERE id = 67;
                """)


def downgrade():
    pass
