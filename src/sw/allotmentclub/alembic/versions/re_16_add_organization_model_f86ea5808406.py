"""re #16: Add organization model.

Revision ID: f86ea5808406
Revises: 1dfd521b7ca0
Create Date: 2016-07-26 13:19:46.031735

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f86ea5808406'
down_revision = '1dfd521b7ca0'

TABLES = ('abwasser', 'accessauthority', 'allotment', 'assignment',
          'assignmentattendee', 'attachment', 'bankingaccount', 'booking',
          'bookingkind', 'bulletin', 'depot', 'electricmeter', 'energyprice',
          'energyvalue', 'externalrecipient', 'grundsteuerb', 'key', 'keylist',
          'keylistattachment', 'log', 'member', 'message', 'parcel',
          'protocol', 'protocolattachment', 'protocolcommitment',
          'protocoldetail', 'salehistory', 'sepasammler', 'sepasammlerentry',
          'user')


def upgrade():
    op.create_table(
        'organization',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.execute("""INSERT into organization (id, title)
                  VALUES (1, 'Leuna-Bungalowgemeinschaft Roter See')""")
    for table in TABLES:
        op.add_column(
            table,
            sa.Column('organization_id', sa.Integer(), nullable=True))
        upd_table = table
        if upd_table == 'user':
            upd_table = 'public.user'
        op.execute("UPDATE {} SET organization_id = 1".format(upd_table))
        op.alter_column(table, "organization_id", nullable=False)


def downgrade():
    for table in TABLES:
        op.drop_column(table, 'organization_id')
    op.drop_table('organization')
