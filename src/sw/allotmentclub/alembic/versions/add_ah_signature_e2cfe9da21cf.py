"""Add ah signature

Revision ID: e2cfe9da21cf
Revises: 897a3181401e
Create Date: 2020-10-15 07:20:57.570537

"""

import base64

import pkg_resources
from alembic import op

# revision identifiers, used by Alembic.
revision = "e2cfe9da21cf"
down_revision = "897a3181401e"


def upgrade():
    signature = base64.b64encode(
        pkg_resources.resource_stream(
            "sw.allotmentclub.signatures", "ah.png"
        ).read()
    ).decode()
    signature = f"data:application/png;base64,{signature}"
    op.execute(f"""UPDATE public.user SET
                  signature = '{signature}'
                  WHERE username = 'ah';""")


def downgrade():
    op.execute("""UPDATE public.user SET
                  signature = ''
                  WHERE username = 'ah';""")
