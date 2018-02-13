"""Add signature for ar

Revision ID: 5b929a47d6ae
Revises: 4841df08d22b
Create Date: 2016-04-18 10:28:47.331715

"""

from alembic import op
import base64
import pkg_resources

# revision identifiers, used by Alembic.
revision = '5b929a47d6ae'
down_revision = '4841df08d22b'


def upgrade():
    signature = pkg_resources.resource_stream(
        'sw.allotmentclub.signatures', 'ar.png').read()
    signature = 'data:application/png;base64,{}'.format(
        base64.b64encode(signature))
    op.execute(u"""UPDATE public.user SET
                  signature = '{signature}'
                  WHERE username = 'ar';""".format(signature=signature))


def downgrade():
    op.execute(u"""UPDATE public.user SET
                  signature = ''
                  WHERE username = 'ar';""")
