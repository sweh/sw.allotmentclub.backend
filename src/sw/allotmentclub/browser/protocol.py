# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from io import BytesIO
from pyramid.response import FileIter
from .base import date_time, get_selected_year, datetime_now, format_size
from .base import format_mimetype
from ..log import user_data_log, log_with_user
from pyramid.view import view_config
import datetime
from sw.allotmentclub import (
    Protocol, ProtocolDetail, ProtocolAttachment, ProtocolCommitment)
import collections
import dateutil.parser
import sw.allotmentclub.browser.base
import markdown


def int2roman(n):
    roman_numerals = []
    zahlen = {1000: "M",
              900: "CM",
              500: "D",
              400: "CD",
              100: "C",
              90: "XC",
              50: "L",
              40: "XL",
              10: "X",
              9: "IX",
              5: "V",
              4: "IV",
              1: "I"}

    if n > 0 and n < 4000 and type(n) == int:
        for zahl in sorted(zahlen.keys(), reverse=True):
            roman_numerals.append(n // zahl * zahlen[zahl])
            n = n % zahl

        return "".join(roman_numerals)


class Query(sw.allotmentclub.browser.base.Query):

    formatters = {
        'Datum': date_time
    }

    data_class = {
        'Datum': 'expand'
    }
    data_hide = {
        'Titel': 'phone,tablet',
        'Teilnehmer': 'phone,tablet',
        'Ort': 'phone,tablet',
    }

    def select(self):
        return (
            self.db.query(
                Protocol.id.label('#'),
                Protocol.day.label('Datum'),
                Protocol.title.label('Titel'),
                Protocol.attendees.label('Teilnehmer'),
                Protocol.location.label('Ort'))
            .select_from(Protocol)
            .filter(Protocol.accounting_year == get_selected_year()))


@view_config(route_name='protocols', renderer='json',
             permission='view')
class ProtocolListView(sw.allotmentclub.browser.base.TableView):
    """ Liste aller Protokolle."""

    query_class = Query
    default_order_by = 'day'
    year_selection = True
    start_year = 2014
    available_actions = [
        dict(url='protocol_add', btn_class='btn-success', icon='fa fa-plus',
             title='Neu'),
        dict(url='protocol_edit', btn_class='btn-success', icon='fa fa-pencil',
             title='Bearbeiten'),
        dict(url='protocol_delete', btn_class='btn-danger',
             icon='glyphicon glyphicon-trash', title='Löschen'),
        dict(url='protocol_detail', btn_class='btn-success', icon='fa fa-list',
             title='Details'),
        dict(url='protocol_attachment', btn_class='btn-success',
             icon='fa fa-list', title='Anlagen'),
        dict(url='protocol_commitment', btn_class='btn-success',
             icon='fa fa-list', title='Absprachen'),
        dict(url='protocol_print', btn_class='btn-success',
             icon='fa fa-print', title='Herunterladen')]


@view_config(route_name='protocol_edit', renderer='json',
             permission='view')
class ProtocolEditView(sw.allotmentclub.browser.base.EditJSFormView):

    title = 'Protokoll bearbeiten'

    @property
    def load_options(self):
        return {
            'day': {
                'label': 'Tag',
                'css_class': 'datetimepicker',
            },
            'title': {
                'label': 'Titel',
            },
            'attendees': {
                'label': 'Teilnehmer',
            },
            'location': {
                'label': 'Ort',
            },

        }

    @property
    def load_data(self):
        fields = [
            ('day', date_time(self.context.day)),
            ('title', self.context.title),
            ('attendees', self.context.attendees),
            ('location', self.context.location),
        ]
        return collections.OrderedDict(fields)

    def update(self):
        super(ProtocolEditView, self).update()
        if self.context.day:
            if isinstance(self.context.day, datetime.datetime):
                self.context.accounting_year = self.context.day.year
            else:
                self.context.accounting_year = (
                    dateutil.parser.parse(self.context.day).year)


@view_config(route_name='protocol_add', renderer='json',
             permission='view')
class ProtocolAddView(ProtocolEditView):

    title = 'Protokoll hinzufügen'

    def __init__(self, context, request):
        context = Protocol.create(
            day=datetime_now(),
            accounting_year=get_selected_year())
        context.commit()
        super(ProtocolAddView, self).__init__(context, request)
        log_with_user(user_data_log.info, self.request.user,
                      'Protokoll %s hinzugefügt.', self.context.id)

    @property
    def route_name(self):
        return 'protocol_edit'


@view_config(route_name='protocol_delete', renderer='json',
             permission='view')
class ProtocolDeleteView(sw.allotmentclub.browser.base.DeleteView):

    model = Protocol


def format_markdown(value, request=None):
    if not value:
        return
    return markdown.markdown(value)


class DetailQuery(sw.allotmentclub.browser.base.Query):

    formatters = {
        'TOP': format_markdown
    }
    data_class = {
        'Dauer': 'expand'
    }
    data_hide = {
        'TOP': 'phone,tablet',
        'Verantwortlich': 'phone',
    }

    def select(self):
        return (
            self.db.query(
                ProtocolDetail.id.label('#'),
                ProtocolDetail.duration.label('Dauer'),
                ProtocolDetail.message.label('TOP'),
                ProtocolDetail.responsible.label('Verantwortlich'))
            .select_from(ProtocolDetail)
            .filter_by(protocol=self.context))


@view_config(route_name='protocol_detail', renderer='json',
             permission='view')
class ProtocolDetailsView(sw.allotmentclub.browser.base.TableView):
    """ Liste aller Protokolle."""

    query_class = DetailQuery
    default_order_by = 'id'
    available_actions = [
        dict(url='protocol_detail_add', btn_class='btn-success',
             icon='fa fa-plus', title='Neu'),
        dict(url='protocol_detail_edit', btn_class='btn-success',
             icon='fa fa-pencil', title='Bearbeiten'),
        dict(url='protocol_detail_delete', btn_class='btn-danger',
             icon='glyphicon glyphicon-trash', title='Löschen')]


@view_config(route_name='protocol_detail_edit', renderer='json',
             permission='view')
class ProtocolDetailEditView(sw.allotmentclub.browser.base.EditJSFormView):

    title = 'Protokoll-Detail bearbeiten'

    @property
    def load_options(self):
        return {
            'duration': {
                'label': 'Dauer',
            },
            'message': {
                'label': 'TOP',
                'template': 'form_markdown',
            },
            'responsible': {
                'label': 'Verantwortlich',
            },
        }

    @property
    def load_data(self):
        fields = [
            ('duration', self.context.duration),
            ('message', self.context.message),
            ('responsible', self.context.responsible),
        ]
        return collections.OrderedDict(fields)

    def get_route(self, item, name):
        route = super(ProtocolDetailEditView, self).get_route(item, name)
        return route.replace('{protocol_id}', str(self.context.protocol.id))


@view_config(route_name='protocol_detail_add', renderer='json',
             permission='view')
class ProtocolDetailAddView(ProtocolDetailEditView):

    title = 'Protokoll-Detail hinzufügen'

    def __init__(self, context, request):
        context = ProtocolDetail.create(protocol=context)
        context.commit()
        super(ProtocolDetailAddView, self).__init__(context, request)
        log_with_user(user_data_log.info, self.request.user,
                      'ProtokollDetail %s hinzugefügt.', self.context.id)

    @property
    def route_name(self):
        return 'protocol_detail_edit'


@view_config(route_name='protocol_detail_delete', renderer='json',
             permission='view')
class ProtocolDetailDeleteView(sw.allotmentclub.browser.base.DeleteView):

    model = ProtocolDetail

    def log(self):
        if self.deleted is not None:
            deleted = self.context.id
            protocol = self.context.protocol.title
            log_with_user(user_data_log.info,
                          self.request.user,
                          'Protokoll-Detail %s aus Protokoll %s gelöscht.',
                          deleted, protocol)


class AttachmentQuery(sw.allotmentclub.browser.base.Query):

    formatters = {
        'Größe': format_size,
        'Dateityp': format_mimetype,
    }
    data_class = {
        'Name': 'expand'
    }
    data_hide = {
        'Dateityp': 'phone,tablet',
        'Größe': 'phone,tablet',
    }

    def select(self):
        return (
            self.db.query(
                ProtocolAttachment.id.label('#'),
                ProtocolAttachment.name.label('Name'),
                ProtocolAttachment.mimetype.label('Dateityp'),
                ProtocolAttachment.size.label('Größe'))
            .select_from(ProtocolAttachment)
            .filter_by(protocol=self.context))


@view_config(route_name='protocol_attachment', renderer='json',
             permission='view')
class ProtocolAttachmentsView(sw.allotmentclub.browser.base.TableView):
    """ Liste aller Anlagen."""

    query_class = AttachmentQuery
    default_order_by = 'Name'
    available_actions = [
        dict(url='protocol_attachment_add', btn_class='btn-success',
             icon='fa fa-plus', title='Neu'),
        dict(url='protocol_attachment_delete', btn_class='btn-danger',
             icon='glyphicon glyphicon-trash', title='Löschen'),
        dict(url='protocol_attachment_download', btn_class='btn-success',
             icon='fa fa-download', title='Herunterladen')]


@view_config(route_name='protocol_attachment_add', renderer='json',
             permission='view')
class ProtocolAttachmentAddView(sw.allotmentclub.browser.base.AddView):

    model = ProtocolAttachment

    def parse_file(self):
        file = self.request.params.get('file')
        data = file.file
        data.seek(0)
        data = data.read()
        name = 'Anlage %s' % int2roman(len(self.context.attachments) + 1)
        mimetype = file.type
        size = len(data)
        return name, mimetype, size, data

    def log(self, id):
        log_with_user(user_data_log.info,
                      self.request.user,
                      'hat Ablage %s %s.', id, self.action)

    def __call__(self):
        if not self.form_submit():
            return {'status': 'success', 'data': {}}
        name, mimetype, size, data = self.parse_file()
        attachment = self.model.create(
            name=name, mimetype=mimetype, size=size, data=data,
            protocol=self.context)
        attachment.commit()
        log_with_user(user_data_log.info,
                      self.request.user,
                      'hat Anlage %s zu Protokoll %s hinzugefügt.',
                      attachment.id, self.context.id)
        return {'status': 'success'}


@view_config(route_name='protocol_attachment_download',
             permission='view')
class ProtocolAttachmentDownloadView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        response = self.request.response
        response.set_cookie('fileDownload', value='true')
        response.content_type = self.context.mimetype
        response.content_length = int(self.context.size)
        response.content_disposition = (
            'attachment; filename="{}"'.format(self.context.name))
        response.app_iter = FileIter(BytesIO(self.context.data))
        return response


@view_config(route_name='protocol_attachment_delete', renderer='json',
             permission='view')
class ProtocolAttachmentDeleteView(sw.allotmentclub.browser.base.DeleteView):

    model = ProtocolAttachment

    def log(self):
        if self.deleted is not None:
            deleted = self.context.id
            protocol = self.context.protocol.title
            log_with_user(user_data_log.info,
                          self.request.user,
                          'Protokoll-Anlage %s aus Protokoll %s gelöscht.',
                          deleted, protocol)


class CommitmentQuery(sw.allotmentclub.browser.base.Query):

    data_class = {
        'Wer?': 'expand'
    }
    data_hide = {
        'Was?': 'phone,tablet',
        'Bis wann?': 'phone,tablet',
    }

    def select(self):
        return (
            self.db.query(
                ProtocolCommitment.id.label('#'),
                ProtocolCommitment.who.label('Wer?'),
                ProtocolCommitment.what.label('Was?'),
                ProtocolCommitment.when.label('Bis wann?'))
            .select_from(ProtocolCommitment)
            .filter_by(protocol=self.context))


@view_config(route_name='protocol_commitment', renderer='json',
             permission='view')
class ProtocolCommitmentsView(sw.allotmentclub.browser.base.TableView):
    """ Liste aller Protokolle."""

    query_class = CommitmentQuery
    default_order_by = 'id'
    available_actions = [
        dict(url='protocol_commitment_add', btn_class='btn-success',
             icon='fa fa-plus', title='Neu'),
        dict(url='protocol_commitment_edit', btn_class='btn-success',
             icon='fa fa-pencil', title='Bearbeiten'),
        dict(url='protocol_commitment_delete', btn_class='btn-danger',
             icon='glyphicon glyphicon-trash', title='Löschen')]


@view_config(route_name='protocol_commitment_edit', renderer='json',
             permission='view')
class ProtocolCommitmentEditView(sw.allotmentclub.browser.base.EditJSFormView):

    title = 'Protokoll-Absprache bearbeiten'

    @property
    def load_options(self):
        return {
            'who': {
                'label': 'Wer?',
            },
            'what': {
                'label': 'Was?',
            },
            'when': {
                'label': 'Bis wann?',
            },
        }

    @property
    def load_data(self):
        fields = [
            ('who', self.context.who),
            ('what', self.context.what),
            ('when', self.context.when),
        ]
        return collections.OrderedDict(fields)

    def get_route(self, item, name):
        route = super(ProtocolCommitmentEditView, self).get_route(item, name)
        return route.replace('{protocol_id}', str(self.context.protocol.id))


@view_config(route_name='protocol_commitment_add', renderer='json',
             permission='view')
class ProtocolCommitmentAddView(ProtocolCommitmentEditView):

    title = 'Protokoll-Absprache hinzufügen'

    def __init__(self, context, request):
        context = ProtocolCommitment.create(protocol=context)
        context.commit()
        super(ProtocolCommitmentAddView, self).__init__(context, request)
        log_with_user(
            user_data_log.info, self.request.user,
            'ProtokollAbsprache %s hinzugefügt.', self.context.id)

    @property
    def route_name(self):
        return 'protocol_commitment_edit'


@view_config(route_name='protocol_commitment_delete', renderer='json',
             permission='view')
class ProtocolCommitmentDeleteView(sw.allotmentclub.browser.base.DeleteView):

    model = ProtocolCommitment

    def log(self):
        if self.deleted is not None:
            deleted = self.context.id
            protocol = self.context.protocol.title
            log_with_user(user_data_log.info,
                          self.request.user,
                          'Protokoll-Absprache %s aus Protokoll %s gelöscht.',
                          deleted, protocol)
