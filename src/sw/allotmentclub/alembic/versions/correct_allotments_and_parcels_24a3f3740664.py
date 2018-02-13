"""Correct allotments and parcels.

Revision ID: 24a3f3740664
Revises: 186285f37c74
Create Date: 2015-03-05 10:34:51.011115

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '24a3f3740664'
down_revision = '186285f37c74'


def upgrade():
    op.execute("UPDATE parcel SET number = 103 WHERE id = 119;")
    op.execute("INSERT into parcel (number, allotment_id) VALUES (131, 185);")
    op.execute("UPDATE parcel SET number = 135 WHERE id = 159;")
    op.execute("UPDATE parcel SET number = 136 WHERE id = 179;")
    op.execute("UPDATE parcel SET number = 123 WHERE id = 197;")
    op.execute("UPDATE parcel SET number = 122 WHERE id = 177;")


def downgrade():
    pass
