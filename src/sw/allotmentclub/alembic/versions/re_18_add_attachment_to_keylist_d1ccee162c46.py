"""re #18: Add attachment to keylist.

Revision ID: d1ccee162c46
Revises: a08b46e0172e
Create Date: 2016-07-25 13:30:03.833379

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d1ccee162c46"
down_revision = "a08b46e0172e"


def upgrade():
    op.create_table(
        "keylistattachment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("keylist_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=True),
        sa.Column("mimetype", sa.String(length=30), nullable=True),
        sa.Column("size", sa.String(length=20), nullable=True),
        sa.Column("data", sa.LargeBinary(length=10485760), nullable=True),
        sa.ForeignKeyConstraint(
            ["keylist_id"], ["keylist.id"], ondelete="cascade"
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("keylistattachment")
