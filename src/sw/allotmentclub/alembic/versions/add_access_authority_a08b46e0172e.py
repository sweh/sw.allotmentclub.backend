"""Add access authority

Revision ID: a08b46e0172e
Revises: 4b98c95b9a56
Create Date: 2016-07-11 15:35:47.894579

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a08b46e0172e'
down_revision = '4b98c95b9a56'

LEVELS = {
    'portal-revision': (5, 4, 2),
    'portal-club-admin': (2,),
    'portal-read-only': (4, 2),
    'portal-admin': (),
}

AUTHORITIES = (
    ('booking_list', 'portal-revision'),
    ('split_booking', 'portal-club-admin'),
    ('map_booking', 'portal-club-admin'),
    ('member_account_list', 'portal-revision'),
    ('member_account_detail_list', 'portal-revision'),
    ('member_account_detail_switch_ir', 'portal-club-admin'),
    ('banking_account_list', 'portal-revision'),
    ('sepa_sammler_list', 'portal-club-admin'),
    ('sepa_sammler_update', 'portal-read-only'),
    ('sepa_sammler_edit', 'portal-read-only'),
    ('sepa_sammler_add', 'portal-read-only'),
    ('sepa_sammler_export', 'portal-read-only'),
    ('sepa_sammler_entry_list', 'portal-club-admin'),
    ('sepa_direct_debit', 'portal-club-admin'),
    ('assignments', 'portal-read-only'),
    ('assignment_edit', 'portal-read-only'),
    ('assignment_add', 'portal-read-only'),
    ('assignment_delete', 'portal-admin'),
    ('assignment_list_attendees', 'portal-read-only'),
    ('assignment_attendees_edit', 'portal-read-only'),
    ('assignment_attendees_add', 'portal-read-only'),
    ('assignment_attendees_delete', 'portal-read-only'),
    ('member_assignments', 'portal-read-only'),
    ('member_assignments_bill', 'portal-admin'),
    ('access_authority', 'portal-admin'),
    ('access_authority_detail', 'portal-admin'),
    ('access_authority_detail_edit', 'portal-admin'),
    ('access_authority_detail_add', 'portal-admin'),
    ('access_authority_detail_delete', 'portal-admin'),
    ('bulletins', 'portal-read-only'),
    ('bulletin_edit', 'portal-read-only'),
    ('bulletin_add', 'portal-read-only'),
    ('bulletin_delete', 'portal-admin'),
    ('bulletin_print', 'portal-read-only'),
    ('depots', 'portal-read-only'),
    ('depot_add', 'portal-read-only'),
    ('depot_edit', 'portal-club-admin'),
    ('depot_delete', 'portal-admin'),
    ('depot_download', 'portal-read-only'),
    ('electricity_list', 'portal-revision'),
    ('global_energy_value_list', 'portal-revision'),
    ('energy_value_list', 'portal-revision'),
    ('advance_pay_value_list', 'portal-read-only'),
    ('energy_meter_export', 'portal-read-only'),
    ('energy_meter_import', 'portal-admin'),
    ('externals', 'portal-read-only'),
    ('external_edit', 'portal-read-only'),
    ('external_add', 'portal-read-only'),
    ('home', 'portal-read-only'),
    ('keylists', 'portal-read-only'),
    ('keylist_edit', 'portal-read-only'),
    ('keylist_add', 'portal-read-only'),
    ('keylist_delete', 'portal-admin'),
    ('keys', 'portal-read-only'),
    ('key_edit', 'portal-read-only'),
    ('key_add', 'portal-read-only'),
    ('key_delete', 'portal-admin'),
    ('mail_list', 'portal-read-only'),
    ('mail_preview', 'portal-read-only'),
    ('mail_print', 'portal-read-only'),
    ('mail_send', 'portal-read-only'),
    ('mail_duplicate', 'portal-read-only'),
    ('mail_delete', 'portal-read-only'),
    ('mail_edit', 'portal-read-only'),
    ('mail_add', 'portal-read-only'),
    ('mail_list_attachments', 'portal-read-only'),
    ('mail_attachment_white_page', 'portal-read-only'),
    ('mail_attachment_del', 'portal-read-only'),
    ('mail_attachment_download', 'portal-read-only'),
    ('map', 'portal-read-only'),
    ('map_download', 'portal-read-only'),
    ('member_list', 'portal-read-only'),
    ('member_edit', 'portal-club-admin'),
    ('member_address_verify', 'portal-admin'),
    ('direct_debit_letter', 'portal-read-only'),
    ('become_member_letter', 'portal-read-only'),
    ('member_sale', 'portal-admin'),
    ('mv_entrance_list', 'portal-read-only'),
    ('member_sale_history', 'portal-read-only'),
    ('protocols', 'portal-read-only'),
    ('protocol_edit', 'portal-admin'),
    ('protocol_add', 'portal-admin'),
    ('protocol_delete', 'portal-admin'),
    ('protocol_detail', 'portal-read-only'),
    ('protocol_detail_edit', 'portal-admin'),
    ('protocol_detail_add', 'portal-admin'),
    ('protocol_detail_delete', 'portal-admin'),
    ('protocol_attachment', 'portal-read-only'),
    ('protocol_attachment_add', 'portal-admin'),
    ('protocol_attachment_download', 'portal-read-only'),
    ('protocol_commitment', 'portal-read-only'),
    ('protocol_commitment_edit', 'portal-admin'),
    ('protocol_commitment_add', 'portal-admin'),
    ('protocol_commitment_delete', 'portal-admin'),
    ('protocol_print', 'portal-read-only'),
)


def upgrade():
    op.create_table(
        'accessauthority',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('viewname', sa.String(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], [u'user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    for viewname, group in AUTHORITIES:
        for user_id in LEVELS[group]:
            op.execute("""INSERT INTO accessauthority (viewname, user_id)
                          VALUES ('{}', {});""".format(viewname, user_id))


def downgrade():
    op.drop_table('accessauthority')
