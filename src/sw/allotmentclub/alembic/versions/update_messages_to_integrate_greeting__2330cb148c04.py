"""Update messages to integrate greeting into text.

Revision ID: 2330cb148c04
Revises: ee1b8c9cb745
Create Date: 2016-04-25 10:34:10.696062

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '2330cb148c04'
down_revision = 'ee1b8c9cb745'


def upgrade():
    op.execute(
        """UPDATE message
           SET body = 'Sehr geehrte{{deflection}} {{appellation}}
           {{title}} {{lastname}},\n\n' || body;""")


def downgrade():
    pass
