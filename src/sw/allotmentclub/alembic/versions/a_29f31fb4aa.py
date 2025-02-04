"""Make haus_nr non unique.

Revision ID: 29f31fb4aa
Revises: 4d42c583ac73
Create Date: 2014-10-27 14:52:05.655804

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "29f31fb4aa"
down_revision = "4d42c583ac73"


def upgrade():
    op.drop_constraint("member_haus_nr_key", "member")


def downgrade():
    op.create_unique_constraint("member_haus_nr_key", "member", ["haus_nr"])
