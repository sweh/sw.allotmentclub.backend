"""Add signature for hs.

Revision ID: 96017ac786bf
Revises: 769e10087d9e
Create Date: 2017-07-28 13:21:10.263997

"""

import base64

import pkg_resources
from alembic import op

# revision identifiers, used by Alembic.
revision = "96017ac786bf"
down_revision = "769e10087d9e"


def upgrade():
    signature = pkg_resources.resource_stream(
        "sw.allotmentclub.signatures", "hs.png"
    ).read()
    signature = "data:application/png;base64,{}".format(
        base64.b64encode(signature).decode("utf-8")
    )
    op.execute(
        """UPDATE public.user SET
                  signature = '{signature}'
                  WHERE username = 'hs';""".format(signature=signature)
    )


def downgrade():
    op.execute("""UPDATE public.user SET
                  signature = ''
                  WHERE username = 'hs';""")
