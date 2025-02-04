"""re #2: Add model for prices of energvalues.

Revision ID: 56e61da4fed1
Revises: 447579f29e92
Create Date: 2014-12-21 16:33:28.811658

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "56e61da4fed1"
down_revision = "447579f29e92"


def upgrade():
    op.create_table(
        "energyprice",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("price", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute("""INSERT into energyprice (year, price) VALUES (2014, 30);""")


def downgrade():
    op.drop_table("energyprice")
