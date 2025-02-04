"""Add accounting year to assignments.

Revision ID: 50035156da61
Revises: 39a3b6119fc6
Create Date: 2015-04-07 19:34:23.388874

"""

# revision identifiers, used by Alembic.
import sqlalchemy as sa
from alembic import op

revision = "50035156da61"
down_revision = "39a3b6119fc6"


def upgrade():
    op.add_column(
        "assignment", sa.Column("accounting_year", sa.Integer(), nullable=True)
    )
    op.execute("""UPDATE assignment SET accounting_year = 2015;""")


def downgrade():
    op.drop_column("assignment", "accounting_year")
