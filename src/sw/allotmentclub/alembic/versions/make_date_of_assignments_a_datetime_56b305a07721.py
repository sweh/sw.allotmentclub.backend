"""Make date of assignments a datetime.

Revision ID: 56b305a07721
Revises: 4377c6148413
Create Date: 2015-02-26 13:51:22.336689

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '56b305a07721'
down_revision = '4377c6148413'


def upgrade():
    op.execute("""ALTER TABLE assignment ALTER COLUMN day TYPE
                  timestamp without time zone;""")
    op.execute("""UPDATE assignment SET day = day + interval '9 hours';""")


def downgrade():
    op.execute("""ALTER TABLE assignment ALTER COLUMN day TYPE date;""")
