"""Update hours of assignment attendees to support 2.5 hours.

Revision ID: 39a3b6119fc6
Revises: 4d63c477b58f
Create Date: 2015-04-07 12:38:11.475425

"""

# revision identifiers, used by Alembic.
from alembic import op
import sqlalchemy

revision = '39a3b6119fc6'
down_revision = '4d63c477b58f'


def upgrade():
    op.alter_column(
        table_name='assignmentattendee',
        column_name='hours',
        nullable=False,
        type_=sqlalchemy.types.Float(1)
    )


def downgrade():
    op.alter_column(
        table_name='assignmentattendee',
        column_name='hours',
        nullable=False,
        type_=sqlalchemy.types.Integer()
    )
