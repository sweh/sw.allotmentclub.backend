"""Allow selecting multiple external recipients on messages.

Revision ID: ee1b8c9cb745
Revises: d6e0f091a932
Create Date: 2016-04-21 09:22:56.964404

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ee1b8c9cb745'
down_revision = 'd6e0f091a932'


def upgrade():
    op.create_table(
        'externals_messages',
        sa.Column('external_id', sa.Integer(), nullable=True),
        sa.Column('message_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['external_id'], ['externalrecipient.id'], ),
        sa.ForeignKeyConstraint(['message_id'], ['message.id'], )
    )
    op.execute(
        """INSERT into externals_messages (message_id, external_id)
             (SELECT id, external_id FROM message
                  WHERE external_id is not null);""")
    op.drop_constraint(
        'externalrecipient_message', 'message', type_='foreignkey')
    op.drop_column('message', 'external_id')


def downgrade():
    op.add_column(
        'message',
        sa.Column('external_id', sa.INTEGER(), autoincrement=False,
                  nullable=True))
    op.create_foreign_key(
        'externalrecipient_message', 'message', 'externalrecipient',
        ['external_id'], ['id'])
    op.execute("""UPDATE message SET external_id = (
                      SELECT external_id FROM externals_messages
                          WHERE message_id = message.id);""")
    op.drop_table('externals_messages')
