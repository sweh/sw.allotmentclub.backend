"""Add email for users.

Revision ID: 4e4d0ae80e7a
Revises: 56b305a07721
Create Date: 2015-02-27 13:42:09.753241

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4e4d0ae80e7a"
down_revision = "56b305a07721"


def upgrade():
    op.add_column(
        "user", sa.Column("email", sa.String(length=50), nullable=True)
    )
    op.execute("""Update public.user SET email = 'sebastian.wehrmann@me.com'
                  WHERE username = 'sw'""")
    op.execute("""Update public.user SET email = 'ominette@gmx.de'
                  WHERE username = 'ar'""")
    op.execute("""Update public.user SET email = 'smjala@aim.com'
                  WHERE username = 'st'""")
    op.execute("""Update public.user SET email = 'gerd-wmi@t-online.de'
                  WHERE username = 'gm'""")


def downgrade():
    op.drop_column("user", "email")
