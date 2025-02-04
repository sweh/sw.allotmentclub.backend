"""Add signature for st

Revision ID: 38a1521607b5
Revises: 2fd64f1e524c
Create Date: 2015-01-04 15:40:04.177104

"""

import base64

import pkg_resources
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "38a1521607b5"
down_revision = "2fd64f1e524c"


def upgrade():
    op.drop_column("user", "signature")
    op.add_column("user", sa.Column("signature", sa.String(), nullable=True))
    signature = pkg_resources.resource_stream(
        "sw.allotmentclub.signatures", "st.png"
    ).read()
    signature = "data:application/png;base64,{}".format(
        base64.b64encode(signature)
    )
    op.execute(
        """UPDATE public.user SET
                  signature = '{signature}'
                  WHERE username = 'st';""".format(signature=signature)
    )


def downgrade():
    op.drop_column("user", "signature")
    op.add_column(
        "user",
        sa.Column("signature", sa.LargeBinary(length=10485760), nullable=True),
    )
