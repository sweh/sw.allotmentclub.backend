"""Increase size of mimetype field for mail attachments.

Revision ID: 46adf5114de1
Revises: 96017ac786bf
Create Date: 2017-08-17 10:57:45.173199

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '46adf5114de1'
down_revision = '96017ac786bf'


def upgrade():
    op.alter_column('attachment', 'mimetype', type_=sa.VARCHAR(100))


def downgrade():
    op.alter_column('attachment', 'mimetype', type_=sa.VARCHAR(30))
