# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from ..assignment import get_assignment_mail_data
from ..electricity import get_energyvalue_mail_data
from ..log import user_data_log, log_with_user
from .base import date_time, get_selected_year, route_url
from .letter import render_pdf, send_mail
from .protocol import format_markdown
from babel.dates import format_datetime
from PyPDF2 import PdfFileWriter, PdfFileReader
from bs4 import BeautifulSoup
from datetime import datetime
from io import BytesIO
from pyramid.response import Response, FileIter
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import view_config
from sqlalchemy import func, or_
from sw.allotmentclub import ExternalRecipient, SentMessageInfo
from sw.allotmentclub import Member, Message, Attachment, User
import base64
import collections
import dateutil.parser
import pybars
import pytz
import re
import sw.allotmentclub.browser.base


def append_pdf(input, output):
    [output.addPage(input.getPage(page_num)) for page_num in
        range(input.numPages)]


def get_recipient(value, request=None):
    recipients = Message.get(value).members + Message.get(value).externals
    if recipients:
        if (len(recipients)) > 1:
            return 'Mehrere Empfänger'
        recipient = recipients[0]
        if recipient.lastname == 'Verein':
            return 'Alle Mitglieder'
        return '{}, {}'.format(recipient.lastname, recipient.firstname)


def print_or_sent_date(value, request=None):
    message = Message.get(value)
    if message.sent:
        return date_time(message.sent)
    if message.printed:
        return date_time(message.printed)


def print_or_sent_type(value, request=None):
    message = Message.get(value)
    if message.sent and message.printed:
        return 'Brief und E-Mail'
    if message.sent:
        return 'E-Mail'
    if message.printed:
        return 'Brief'


class MailQuery(sw.allotmentclub.browser.base.Query):

    formatters = {
        'Gesendet': print_or_sent_date,
        'Via': print_or_sent_type,
        'Empfänger': get_recipient,
    }

    data_class = {
        'Betreff': 'expand'
    }
    data_hide = {
        'Gesendet': 'phone,tablet',
        'Via': 'phone,tablet',
        'Empfänger': 'phone,tablet',
        'Von': 'phone,tablet',
    }

    def select(self):
        return (
            self.db.query(
                Message.id.label('#'),
                Message.id.label('Empfänger'),
                Message.subject.label('Betreff'),
                User.username.label('Von'),
                Message.id.label('Gesendet'),
                Message.id.label('Via'))
            .select_from(Message)
            .join(User))


class InboxQuery(MailQuery):

    formatters = {
        'Empfangen': print_or_sent_date,
        'Absender': get_recipient,
    }
    data_class = {
        'Betreff': 'expand'
    }
    data_hide = {
    }

    def select(self):
        return (
            self.db.query(
                Message.id.label('#'),
                Message.subject.label('Betreff'),
                Message.id.label('Absender'),
                Message.id.label('Empfangen'))
            .select_from(Message)
            .join(User)
            .filter(Message.inbound.is_(True))
            .filter(Message.accounting_year == get_selected_year()))


class DraftsQuery(MailQuery):

    def select(self):
        query = super(DraftsQuery, self).select()
        return (
            query
            .filter(Message.inbound.is_(False))
            .filter(Message.sent.is_(None))
            .filter(Message.printed.is_(None)))


class SentQuery(MailQuery):

    def select(self):
        query = super(SentQuery, self).select()
        return (
            query
            .filter(Message.inbound.is_(False))
            .filter(or_(
                Message.sent.isnot(None),
                Message.printed.isnot(None)))
            .filter(Message.accounting_year == get_selected_year()))


@view_config(route_name='mail_list_drafts', renderer='json', permission='view')
class MailListDraftsView(sw.allotmentclub.browser.base.TableView):
    """ Liste aller Entwürfe."""

    query_class = DraftsQuery
    available_actions = [
        dict(url='mail_add', btn_class='btn-success', icon='fa fa-plus',
             title='Neu'),
        dict(url='mail_edit', btn_class='btn-success', icon='fa fa-pencil',
             title='Bearbeiten'),
        dict(url='mail_duplicate', btn_class='btn-success',
             icon='fa fa-copy', title='Duplizieren'),
        dict(url='mail_preview', btn_class='btn-success',
             icon='fa fa-print', title='Vorschau'),
        dict(url='mail_send', btn_class='btn-success',
             icon='fa fa-envelope', title='Versenden'),
        dict(url='mail_delete', btn_class='btn-danger',
             icon='glyphicon glyphicon-trash', title='Löschen')]


@view_config(route_name='mail_list_sent', renderer='json', permission='view')
class MailListSentView(sw.allotmentclub.browser.base.TableView):

    query_class = SentQuery
    default_order_by = 'sent'
    year_selection = True
    start_year = 2015
    available_actions = [
        dict(url='mail_status', btn_class='btn-success', icon='fa fa-truck',
             title='Zustell-Status'),
        dict(url='mail_edit', btn_class='btn-success', icon='fa fa-eye',
             title='Anzeigen'),
        dict(url='mail_preview', btn_class='btn-success',
             icon='fa fa-print', title='Vorschau'),
        dict(url='mail_send', btn_class='btn-success',
             icon='fa fa-envelope', title='Erneut Drucken'),
        dict(url='mail_duplicate', btn_class='btn-success',
             icon='fa fa-copy', title='Duplizieren')]


@view_config(route_name='mail_list_inbox', renderer='json', permission='view')
class MailListInboxView(sw.allotmentclub.browser.base.TableView):

    query_class = InboxQuery
    default_order_by = 'sent'
    year_selection = True
    start_year = 2017
    available_actions = [
        dict(url='mail_edit', btn_class='btn-success', icon='fa fa-eye',
             title='Anzeigen'),
        dict(url='mail_reply', btn_class='btn-success', icon='fa fa-reply',
             title='Antworten'),
        dict(url='mail_edit', btn_class='btn-success', icon='fa fa-pencil',
             title='Anzeigen')]


class MailStatusQuery(sw.allotmentclub.browser.base.Query):

    data_class = {
        'Empfänger': 'expand'
    }

    def select(self):
        return (
            self.db.query(
                SentMessageInfo.id.label('#'),
                SentMessageInfo.address.label('Empfänger'),
                func.coalesce(
                    SentMessageInfo.status, 'Versendet').label('Status'))
            .select_from(SentMessageInfo)
            .join(Message)
            .filter(SentMessageInfo.message == self.context))


@view_config(route_name='mail_status', renderer='json', permission='view')
class MailStatusView(sw.allotmentclub.browser.base.TableView):
    """Liste aller Empfänger-Status."""

    query_class = MailStatusQuery
    default_order_by = 'address'
    year_selection = False


@view_config(route_name='mail_preview', renderer='json', permission='view')
class MailPreviewView(sw.allotmentclub.browser.base.View):

    preview = True
    additional = {'Energieabrechnung': get_energyvalue_mail_data,
                  'Fehlende Arbeitsstunden': get_assignment_mail_data}

    def add_attachments(self, pdf, output):
        if self.context.attachments:
            for attachment in self.context.attachments:
                if attachment.mimetype in ('application/pdf',):
                    if attachment.white_page_before:
                        output.addBlankPage()
                    pdf = PdfFileReader(BytesIO(attachment.data), strict=False)
                    append_pdf(pdf, output)
        return pdf, output

    @property
    def recipients(self):
        recipients = self.context.members + self.context.externals
        organization_id = self.request.user.organization_id
        if not recipients:
            return [None]
        members = self.context.members
        if members and members[0].lastname == 'Verein':
            return (
                Member.query()
                .filter(Member.leaving_year.is_(None))
                .filter(Member.organization_id == organization_id)
                .filter(Member.get_post.is_(True)).all())
        return recipients

    def recipients_data(self, recipient):
        if recipient is None:
            return dict()
        return dict(deflection=recipient.deflection,
                    appellation=recipient.appellation,
                    title=recipient.title,
                    firstname=recipient.firstname,
                    lastname=recipient.lastname,
                    phone=recipient.phone,
                    mobile=recipient.mobile)

    def update(self):
        output = PdfFileWriter()
        if self.recipients == [None] or self.preview:
            recipients = self.recipients
        else:
            recipients = [r for r in self.recipients if r and not r.email]
        subject = self.context.subject or ''
        compiler = pybars.Compiler()
        compiled_body = compiler.compile(self.context.body)
        for recipient in recipients:
            address = recipient.address if recipient else None
            data = self.recipients_data(recipient)
            if subject in self.additional.keys():
                for nsubject, additional_data in self.additional[subject](
                        recipient, self.context.accounting_year):
                    additional_data.update(data)
                    body = format_markdown(compiled_body(additional_data))
                    output = self.add_page(address, nsubject, body, output)
            else:
                body = format_markdown(compiled_body(data))
                output = self.add_page(address, subject, body, output)
        result = BytesIO()
        output.write(result)
        result.seek(0)
        response = self.request.response
        response.set_cookie('fileDownload', value='true')
        response.content_type = 'application/pdf'
        response.content_disposition = 'attachment; filename=Brief.pdf'
        response.app_iter = FileIter(result)
        self.result = response

    def add_page(self, address, subject, body, output):
        sent = self.context.printed or self.context.sent
        pdf = render_pdf(address, subject, body, self.context.user,
                         date=sent, force_from=False)
        pdf = PdfFileReader(pdf, strict=False)
        append_pdf(pdf, output)
        pdf, output = self.add_attachments(pdf, output)
        numpages = pdf.numPages
        if numpages % 2 == 1:
            output.addBlankPage()
        return output


@view_config(route_name='mail_print', renderer='json', permission='view')
class MailPrintView(MailPreviewView):

    preview = False

    def update(self):
        if not self.context.printed:
            self.context.printed = datetime.now()
        return super(MailPrintView, self).update()


@view_config(route_name='mail_send', renderer='json', permission='view')
class MailSendView(MailPrintView):

    def update(self):
        if self.recipients == [None]:
            return
        recipients = []
        if not self.context.sent:
            recipients = [r for r in self.recipients if r.email]
            subject = self.context.subject or ''
            compiler = pybars.Compiler()
            compiled_body = compiler.compile(self.context.body)
            self_cc = True if len(recipients) == 1 else False
            for recipient in recipients:
                address = recipient.email
                data = self.recipients_data(recipient)
                if subject in self.additional.keys():
                    for nsubject, additional_data in self.additional[subject](
                            recipient, self.context.accounting_year):
                        additional_data.update(data)
                        body = format_markdown(compiled_body(additional_data))
                        msg_tag = send_mail(
                            address, nsubject, body, self.context.user,
                            attachments=self.context.attachments,
                            self_cc=self_cc)
                        SentMessageInfo.find_or_create(
                            message=self.context, tag=msg_tag, address=address)
                else:
                    body = format_markdown(compiled_body(data))
                    msg_tag = send_mail(
                        address, subject, body, self.context.user,
                        attachments=self.context.attachments,
                        self_cc=self_cc)
                    SentMessageInfo.find_or_create(
                        message=self.context, tag=msg_tag, address=address)
        sent = len(recipients)
        if sent:
            self.context.sent = datetime.now()
            self.result = {
                'status': 'success',
                'message': '%s E-Mail(s) erfolgreich versendet' % sent}
        else:
            self.result = {
                'status': 'success',
                'message': 'Keine E-Mail versendet'}
        print_recipients = [r for r in self.recipients if not r.email]
        if print_recipients:
            self.result['redirect'] = ('/api' + route_url(
                'mail_print', self.request).replace(
                    '{id}', str(self.context.id)))


@view_config(route_name='mail_duplicate', renderer='json', permission='view')
class MailDuplicateView(sw.allotmentclub.browser.base.View):

    def update(self):
        message = Message.create(
            accounting_year=datetime.now().year,
            members=self.context.members,
            externals=self.context.externals,
            subject=self.context.subject,
            body=self.context.body,
            user=self.request.user)
        for attachment in self.context.attachments:
            Attachment.create(
                message=message,
                filename=attachment.filename,
                mimetype=attachment.mimetype,
                size=attachment.size,
                data=attachment.data)
        self.result = {'status': 'success',
                       'message': 'Duplikat erstellt.'}


@view_config(route_name='mail_delete', renderer='json', permission='view')
class MailDeleteView(sw.allotmentclub.browser.base.View):

    def update(self):
        if (self.context.printed or self.context.sent):
            self.result = {
                'status': 'error',
                'message': ('Bereits gedruckte oder versendete Nachrichten '
                            'können nicht gelöscht werden.')}
            return
        self.context.delete()
        self.result = {'status': 'success', 'message': 'Nachricht gelöscht.'}


@view_config(route_name='mail_edit', renderer='json', permission='view')
class MailEditView(sw.allotmentclub.browser.base.EditJSFormView):

    title = 'Brief/E-Mail versenden'
    show_old_members = True

    def strip_html(self, body):
        if not body.startswith('<'):
            return body
        soup = BeautifulSoup(body, 'html.parser')
        texts = soup.findAll(text=True)

        def visible(element):
            if element.parent.name in ['style', 'script', '[document]',
                                       'head', 'title']:
                return False
            elif re.match('<!--.*-->', str(element)):
                return False
            return True

        result = filter(visible, texts)
        return '\n'.join(r.strip() for r in result)

    def quote_body(self, msg):
        body = self.strip_html(msg.body)
        body = '\n'.join('> {}'.format(l) for l in body.splitlines())
        recipient = (msg.members or msg.externals)[0]
        quote_header = 'Am {} schrieb {} {} <{}>:'.format(
            format_datetime(
                msg.sent, "EEEE, 'den' d. MMM Y H:m 'Uhr'", locale='de_DE'),
            recipient.firstname,
            recipient.lastname,
            recipient.email)
        return '\n\n{}\n{}'.format(quote_header, body)

    @property
    def disabled(self):
        if self.context.sent or self.context.printed:
            return True
        return False

    @property
    def load_options(self):
        collection_url = '/api/' + route_url(
            'mail_list_attachments',
            self.request).replace('{id}', str(self.context.id))
        disabled = self.disabled
        return {
            'member_ids': {
                'source': self.member_source,
                'label': 'Empfänger',
                'css_class': 'chosen',
                'disabled': disabled,
                'multiple': True,
            },
            'external_ids': {
                'source': self.external_source,
                'label': 'Externe Empfänger',
                'css_class': 'chosen',
                'disabled': disabled,
                'multiple': True,
            },
            'subject': {
                'label': 'Betreff',
                'disabled': disabled
            },
            'body': {
                'label': 'Nachricht',
                'template': 'form_markdown',
                'disabled': disabled
            },
            'attachments': {
                'label': 'Anhänge',
                'template': 'form_upload',
                'documents_collection_url': collection_url,
                'disabled': disabled
            }
        }

    def resource_data_item_title(self, item):
        meta = ('({}, {} Uhr)'.format(item.user.username, date_time(item.date))
                if item.user else '')
        return '{} {} {}'.format(
            item.filename,
            meta,
            '(Weiße Seite davor)' if item.white_page_before else '')

    @property
    def members(self):
        return super(MailEditView, self).members.filter(
            ~Member.lastname.in_(('Verein', 'Werkstatt')))

    @property
    def member_source(self):
        result = super(MailEditView, self).member_source
        verein = Member.query().filter(Member.lastname == 'Verein').one()
        result.insert(0, {u'title': u'Alle Mitglieder', u'token': verein.id})
        return result

    @property
    def external_source(self):
        return [
            {
                'token': external.id,
                'title': '{}, {}'.format(
                    external.lastname,
                    external.firstname)
            }
            for external in (
                ExternalRecipient.query()
                .filter(ExternalRecipient.city != '')
                .order_by(ExternalRecipient.lastname))]

    @property
    def body(self):
        if self.disabled:
            return self.strip_html(self.context.body)
        if self.context.body:
            return self.context.body
        return ('Sehr geehrte{{deflection}} {{appellation}} '
                '{{title}} {{lastname}},')

    @property
    def load_data(self):
        fields = [
            ('member_ids', self.context.member_ids),
            ('external_ids', self.context.external_ids),
            ('subject', self.context.subject),
            ('body', self.body),
            ('attachments', [{'id': a.id, 'title': a.filename}
                             for a in self.context.attachments])]
        return collections.OrderedDict(fields)

    def handle_upload(self, file_):
        data = file_.file
        data.seek(0)
        data = data.read()
        return Attachment.create(
            message=self.context,
            filename=file_.filename,
            mimetype=file_.type,
            size=len(data),
            data=data), 'mail_attachment_del'


@view_config(route_name='mail_add', renderer='json', permission='view')
class MailAddView(MailEditView):

    def __init__(self, context, request):
        context = Message.create(
            user=request.user,
            accounting_year=datetime.now().year)
        context.commit()
        super(MailAddView, self).__init__(context, request)
        log_with_user(user_data_log.info, self.request.user,
                      'Nachricht %s hinzugefügt.', self.context.id)

    @property
    def route_name(self):
        return 'mail_edit'


@view_config(route_name='mail_reply', renderer='json', permission='view')
class MailReplyView(MailEditView):

    def __init__(self, context, request):
        msg = Message.create(
            user=request.user,
            in_reply_to=context,
            accounting_year=datetime.now().year)
        msg.members.extend(context.members)
        msg.externals.extend(context.externals)
        msg.body = self.quote_body(context)
        msg.subject = 'Re: {}'.format(context.subject)
        msg.commit()
        super(MailReplyView, self).__init__(msg, request)
        log_with_user(user_data_log.info, self.request.user,
                      'Nachricht %s hinzugefügt.', self.context.id)

    @property
    def route_name(self):
        return 'mail_edit'


@view_config(route_name='mail_list_attachments', renderer='json',
             permission='view')
class MailListAttachments(MailEditView):

    def update(self):
        self.result = [
            self.resource_data_item(attachment, 'mail_attachment_del')
            for attachment in self.context.attachments]


@view_config(route_name='mail_attachment_white_page', renderer='json',
             permission='view')
class AttachmentWhitePageView(MailEditView):

    def update(self):
        self.context.white_page_before = not self.context.white_page_before
        self.result = {'title': self.resource_data_item_title(self.context)}


@view_config(route_name='mail_attachment_del', renderer='json',
             permission='view')
class AttachmentDelView(sw.allotmentclub.browser.base.DeleteView):

    model = Attachment


@view_config(route_name='mail_attachment_download', renderer='json',
             permission='view')
class AttachmentDownloadView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        response = self.request.response
        response.set_cookie('fileDownload', value='true')
        response.content_type = self.context.mimetype
        response.content_length = int(self.context.size)
        response.content_disposition = (
            'attachment; filename="{}"'.format(self.context.filename))
        response.app_iter = FileIter(BytesIO(self.context.data))
        return response


@view_config(route_name='mail_postmark_open_tracking_webhook',
             permission=NO_PERMISSION_REQUIRED)
class PostmarkOpenTrackingWebhookView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def opened(self, info, data):
        received_date = dateutil.parser.parse(data['ReceivedAt'])
        native = pytz.timezone('Etc/GMT+5')
        local = pytz.timezone('Europe/Berlin')
        received = date_time(
            received_date.replace(tzinfo=native).astimezone(local))
        info.status = (
            'Geöffnet am {} Uhr in {} (IP: {}) für {} Sekunden.'.format(
                received, data['Geo'].get('City', 'Unbekannt'),
                data['Geo'].get('IP', 'Unbekannt'),
                data.get('ReadSeconds', 'Unbekannt')))

    def bounced(self, info, data):
        local = pytz.timezone('Europe/Berlin')
        bounce_date = date_time(
            dateutil.parser.parse(data['BouncedAt']).astimezone(local))
        info.status = '{} am {} Uhr: {}'.format(data['Name'], bounce_date,
                                                data['Description'])

    def delivered(self, info, data):
        local = pytz.timezone('Europe/Berlin')
        delivery_date = date_time(
            dateutil.parser.parse(data['DeliveredAt']).astimezone(local))
        info.status = 'Zugestellt am {} Uhr.'.format(delivery_date)

    def __call__(self):
        data = self.request.json
        recipient = data.get('Recipient', data.get('Email'))
        if not recipient:
            raise ValueError("No recipient found: %r" % data)
        data['Tag'] = data['Tag'].replace(' ', '')
        info = (SentMessageInfo
                .query()
                .filter(SentMessageInfo.tag == data['Tag'])
                .filter(SentMessageInfo.address == recipient)
                .one_or_none())
        if not info:
            info = (SentMessageInfo
                    .query()
                    .filter(SentMessageInfo.tag == data['Tag'])
                    .first())
            if info is None:
                return Response('ok')
            info = SentMessageInfo.create(
                organization_id=info.organization_id,
                message=info.message, tag=info.tag, address=recipient)
        if 'ReceivedAt' in data:
            self.opened(info, data)
        elif 'BouncedAt' in data:
            self.bounced(info, data)
        elif 'DeliveredAt' in data:
            self.delivered(info, data)
        else:
            raise RuntimeError(
                "Could not identify given data: %r " % data)
        return Response('ok')


@view_config(route_name='mail_postmark_inbound_webhook',
             permission=NO_PERMISSION_REQUIRED)
class PostmarkInboundWebhookView(object):

    organization_id = 1  # New messages are added on Verwaltung Roter See

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def sent_date(self, data):
        local = pytz.timezone('Europe/Berlin')
        return dateutil.parser.parse(data['Date'][:31]).astimezone(local)

    def __call__(self):
        data = self.request.json
        sender = data['FromFull']['Email'].lower()
        if sender == 'vorstand@roter-see.de':
            return Response('ok')
        message = Message.create(
            inbound=True,
            organization_id=self.organization_id,
            user=User.by_username('system'))
        member = Member.query().filter(Member.email == sender).first()
        if member:
            message.members.append(member)
            message.organization_id = member.organization_id
        else:
            external = (ExternalRecipient.query()
                        .filter(ExternalRecipient.email == sender)
                        .first())
            if not external:
                external = ExternalRecipient.create(email=sender)
                external.lastname = data['FromFull']['Name']
                external.organization_id = self.organization_id
            message.externals.append(external)
            message.organization_id = external.organization_id
        message.subject = data['Subject']
        message.body = (
            data['HtmlBody'] if data['HtmlBody'] else data['TextBody'])
        message.sent = self.sent_date(data)
        message.accounting_year = message.sent.year
        for attachment in data['Attachments']:
            Attachment.create(
                message=message,
                organization_id=message.organization_id,
                filename=attachment["Name"],
                mimetype=attachment["ContentType"],
                size=attachment["ContentLength"],
                data=base64.b64decode(attachment["Content"]))
        return Response('ok')
