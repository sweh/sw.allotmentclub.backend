"""Add flag if member gets post.

Revision ID: 3f6271158ce3
Revises: dea40636fb3
Create Date: 2015-01-30 12:08:01.977482

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3f6271158ce3"
down_revision = "dea40636fb3"


def upgrade():
    op.add_column("member", sa.Column("get_post", sa.Boolean(), nullable=True))
    op.execute("""UPDATE member set get_post = true;""")
    op.execute("""UPDATE member set get_post = false WHERE id in (190);""")


def downgrade():
    op.drop_column("member", "get_post")
