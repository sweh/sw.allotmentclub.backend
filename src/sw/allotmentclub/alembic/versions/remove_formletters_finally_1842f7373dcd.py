"""Remove formletters (finally)

Revision ID: 1842f7373dcd
Revises: 0593bb8c05b6
Create Date: 2016-07-05 17:23:43.155107

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1842f7373dcd'
down_revision = '0593bb8c05b6'


def upgrade():
    op.drop_table('formletter')


def downgrade():
    op.create_table(
        'formletter',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('kind', postgresql.ENUM(
            u'Standard', u'Abrechnung Energie', u'Abschl\xe4ge Energie',
            u'Einladung Mitgliederversammlung', u'Info-Brief',
            u'Einzugserm\xe4chtigung', u'Fehlende Arbeitsstunden',
            name='form_letter_kind'), autoincrement=False, nullable=False),
        sa.Column('mimetype', sa.VARCHAR(length=30), autoincrement=False,
                  nullable=True),
        sa.Column('size', sa.VARCHAR(length=20), autoincrement=False,
                  nullable=True),
        sa.Column('data', postgresql.BYTEA(), autoincrement=False,
                  nullable=True),
        sa.Column('date', postgresql.TIMESTAMP(), autoincrement=False,
                  nullable=False),
        sa.Column('user_id', sa.INTEGER(), autoincrement=False,
                  nullable=False),
        sa.Column('status', postgresql.ENUM(
            u'Wartet', u'In Bearbeitung', u'Fehler', u'Fertig gestellt',
            name='form_letter_status'), autoincrement=False, nullable=False),
        sa.Column('with_address', sa.BOOLEAN(), autoincrement=False,
                  nullable=True),
        sa.Column('content', sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column('subject', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ['user_id'], [u'user.id'], name=u'formletter_user_id_fkey'),
        sa.PrimaryKeyConstraint('id', name=u'formletter_pkey')
    )
