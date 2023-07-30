# -* -coding: utf-8 -*-
from ..log import app_log, error_log, auth_log, log_with_user
from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.events import NewRequest
from pyramid.security import NO_PERMISSION_REQUIRED
import hashlib
import json
import mimetypes
import pkg_resources
import pyramid.config
import pyramid.events
import pyramid.httpexceptions
import pyramid.i18n
import pyramid.settings
import pyramid.threadlocal
import pyramid.view
import risclog.sqlalchemy.serializer
import signal
import sw.allotmentclub
import sw.allotmentclub.application
import sw.allotmentclub.browser
import sw.allotmentclub.browser.auth
import sw.allotmentclub.browser.base
import sw.allotmentclub.version
import time
import traceback
import zope.component
import sentry_sdk
from sentry_sdk.integrations.pyramid import PyramidIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration


def json_serializer(value, default, **kw):
    return json.dumps(value, default=default, **kw)


def check_csrf(request):
    token = request.session.get_csrf_token()
    csrf_token = request.POST.get('csrf_token')
    return token == str(csrf_token)


class WSGIWrapper(object):

    def __init__(self, app, **settings):
        self.app = app
        self.settings = settings

    def __call__(self, environ, start_response):
        def start_response_wrapper(status, headers, exc_info=None):
            self.mangle_headers(headers)
            return start_response(status, headers, exc_info)
        return self.app(environ, start_response_wrapper)


class DenyFrame(WSGIWrapper):

    def mangle_headers(self, headers):
        headers.append(('X-Frame-Options', 'SAMEORIGIN'))


class NoCache(WSGIWrapper):

    def mangle_headers(self, headers):
        headers.append(('cache-control', 'no-cache'))
        headers.append(('cache-control', 'no-store'))
        headers.append(('pragma', 'no-cache'))


class Portal(sw.allotmentclub.application.Application):
    """The portal application."""

    def __call__(self, global_config, **settings):
        super(Portal, self).__call__(**settings)
        app = self.make_wsgi_app(global_config)
        return app

    def configure(self):
        super(Portal, self).configure()
        self.configure_zca()

        mimetypes.add_type('application/font-woff', '.woff')
        mimetypes.add_type('application/x-font-ttf', '.ttf')

        registry = pyramid.registry.Registry(
            bases=(zope.component.getGlobalSiteManager(),))
        if self.settings.get('sentry.dsn', None):
            version = sw.allotmentclub.version.__version__
            sentry_sdk.init(
                release=f"sw-allotmentclub-backend@{version}",
                dsn=self.settings['sentry.dsn'],
                integrations=[PyramidIntegration(), SqlalchemyIntegration()])
        self.config = config = pyramid.config.Configurator(
            settings=self.settings,
            registry=registry)
        config.setup_registry(settings=self.settings)
        config.include('pyramid_beaker')
        config.include('pyramid_exclog')
        config.include('pyramid_tm')

        if self.testing:
            config.include('pyramid_mailer.testing')
        elif config.registry.settings.get('mail.enable') == 'false':
            config.include('sw.allotmentclub.printmailer')
        else:
            config.include('sw.allotmentclub.logmailer')

        # self.add_csrf_check()

        config.add_renderer(
            'json', risclog.sqlalchemy.serializer.json_renderer_factory(
                serializer=json_serializer))

        config.set_default_permission('view')
        config.set_authentication_policy(SessionAuthenticationPolicy())
        config.set_authorization_policy(ACLAuthorizationPolicy())
        config.set_root_factory(
            sw.allotmentclub.browser.auth.get_default_context)
        config.add_request_method(
            sw.allotmentclub.browser.auth.get_user, 'user', property=True)

        self.add_routes()
        config.scan(package=sw.allotmentclub.browser,
                    ignore=sw.allotmentclub.SCAN_IGNORE_TESTS)

    def configure_zca(self):
        pass

    def add_csrf_check(self):
        def check_request_for_csrf(event):
            request = event.request
            if request.POST and not check_csrf(request):
                # disable csrf check for login
                if request.path == '/login':
                    return
                raise sw.allotmentclub.browser.interfaces.CSRFForbidden()
        self.config.add_subscriber(check_request_for_csrf, NewRequest)

    def add_routes(self):
        config = self.config
        config.add_route('sentry_frontend', '/sentry_frontend')
        config.add_route('login', '/login')
        config.add_route('logout', '/logout')

        config.add_route('navigation', '/navigation')

        config.add_route('home', '/')
        config.add_route('map', '/map')
        config.add_route('infobrief_print', '/infobrief_print')
        config.add_route('calendar', '/calendar')
        config.add_route('calendar_event_add', '/calendar/add')
        config.add_route(
            'calendar_event_delete',
            '/calendar/{id}/delete',
            factory='..model.Event.context_factory'
        )
        config.add_route('map_download', '/map/download')
        config.add_route('parcel_list', '/parcels')
        config.add_route('parcel_map_upload', '/parcels/{id}/upload_map',
                         factory='..model.Parcel.context_factory')
        config.add_route('parcel_map_download_check',
                         '/parcels/{id}/check_download_map',
                         factory='..model.Parcel.context_factory')
        config.add_route('parcel_map_download', '/parcels/{id}/download_map',
                         factory='..model.Parcel.context_factory')

        config.add_route('depot', '/depot')

        config.add_route('mail_add', '/mail/add')
        config.add_route('mail_list_inbox', '/mail/inbox')
        config.add_route('mail_list_sent', '/mail/sent')
        config.add_route('mail_list_drafts', '/mail/drafts')
        config.add_route('mail_edit', '/mail/{id}/edit',
                         factory='..mail.Message.context_factory')
        config.add_route('mail_reply', '/mail/{id}/reply',
                         factory='..mail.Message.context_factory')
        config.add_route('mail_status', '/mail/{id}/status',
                         factory='..mail.Message.context_factory')
        config.add_route('mail_preview', '/mail/{id}/preview',
                         factory='..mail.Message.context_factory')
        config.add_route('mail_print', '/mail/{id}/download',
                         factory='..mail.Message.context_factory')
        config.add_route('mail_send', '/mail/{id}/send',
                         factory='..mail.Message.context_factory')
        config.add_route('mail_duplicate', '/mail/{id}/duplicate',
                         factory='..mail.Message.context_factory')
        config.add_route('mail_delete', '/mail/{id}/delete',
                         factory='..mail.Message.context_factory')
        config.add_route('mail_list_attachments', '/mail/{id}/attachments',
                         factory='..mail.Message.context_factory')
        config.add_route('mail_attachment_del', '/mail/attachment/{id}/del',
                         factory='..mail.Attachment.context_factory')
        config.add_route('mail_attachment_white_page',
                         '/mail/attachment/{id}/change_white_page',
                         factory='..mail.Attachment.context_factory')
        config.add_route('mail_attachment_download',
                         '/mail/attachment/{id}/download',
                         factory='..mail.Attachment.context_factory')
        config.add_route('mail_postmark_open_tracking_webhook',
                         '/mail/postmark_open_tracking_webhook')
        config.add_route('mail_postmark_inbound_webhook',
                         '/mail/postmark_inbound_webhook')

        config.add_route('member_assignments', '/members/assignment_attendees')
        config.add_route('member_assignments_bill',
                         '/members/assignment_attendees/bill')
        config.add_route('member_assignments_detail',
                         '/members/assignment_attendees/{id}/list',
                         factory='..model.Member.context_factory')
        config.add_route('member_add', '/members/add')
        config.add_route('member_edit',
                         '/members/{id}/edit',
                         factory='..model.Member.context_factory')
        config.add_route('member_attachment_add',
                         '/members/{id}/attachments/add',
                         factory='..model.Member.context_factory')
        config.add_route('member_attachment', '/members/{id}/attachments',
                         factory='..model.Member.context_factory')
        config.add_route(
            'member_attachment_download',
            '/members/{member_id}/attachments/{id}/download',
            factory='..model.MemberAttachment.context_factory')
        config.add_route(
            'member_attachment_delete',
            '/members/{member_id}/attachments/{id}/delete',
            factory='..model.MemberAttachment.context_factory')
        config.add_route('member_account_list', '/members/account_list')
        config.add_route('member_account_detail_list',
                         '/members/{id}/account_details',
                         factory='..model.Member.context_factory')
        config.add_route(
            'member_account_detail_switch_ir',
            '/members/{member_id}/account_details/{id}/switch',
            factory='.account.AccountDetailFactory')
        config.add_route('banking_account_list', '/accounts/list')
        config.add_route('banking_account_list_detail',
                         '/accounts/{id}/detail',
                         factory='..account.BookingKind.context_factory')
        config.add_route('banking_account_list_report', '/accounts/report.pdf')
        config.add_route('sepa_sammler_list', '/accounts/sepa_sammler')
        config.add_route('sepa_sammler_add', '/accounts/sepa_sammler/add')
        config.add_route(
            'sepa_ueberweisung_add',
            '/accounts/sepa_sammler/add_ueberweisung'
        )
        config.add_route('sepa_sammler_edit',
                         '/accounts/sepa_sammler/{id}/edit',
                         factory='..account.SEPASammler.context_factory')
        config.add_route('sepa_sammler_export',
                         '/accounts/sepa_sammler/{id}/export',
                         factory='..account.SEPASammler.context_factory')
        config.add_route('sepa_sammler_update',
                         '/accounts/sepa_sammler/{id}/update',
                         factory='..account.SEPASammler.context_factory')
        config.add_route('sepa_sammler_entry_list',
                         '/accounts/sepa_sammler/{id}/entries',
                         factory='..account.SEPASammler.context_factory')
        config.add_route('sepa_direct_debit', '/accounts/sepa_direct_debit')
        config.add_route('booking_list', '/accounts/{id}/list',
                         factory='..account.BankingAccount.context_factory')
        config.add_route('split_booking', '/booking/{id}/split',
                         factory='..account.Booking.context_factory')
        config.add_route('map_booking', '/booking/{id}/map',
                         factory='..account.Booking.context_factory')

        config.add_route('waste_water', '/waste_water')
        config.add_route('property_tax_b', '/property_tax_b')

        config.add_route('member_list', '/members')
        config.add_route('member_list_leased', '/members_leased')
        config.add_route('member_list_passive', '/members_passive')
        config.add_route('member_list_tap_water', '/members_tap_water')
        config.add_route('member_sale_history', '/members/sale_history')
        config.add_route('membership_fee', '/members/insert_membership_fee')
        config.add_route('member_sale',
                         '/members/{id}/sale',
                         factory='..model.Member.context_factory')
        config.add_route('direct_debit_letter',
                         '/members/{id}/direct_debit_letter',
                         factory='..model.Member.context_factory')
        config.add_route('become_member_letter',
                         '/members/{id}/become_member_letter',
                         factory='..model.Member.context_factory')
        config.add_route('mv_entrance_list', '/members/mv_entrance_list')

        config.add_route('energy_meter_export', '/electricity/export')
        config.add_route('energy_meter_import', '/electricity/import')
        config.add_route('calculate_energy_values',
                         '/electricity/calculate_energy_values')

        config.add_route('access_authority', '/access_authority')
        config.add_route('access_authority_detail',
                         '/access_authority/{id}/list',
                         factory='.authority.AuthorityContext.context_factory')
        config.add_route('access_authority_detail_add',
                         '/access_authority/{id}/list/add',
                         factory='.authority.AuthorityContext.context_factory')
        config.add_route(
            'access_authority_detail_edit',
            '/access_authority/{viewname}/list/{id}/edit',
            factory='..model.AccessAuthority.context_factory')
        config.add_route(
            'access_authority_detail_delete',
            '/access_authority/{viewname}/list/{id}/delete',
            factory='..model.AccessAuthority.context_factory')

        config.add_route('energy_price', '/energy_price')
        config.add_route('electricity_list', '/electricity')
        config.add_route('global_energy_value_list', '/electricity_billing')
        config.add_route('energy_value_list',
                         '/electricity/{id}/history',
                         factory='..electricity.ElectricMeter.context_factory')
        config.add_route('advance_pay_value_list',
                         '/electricity/{id}/advance_pay_history',
                         factory='..electricity.ElectricMeter.context_factory')

        config.add_route('externals', '/externals')
        config.add_route('external_add', '/externals/add')
        config.add_route('external_edit', '/externals/{id}/edit',
                         factory='..mail.ExternalRecipient.context_factory')
        config.add_route('external_delete', '/externals/{id}/delete',
                         factory='..mail.ExternalRecipient.context_factory')

        config.add_route('bulletins', '/bulletins')
        config.add_route('bulletin_add', '/bulletins/add')
        config.add_route('bulletin_edit', '/bulletins/{id}/edit',
                         factory='..bulletins.Bulletin.context_factory')
        config.add_route('bulletin_delete', '/bulletins/{id}/delete',
                         factory='..bulletins.Bulletin.context_factory')
        config.add_route('bulletin_print', '/bulletins/{id}/print',
                         factory='..bulletins.Bulletin.context_factory')

        config.add_route('keylists', '/keylists')
        config.add_route('keylist_add', '/keylists/add')
        config.add_route('keylist_edit', '/keylists/{id}/edit',
                         factory='..keylist.Keylist.context_factory')
        config.add_route('keylist_delete', '/keylists/{id}/delete',
                         factory='..keylist.Keylist.context_factory')
        config.add_route('keys', '/keylists/{id}/keys',
                         factory='..keylist.Keylist.context_factory')
        config.add_route('key_add', '/keylists/{id}/keys/add',
                         factory='..keylist.Keylist.context_factory')
        config.add_route(
            'key_edit',
            '/keylists/{keylist_id}/keys/{id}/edit',
            factory='..keylist.Key.context_factory')
        config.add_route(
            'key_delete',
            '/keylists/{keylist_id}/keys/{id}/delete',
            factory='..keylist.Key.context_factory')
        config.add_route('keylist_attachment_add',
                         '/keylists/{id}/attachments/add',
                         factory='..keylist.Keylist.context_factory')
        config.add_route('keylist_attachment', '/keylists/{id}/attachments',
                         factory='..keylist.Keylist.context_factory')
        config.add_route(
            'keylist_attachment_download',
            '/keylists/{keylist_id}/attachments/{id}/download',
            factory='..keylist.KeylistAttachment.context_factory')

        config.add_route('protocols', '/protocols')
        config.add_route('protocol_add', '/protocols/add')
        config.add_route('protocol_edit', '/protocols/{id}/edit',
                         factory='..protocol.Protocol.context_factory')
        config.add_route('protocol_delete', '/protocols/{id}/delete',
                         factory='..protocol.Protocol.context_factory')
        config.add_route('protocol_detail', '/protocols/{id}/details',
                         factory='..protocol.Protocol.context_factory')
        config.add_route('protocol_detail_add', '/protocols/{id}/details/add',
                         factory='..protocol.Protocol.context_factory')
        config.add_route(
            'protocol_detail_edit',
            '/protocols/{protocol_id}/details/{id}/edit',
            factory='..protocol.ProtocolDetail.context_factory')
        config.add_route(
            'protocol_detail_delete',
            '/protocols/{protocol_id}/details/{id}/delete',
            factory='..protocol.ProtocolDetail.context_factory')
        config.add_route('protocol_print', '/protocols/{id}/print',
                         factory='..protocol.Protocol.context_factory')
        config.add_route('protocol_attachment_add',
                         '/protocols/{id}/attachments/add',
                         factory='..protocol.Protocol.context_factory')
        config.add_route('protocol_attachment', '/protocols/{id}/attachments',
                         factory='..protocol.Protocol.context_factory')
        config.add_route(
            'protocol_attachment_download',
            '/protocols/{protocol_id}/attachments/{id}/download',
            factory='..protocol.ProtocolAttachment.context_factory')
        config.add_route(
            'protocol_attachment_delete',
            '/protocols/{protocol_id}/attachments/{id}/delete',
            factory='..protocol.ProtocolAttachment.context_factory')
        config.add_route('protocol_commitment', '/protocols/{id}/commitments',
                         factory='..protocol.Protocol.context_factory')
        config.add_route('protocol_commitment_add',
                         '/protocols/{id}/commitments/add',
                         factory='..protocol.Protocol.context_factory')
        config.add_route(
            'protocol_commitment_edit',
            '/protocols/{protocol_id}/commitments/{id}/edit',
            factory='..protocol.ProtocolCommitment.context_factory')
        config.add_route(
            'protocol_commitment_delete',
            '/protocols/{protocol_id}/commitments/{id}/delete',
            factory='..protocol.ProtocolCommitment.context_factory')

        config.add_route('assignments', '/assignments')
        config.add_route('assignment_add', '/assignments/add')
        config.add_route('assignment_edit', '/assignments/{id}/edit',
                         factory='..assignment.Assignment.context_factory')
        config.add_route('assignment_delete', '/assignments/{id}/delete',
                         factory='..assignment.Assignment.context_factory')
        config.add_route('assignment_list_attendees', '/assignments/{id}/list',
                         factory='..assignment.Assignment.context_factory')
        config.add_route('assignment_attendees_add',
                         '/assignments/{id}/attendees/add',
                         factory='..assignment.Assignment.context_factory')
        config.add_route(
            'assignment_attendees_edit',
            '/assignments/{assignment_id}/attendees/{id}/edit',
            factory='..assignment.AssignmentAttendee.context_factory')

        config.add_route(
            'assignment_attendees_delete',
            '/assignments/{assignment_id}/attendees/{id}/delete',
            factory='..assignment.AssignmentAttendee.context_factory')
        config.add_route('assignment_todos', '/assignment_todos')
        config.add_route('assignment_todo_add', '/assignment_todos/add')
        config.add_route('assignment_todo_edit', '/assignment_todos/{id}/edit',
                         factory='..assignment.AssignmentTodo.context_factory')
        config.add_route(
            'assignment_todo_delete',
            '/assignment_todos/{id}/delete',
            factory='..assignment.AssignmentTodo.context_factory')

        config.add_route('depots', '/depots')
        config.add_route('depot_add', '/depots/add')
        config.add_route('depot_edit', '/depots/{id}/edit',
                         factory='..depot.Depot.context_factory')
        config.add_route('depot_delete', '/depots/{id}/delete',
                         factory='..depot.Depot.context_factory')
        config.add_route('depot_download', '/depots/{id}/download',
                         factory='..depot.Depot.context_factory')

    @property
    def pipeline(self):
        return [
            (DenyFrame, 'factory', None, {}),
            (NoCache, 'factory', None, {}),
        ]

    def make_wsgi_app(self, global_config):
        app = self.config.make_wsgi_app()
        for spec, protocol, name, extra in self.pipeline:
            if protocol == 'factory':
                app = spec(app, **extra)
                continue
            entrypoint = pkg_resources.get_entry_info(spec, protocol, name)
            app = entrypoint.load()(app, global_config, **extra)
        return app


factory = Portal()


@pyramid.view.view_config(
    context=Exception,
    permission=NO_PERMISSION_REQUIRED,
    renderer='json')
class Error(sw.allotmentclub.browser.base.View):

    title = u'Interner Server-Fehler'
    status_code = 500

    def __init__(self, context, request):
        super(Error, self).__init__(context, request)
        self.time = time.time()

    @property
    def show_traceback(self):
        return self.request.registry.settings['testing']

    @property
    def exc_line(self):
        return traceback.format_exception_only(
            type(self.context), self.context)[0].strip()

    @property
    def error_ref(self):
        return (str(int(self.time))[-4:] +
                str(int(hashlib.sha1(
                    self.tb.encode('utf-8')).hexdigest(), 16))[:4])

    def update(self):
        self.tb = traceback.format_exc()
        self.error_summary = ('Ref: %s %s', self.error_ref, self.exc_line)
        self.request.response.status_code = self.status_code
        self.log()

    def log(self):
        error_log.error(*self.error_summary)
        for line in self.tb.splitlines():
            error_log.info(line, log_request=False)
        if self.show_traceback:
            print('Exception raised during test: {}'.format(self.tb))


@pyramid.view.view_config(
    route_name='sentry_frontend',
    permission=NO_PERMISSION_REQUIRED,
    renderer='json')
class SentryDataView(sw.allotmentclub.browser.base.View):

    def __call__(self):
        settings = pyramid.threadlocal.get_current_registry().settings
        return dict(dsn=settings.get('sentry.frontenddsn', ''))


@pyramid.view.view_config(
    context=pyramid.httpexceptions.HTTPException,
    permission=NO_PERMISSION_REQUIRED)
def HTTPException(context, request):
    return context


@pyramid.view.view_config(
    context=pyramid.httpexceptions.HTTPError,
    permission=NO_PERMISSION_REQUIRED,
    renderer='json')
class HTTPError(Error):

    @property
    def title(self):
        return '%s %s' % (self.status_code, type(self.context).__name__)

    @property
    def status_code(self):
        return self.context.status_code


@pyramid.view.notfound_view_config(renderer='json')
class NotFound(HTTPError):

    def log(self):
        if self.request.user and self.request.user.authenticated:
            log_with_user(
                auth_log.warning, self.request.user,
                'Ref: %s User %s tried to access non-existing url %s',
                self.error_ref, self.request.user.username, self.request.url)
        else:
            app_log.warning(
                'Ref: %s Unauthenticated user tried to access '
                'non-existing url %s' % (self.error_ref, self.request.url)
            )


@pyramid.events.subscriber(pyramid.events.ApplicationCreated)
def log_start(event):
    app_log.info('Application successfully started.')


shutdown_already_logged = False


def log_shutdown(signalnum, frame):
    global shutdown_already_logged
    if not shutdown_already_logged:
        shutdown_already_logged = True
        app_log.info('Application shutdown.')
    if signalnum == signal.SIGINT:
        # Make sure the port is closed, too:
        orig_sigint_handler(signalnum, frame)


signal.signal(signal.SIGTERM, log_shutdown)
orig_sigint_handler = signal.signal(signal.SIGINT, log_shutdown)
