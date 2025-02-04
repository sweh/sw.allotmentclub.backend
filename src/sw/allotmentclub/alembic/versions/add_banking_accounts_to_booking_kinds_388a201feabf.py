"""Add banking accounts to booking kinds.

Revision ID: 388a201feabf
Revises: 5fe4feac157
Create Date: 2015-04-01 13:17:35.841429

"""

# revision identifiers, used by Alembic.
import sqlalchemy as sa
from alembic import op

revision = "388a201feabf"
down_revision = "5fe4feac157"


def upgrade():
    op.add_column(
        "bookingkind",
        sa.Column("banking_account_id", sa.Integer(), nullable=True),
    )
    op.execute("UPDATE bookingkind SET banking_account_id = 2 WHERE id = 1;")
    op.execute("UPDATE bookingkind SET banking_account_id = 3 WHERE id = 2;")
    op.execute("UPDATE bookingkind SET banking_account_id = 4 WHERE id = 3;")
    op.execute("UPDATE bookingkind SET banking_account_id = 4 WHERE id = 4;")
    op.execute("UPDATE bookingkind SET banking_account_id = 4 WHERE id = 5;")


def downgrade():
    op.drop_column("bookingkind", "banking_account_id")
